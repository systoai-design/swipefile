#!/usr/bin/env python3
"""
Rewrite pass for the mirror — turns crawled HTML into a servable local site.

Reads _raw/*.html plus crawl-manifest.json, mirrors every asset the pages
reference (following text assets to a fixed point), then rewrites each page so
that:
  - assets point at the shared local cdn/ directory
  - links to pages we mirrored point at their local slug (navigation works)
  - links to anything we did not mirror go inert (#inert, never bare #)
  - forms go inert
  - integrity/crossorigin are stripped, because rewriting a file's bytes voids
    its SRI hash and the browser then drops the whole resource silently

Every rule here was paid for by a measured failure; see library/INDEX.md
"Cross-site patterns observed" for the evidence behind each.

Run after crawl.py:  python3 build.py
Then serve with:     python3 serve.py --directory site
"""
import argparse, hashlib, json, os, re, glob
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/150.0 Safari/537.36")

# A CDN answering `vary: Accept` hands a bare fetch different bytes than it
# hands the browser — framerusercontent serves AVIF to Chrome and PNG to
# `Accept: */*`, so a mirror fetched without this is a different image set.
ACCEPT = 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'

# Truncate a captured URL at its first valid extension. Stripping trailing
# punctuation is necessary but not sufficient: a url() inside a CSS custom
# property in an inline <style> is followed by `);--next-prop:…`, and `;`/`:`
# are not stop characters, so the match runs into the next declaration.
ASSET_EXT = (r'woff2?|ttf|otf|eot|png|jpe?g|gif|webp|avif|svg|ico|bmp|'
             r'mp4|webm|mov|m4v|ogg|mp3|wav|'
             r'css|js|mjs|json|framercms|txt|xml|wasm|map|'
             r'glb|gltf|hdr|exr|ktx2|basis|bin')
URL_ANY = re.compile(r'https?://[^\s"\'<>\\`]+', re.I)
EXT_AT = re.compile(rf'\.(?:{ASSET_EXT})(?=[?#]|$|[^A-Za-z0-9])', re.I)
QUERY_STOP = re.compile(r'[\s"\'<>\\`)]')

# Text assets get re-scanned for the URLs they build at runtime.
TEXT_EXT = re.compile(r'\.(?:css|js|mjs|json|framercms|map|txt|xml)$', re.I)
# Relative specifiers, captured with their delimiters so the same patterns can
# both harvest (group 3) and rewrite. Bundler chunks reference each other as
# import('./X.mjs'), which a host-based scan cannot see.
REL_SPEC = re.compile(r"""((?:import\s*\(|from\s+|new\s+URL\s*\()\s*)(['"`])([^'"`]+)(\2)""")
CSS_URL = re.compile(r"""(url\(\s*)(['"]?)([^'")]+)(\2)""")
ATTR_URL = re.compile(r"""((?:src|href|poster|data-src)\s*=\s*)(["'])([^"']+)(\2)""", re.I)
# srcset is a LIST of "url descriptor" candidates, comma-separated — not a single
# URL like the other attributes above, so it needs its own rewrite pass. Missing
# this rewrites the fallback <img src> only; every <source srcset> a <picture>
# actually selects keeps pointing at the origin. A <picture> does NOT fall back
# to <img> when its chosen <source> 404s — only when no <source> matches at all —
# so the visible symptom is not a broken-image icon, it is a blank box exactly
# where a real photo belongs, on img/source pairs everywhere responsive art
# direction is used.
SRCSET_ATTR = re.compile(r'\bsrcset\s*=\s*(["\'])([^"\']+)\1', re.I)
REL_PATTERNS = (REL_SPEC, CSS_URL, ATTR_URL)
SKIP_SCHEMES = ('data:', 'blob:', '#', 'mailto:', 'tel:', 'javascript:', 'http://', 'https://', '//')


def truncate_at_extension(url):
    """Cut a greedily-captured URL at its first valid extension, keeping the query.

    Returns None when nothing that looks like an asset is in it.
    """
    m = EXT_AT.search(url)
    if not m:
        return None
    end = m.end()
    if end < len(url) and url[end] == '?':
        stop = QUERY_STOP.search(url, end)
        end = stop.start() if stop else len(url)
    return url[:end]


def local_name(url, claimed=None):
    """Local filename for an asset URL, unique across the whole mirror.

    Query strings are part of the identity, not noise: srcset candidates like
    `?scale-down-to=512` and `?width=1024` are different images sharing one
    path, so collapsing them collapses every candidate onto one file. Distinct
    query -> distinct file.

    Basenames are not unique either — `/images/hero.png` and `/blog/hero.png`
    are different images with the same name, and one silently overwriting the
    other is a wrong-image bug no screenshot catches. So the plain basename is
    used only while it is unclaimed; the second URL wanting it gets the
    disambiguated form. `claimed` maps name -> url and is updated in place.
    """
    split = urlsplit(url)
    name = os.path.basename(split.path) or 'index'
    stem, ext = os.path.splitext(name)
    tag = hashlib.sha1(url.encode()).hexdigest()[:8]
    if split.query:
        name = f'{stem}__{tag}{ext}'
    if claimed is None:
        return name
    if claimed.get(name, url) != url:
        name = f'{stem}__{tag}{ext}'
    claimed.setdefault(name, url)
    return name


def harvest(text, base):
    """Every asset URL in a blob, absolute and relative, resolved against base."""
    found = set()
    for raw in URL_ANY.findall(text.replace('&amp;', '&')):
        u = truncate_at_extension(raw)
        if u:
            found.add(u)
    for pat in REL_PATTERNS:
        for m in pat.finditer(text):
            rel = m.group(3).strip().replace('&amp;', '&')
            if not rel or rel.startswith(SKIP_SCHEMES[:6]):
                continue
            u = truncate_at_extension(urljoin(base, rel))
            if u:
                found.add(u)
    # Both quote styles, matching SRCSET_ATTR above. Double-quote-only here meant
    # a single-quoted srcset was never FETCHED, so the rewriter had nothing to
    # point at and the origin URL survived — the blank-box failure again, with a
    # build log reading `failed: 0`.
    for s in re.findall(r'srcset\s*=\s*(?:"([^"]+)"|\'([^\']+)\')', text, re.I):
        s = s[0] or s[1]
        for cand in s.split(','):
            cand = cand.strip().split()[0] if cand.strip() else ''
            if cand:
                u = truncate_at_extension(urljoin(base, cand.replace('&amp;', '&')))
                if u:
                    found.add(u)
    return found


def cms_siblings(urls):
    """CMS collections ship as -chunk-/-indexes- pairs and only one name is a
    literal — the sibling is built by runtime substitution, so a scan finds one
    and the loader 404s on the other, rendering the collection empty with no
    error. A derived name that 404s upstream is expected and harmless."""
    out = set()
    for u in urls:
        if '-chunk-' in u:
            out.add(u.replace('-chunk-', '-indexes-'))
        elif '-indexes-' in u:
            out.add(u.replace('-indexes-', '-chunk-'))
    return out - set(urls)


def grab(url, name, outdir):
    """Fetch one asset. An HTML error page written to hero.png is an integrity
    problem, not an asset — reject it here rather than discover it in the diff."""
    dest = os.path.join(outdir, name)
    try:
        req = Request(url, headers={'User-Agent': UA, 'Accept': ACCEPT})
        with urlopen(req, timeout=45) as r:
            if r.status != 200:
                return url, None, f'HTTP {r.status}'
            data = r.read()
            ctype = r.headers.get('Content-Type', '')
    except Exception as e:
        return url, None, type(e).__name__
    if not data:
        return url, None, 'empty body'
    head = data[:64].lstrip().lower()
    if not TEXT_EXT.search(urlsplit(url).path) and (
            head.startswith(b'<!doctype') or head.startswith(b'<html')):
        return url, None, 'HTML body for a binary asset (404 page)'
    if 'text/html' in ctype and not urlsplit(url).path.lower().endswith(
            ('.html', '.htm')):
        return url, None, f'content-type {ctype.split(";")[0]} contradicts extension'
    with open(dest, 'wb') as f:
        f.write(data)
    return url, name, None


def classify_failure(why):
    """Which bucket a fetch failure belongs in.

    A 404 on the reference's own origin is the reference's defect, not the
    mirror's, and references/report.md keeps the two apart so the integrity gate
    is not tripped by a link that was already broken upstream.
    """
    if why.startswith('HTTP '):
        return 'origin_404s'
    if why.startswith('content-type'):
        return 'content_type_mismatches'
    if why.startswith('HTML body') or why == 'empty body':
        return 'integrity_problems'
    return 'network_failures'


def main():
    ap = argparse.ArgumentParser(description='Mirror assets and rewrite crawled pages.')
    ap.add_argument('--origin', default=None,
                    help='site origin; defaults to the manifest, then the first page URL')
    ap.add_argument('--out', default='site', help='directory to write pages into')
    ap.add_argument('--cdn', default='cdn', help='shared asset directory')
    ap.add_argument('--max-rounds', type=int, default=6,
                    help='asset discovery rounds; text assets reference more assets')
    a = ap.parse_args()

    if not os.path.exists('crawl-manifest.json'):
        raise SystemExit(
            'no crawl-manifest.json in this directory.\n'
            'build.py rewrites what crawl.py fetched, so run it from the same place:\n'
            '  python3 crawl.py <url> && python3 build.py')
    man = json.load(open('crawl-manifest.json'))
    pages = man['pages']
    urlmap = {k.rstrip('/'): v for k, v in man['urlmap'].items()}
    origin = a.origin or man.get('origin')
    if not origin and pages:
        s = urlsplit(pages[0]['url'])
        origin = f'{s.scheme}://{s.netloc}'
    if not origin:
        raise SystemExit('no origin: pass --origin')

    missing = [p['slug'] for p in pages if not os.path.exists(f"_raw/{p['slug']}")]
    if missing:
        raise SystemExit(f'crawl-manifest.json lists {len(pages)} pages but _raw/ is '
                         f'missing {len(missing)} of them ({", ".join(missing[:4])}). '
                         f'Re-run crawl.py — a partial _raw/ builds a partial site.')
    raw = {p['slug']: open(f"_raw/{p['slug']}", encoding='utf-8', errors='replace').read()
           for p in pages}
    page_url = {p['slug']: p['url'] for p in pages}

    # ---------- 1. discover assets, following text assets to a fixed point ----------
    os.makedirs(a.cdn, exist_ok=True)
    resolved, failed = {}, {}
    names, claimed = {}, {}      # url -> local name, and name -> first url to claim it
    frontier = set()
    for slug, html in raw.items():
        frontier |= harvest(html, page_url[slug])
    frontier |= cms_siblings(frontier)

    for rnd in range(a.max_rounds):
        todo = sorted(u for u in frontier if u not in resolved and u not in failed)
        if not todo:
            break
        print(f'round {rnd + 1}: fetching {len(todo)} assets')
        # Names are assigned single-threaded and in sorted order so the mapping
        # is deterministic across runs, then handed to the workers.
        for u in todo:
            names[u] = local_name(u, claimed)
        with ThreadPoolExecutor(max_workers=12) as ex:
            for url, name, err in ex.map(lambda u: grab(u, names[u], a.cdn), todo):
                if name:
                    resolved[url] = name
                else:
                    failed[url] = err
        # text assets build URLs no markup scan can see — re-scan them
        nxt = set()
        for url, name in resolved.items():
            if not TEXT_EXT.search(urlsplit(url).path):
                continue
            path = os.path.join(a.cdn, name)
            try:
                body = open(path, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            nxt |= harvest(body, url)
        nxt |= cms_siblings(nxt)
        frontier |= nxt

    print(f'assets mirrored: {len(resolved)}   failed: {len(failed)}')
    if failed:
        for url, why in sorted(failed.items())[:15]:
            print(f'  MISS  {why:<48} {url}')
        if len(failed) > 15:
            print(f'  ... {len(failed) - 15} more')

    # Assets that failed to mirror still get pointed at a local path. Leaving
    # them absolute would keep the mirror phoning home and break the "0 origin
    # refs" gate; pointed local they 404 in the network log, which is the
    # documented way these get found in the first place.
    table = {**resolved, **{u: names[u] for u in failed}}
    # longest first so one URL is never rewritten through another's prefix
    order = sorted(table, key=len, reverse=True)

    # Every change made to the reference's own markup, counted by class as it
    # happens. The report's integrity gate asks for 0 *unexplained* changes,
    # which is only answerable if the explained ones were tallied at the time.
    changes = {'url-relocalisation': 0, 'sri-strip': 0, 'href-inert': 0,
               'href-wired': 0, 'form-inert': 0, 'stamp': 0}

    def rewrite_urls(text, prefix, count=False):
        """Absolute asset URLs -> local path."""
        for url in order:
            if url in text:
                if count:
                    changes['url-relocalisation'] += text.count(url)
                text = text.replace(url, f'{prefix}{table[url]}')
            amp = url.replace('&', '&amp;')
            if amp != url and amp in text:
                if count:
                    changes['url-relocalisation'] += text.count(amp)
                text = text.replace(amp, f'{prefix}{table[url]}')
        return text

    def rewrite_relative(text, base, prefix, count=False):
        """Relative specifiers -> the same local path, resolved against base."""
        def one(m):
            spec = m.group(3).strip()
            if not spec or spec.startswith(SKIP_SCHEMES):
                return m.group(0)
            u = truncate_at_extension(urljoin(base, spec.replace('&amp;', '&')))
            if u and u in table:
                if count:
                    changes['url-relocalisation'] += 1
                return f'{m.group(1)}{m.group(2)}{prefix}{table[u]}{m.group(4)}'
            return m.group(0)
        for pat in REL_PATTERNS:
            text = pat.sub(one, text)

        def srcset_one(m):
            quote, body = m.group(1), m.group(2)
            rewritten = []
            changed = False
            for cand in body.split(','):
                stripped = cand.strip()
                if not stripped:
                    continue
                parts = stripped.split(None, 1)
                spec, descriptor = parts[0], (parts[1] if len(parts) > 1 else '')
                if not spec.startswith(SKIP_SCHEMES):
                    u = truncate_at_extension(urljoin(base, spec.replace('&amp;', '&')))
                    if u and u in table:
                        spec = f'{prefix}{table[u]}'
                        changed = True
                        if count:
                            changes['url-relocalisation'] += 1
                rewritten.append(f'{spec} {descriptor}'.strip())
            if not changed:
                return m.group(0)
            return f'srcset={quote}{", ".join(rewritten)}{quote}'

        return SRCSET_ATTR.sub(srcset_one, text)

    # ---------- 2. rewrite the mirrored text assets ----------
    # Inside module bodies the same string is resolved against the *module* as an
    # import specifier and against the *document* when it becomes a DOM src at
    # runtime. './x' is correct for one and 404s for the other; '/cdn/x' is
    # correct for both.
    for url, name in resolved.items():
        if not TEXT_EXT.search(urlsplit(url).path):
            continue
        path = os.path.join(a.cdn, name)
        try:
            body = open(path, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        # A `new URL(rel, base)` base must stay absolute — relativising it throws
        # TypeError, and one uncaught error in a framework bundle takes the whole
        # render down: images and boxes paint while ALL text disappears.
        body = re.sub(r"""(new\s+URL\s*\(\s*[^,]+,\s*)(['"`])https?://[^'"`]+\2""",
                      r'\1location.origin', body)
        body = rewrite_urls(body, f'/{a.cdn}/')
        body = rewrite_relative(body, url, f'/{a.cdn}/')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(body)

    # ---------- 3. rewrite every page ----------
    inert = mapped = 0
    wired_slugs = set()

    def relink(m):
        nonlocal inert, mapped
        pre, href, post = m.group(1), m.group(2), m.group(3)
        if href.startswith('#') or href.startswith(f'{a.cdn}/'):
            return m.group(0)
        slug = urlmap.get(urljoin(origin + '/', href).split('#')[0].rstrip('/'))
        if slug:
            mapped += 1
            wired_slugs.add(slug)
            return f'{pre}{slug}{post}'
        inert += 1
        # Never bare '#': an anchor component that runs
        # document.querySelector(href) raises SyntaxError on '#', and that throw
        # has stopped a whole component tree rendering. Any valid-but-unmatched
        # selector is equally dead as a link target.
        return f'{pre}#inert{post}'

    os.makedirs(a.out, exist_ok=True)
    host = urlsplit(origin).netloc
    bare_hash = 0
    for slug, html in raw.items():
        h = rewrite_urls(html, f'{a.cdn}/', count=True)
        h = rewrite_relative(h, page_url[slug], f'{a.cdn}/', count=True)
        # SRI: rewriting a file's bytes means its hash no longer matches, and the
        # browser drops the entire resource with no console error. Symptom is a
        # page rendering in Times with document.fonts.size === 0.
        h, n1 = re.subn(r'\s+(integrity|crossorigin)=(["\'])[^"\']*\2', '', h)
        h, n2 = re.subn(r'\s+(integrity|crossorigin)(?=[\s>])', '', h)
        changes['sri-strip'] += n1 + n2
        h = re.sub(r'(<a\b[^>]*?href=")([^"]*)(")', relink, h)
        h, n3 = re.subn(r'(<form\b[^>]*?action=")[^"]*(")', r'\1#inert\2', h)
        changes['form-inert'] += n3
        h, n4 = re.subn(r'<head>',
                        f'<head>\n<!-- LOCAL STUDY MIRROR of {host}. Internal links point at\n'
                        '     mirrored pages; everything else is inert. Do not publish. -->',
                        h, count=1)
        changes['stamp'] += n4
        bare_hash += len(re.findall(r'href="#"', h))
        with open(os.path.join(a.out, slug), 'w', encoding='utf-8') as f:
            f.write(h)
    changes['href-wired'], changes['href-inert'] = mapped, inert

    # Pages are served with --directory site, so cdn/ has to resolve from inside
    # it — both as the relative 'cdn/x' in markup and the root-absolute '/cdn/x'
    # in module bodies. Without this every asset 404s and the mirror looks broken
    # in a way the build log does not show.
    link = os.path.join(a.out, a.cdn)
    if not os.path.lexists(link):
        os.symlink(os.path.relpath(a.cdn, a.out), link)

    # ---------- 4. the build's own evidence ----------
    # report.py consumes this. Counted here rather than reconstructed later,
    # because a number recovered by re-reading the output is a guess about what
    # the build did, not a record of it.
    buckets = {'origin_404s': [], 'content_type_mismatches': [],
               'integrity_problems': [], 'network_failures': []}
    for url, why in sorted(failed.items()):
        buckets[classify_failure(why)].append({'url': url, 'why': why})
    total_bytes = 0
    for name in resolved.values():
        try:
            total_bytes += os.path.getsize(os.path.join(a.cdn, name))
        except OSError:
            pass
    manifest = {
        'origin': origin, 'out': a.out, 'cdn': a.cdn,
        'pages': [{'slug': s, 'url': page_url[s]} for s in sorted(raw)],
        'assets': {
            'mirrored': len(resolved),
            'bytes': total_bytes,
            'problems': len(buckets['integrity_problems']) + len(buckets['network_failures']),
            'origin_404s': buckets['origin_404s'],
            'content_type_mismatches': len(buckets['content_type_mismatches']),
            'failures': {k: v for k, v in buckets.items() if k != 'origin_404s'},
        },
        'links': {'wired': mapped, 'inert': inert,
                  'missing_targets': sorted(wired_slugs - set(raw)),
                  'bare_hash_hrefs': bare_hash},
        'markup_changes': changes,
    }
    # missing_targets is a count in the report schema; the list is kept beside it
    # because "which one" is the only form of that number anybody can act on.
    manifest['links'] = {**manifest['links'],
                         'missing_target_slugs': manifest['links']['missing_targets'],
                         'missing_targets': len(manifest['links']['missing_targets'])}
    with open('build-manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=1)

    print(f'pages written: {len(raw)}   internal links wired: {mapped}   made inert: {inert}')
    print(f'cdn files: {len(resolved)}   served from {a.out}/{a.cdn} -> ../{a.cdn}')
    print(f'build-manifest.json written: {total_bytes} bytes of assets, '
          f"{sum(changes.values())} classified markup changes, "
          f"{manifest['links']['missing_targets']} missing link targets")
    if failed:
        print(f'NOTE: {len(failed)} assets did not mirror — listed above. Load the built '
              f'site and read the network log before concluding a region failed.')


if __name__ == '__main__':
    main()

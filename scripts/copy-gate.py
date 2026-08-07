#!/usr/bin/env python3
"""
Copy, SEO and GEO gate — the content layer swipefile never checked.

The skill measures design to the pixel and says nothing about the words. On a
Match that is correct: copy is captured verbatim and rewriting it corrupts the
replication. But every Adapt, Brand and from-scratch build WRITES copy, and
nothing looked at it, so the page could be pixel-perfect and read like a machine.

Two halves, because they fail differently:

  AI-writing tells   — mechanical checks drawn from the `humanizer` skill's own
                       numbered categories. Load that skill to FIX prose; this
                       only tells you where to look. Judgement stays there.
  SEO / GEO          — presence checks. Structured data is the one that matters
                       most for generative engines and is the one most often
                       simply absent: both measured builds shipped zero JSON-LD.

    python3 copy-gate.py index.html
    python3 copy-gate.py index.html --match     # captured copy: skip prose checks
    python3 copy-gate.py index.html --json

Exit non-zero on failures. Warnings never fail the gate — a gate that cries wolf
gets ignored, which is the failure this whole file exists to prevent.
"""
import argparse, html as _html, json, re, sys

# --- humanizer categories that are mechanically detectable. Numbers cite that
# --- skill's own headings so a finding routes straight to the fix.
#
# Budgets are a RATE per 1000 words plus a hard floor, never an absolute count.
# Two superlatives in a 69-word paragraph is egregious; two across a 2000-word
# page is ordinary English. An absolute budget gets one of those wrong, and the
# one it gets wrong is the short punchy marketing copy this gate exists for.
TELLS = [
    ('7  AI vocabulary', re.compile(
        r'\b(delve|elevat\w+|seamless\w*|testament|tapestry|nestled|crucial|pivotal|'
        r'leverag\w+|robust|meticulous\w*|curat(?:e|ed|ing|ion)|realm|landscape|'
        r'unlock\w*|journey|embark|myriad|plethora|bespoke|artisanal|'
        r'game-chang\w+|cutting-edge|state-of-the-art|holistic|synerg\w+)\b', re.I), 6, 1),
    ('4  promotional language', re.compile(
        r'\b(finest|world-class|unparalleled|premier|ultimate|exceptional|'
        r'unrivall?ed|best-in-class|top-tier|second to none)\b', re.I), 2, 0),
    ('5  vague attribution', re.compile(
        r'\b(experts? (?:say|agree|believe)|(?:widely|generally) (?:regarded|considered|known)|'
        r'many believe|it is believed|studies show|research suggests)\b', re.I), 0, 0),
    ('3  superficial -ing analysis', re.compile(
        r',\s+(?:highlighting|showcasing|reflecting|underscoring|emphasi[sz]ing|'
        r'demonstrating|solidifying|cementing|ensuring)\b', re.I), 2, 0),
    ('9  negative parallelism', re.compile(
        r"\b(?:not (?:just|only|merely)|isn'?t (?:just|only|merely)|"
        r"more than (?:just|simply))\b", re.I), 2, 0),
    ('1  inflated significance', re.compile(
        r'\b(stands as|serves as) a (?:testament|reminder|symbol)\b|'
        r'\b(?:marks|represents) a (?:turning point|milestone|new era)\b', re.I), 1, 0),
    ('12 false range', re.compile(r'\bfrom \w+ to \w+,\s', re.I), 3, 1),
    ('18 emoji', re.compile('[\U0001F300-\U0001FAFF☀-➿]'), 0, 0),
    ('19 curly quotes', re.compile('[“”‘’]'), 40, 10),
    # 31-33 are the tells that actually date a 2026 page. They matter more than
    # "delve" now, and none of them are vocabulary — they are shapes.
    ('33 rhetorical opener', re.compile(
        r"(?:^|[.!?]\s+)(?:Honestly\?|Look,|Here'?s the thing|The thing is|"
        r"Let'?s be honest|Real talk|But here'?s|Turns out,)", re.I), 1, 0),
    ('32 aphorism formula', re.compile(
        r'\bis the (?:language|currency|architecture|backbone|lifeblood) of\b|'
        r'\bis not (?:a|just a) \w+,? but (?:a|an)\b|\bbecomes? a trap\b', re.I), 1, 0),
]


def staccato_runs(text, max_words=5, run=3):
    """humanizer 31: a run of very short sentences manufacturing drama.

    Structural, not lexical, so no vocabulary swap evades it. One short sentence
    for emphasis is fine; three in a row is engineered.
    """
    sents = [x.strip() for x in re.split(r'(?<=[.!?])\s+', text) if x.strip()]
    worst, cur = 0, 0
    for x in sents:
        cur = cur + 1 if len(x.split()) <= max_words else 0
        worst = max(worst, cur)
    return worst


def visible_text(doc):
    """Rendered words only — no scripts, styles, or HTML comments.

    Comments matter: a build's own design notes sitting in <!-- --> are not copy,
    and counting them produces phantom findings about text no reader ever sees.
    """
    s = re.sub(r'<!--.*?-->', ' ', doc, flags=re.S)
    s = re.sub(r'<(script|style|svg|noscript)[^>]*>.*?</\1>', ' ', s, flags=re.S | re.I)
    s = _html.unescape(re.sub(r'<[^>]+>', ' ', s))
    return re.sub(r'\s+', ' ', s).strip()


def attr(doc, pattern):
    m = re.search(pattern, doc, re.I | re.S)
    return _html.unescape(m.group(1)).strip() if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('file')
    ap.add_argument('--match', action='store_true',
                    help='Match mode: copy was captured verbatim from the reference. '
                         'Prose checks are SKIPPED — rewriting captured copy corrupts the '
                         'replication and breaks the Step 4 diff. SEO/GEO still reported.')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    doc = open(a.file, encoding='utf-8', errors='replace').read()
    text = visible_text(doc)
    words = text.split()
    n = len(words) or 1
    fails, warns, notes = [], [], []

    # ---------- prose ----------
    hits = {}
    if a.match:
        notes.append('Match mode: prose checks skipped (captured copy is not ours to rewrite).')
    else:
        for label, rx, rate, floor in TELLS:
            found = rx.findall(text)
            budget = max(floor, round(rate * n / 1000))
            if len(found) > budget:
                hits[label] = len(found)
        # em dashes are about density, not presence (humanizer #14)
        em = text.count('—')
        if em > max(2, n / 150):
            hits['14 em-dash density'] = em
        run = staccato_runs(text)
        if run >= 4:
            hits['31 staccato drama'] = run
        for label, count in sorted(hits.items(), key=lambda kv: -kv[1]):
            fails.append(f'{label}: {count} occurrences')
        if hits:
            fails.append('Load the `humanizer` skill and fix these; it holds the rewrite guidance.')

    # ---------- SEO ----------
    title = attr(doc, r'<title[^>]*>(.*?)</title>')
    desc = attr(doc, r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']')
    canon = re.search(r'<link[^>]+rel=["\']canonical["\']', doc, re.I)
    lang = re.search(r'<html[^>]+lang=', doc, re.I)
    h1s = re.findall(r'<h1[\s>]', doc, re.I)
    og = {k: bool(re.search(rf'property=["\']og:{k}["\']', doc, re.I))
          for k in ('title', 'description', 'image')}
    imgs = re.findall(r'<img\b[^>]*>', doc, re.I)
    no_alt = [i for i in imgs if not re.search(r'\balt=', i, re.I)]

    if not title:
        fails.append('SEO: no <title>')
    elif not 15 <= len(title) <= 65:
        warns.append(f'SEO: title is {len(title)} chars (aim 15-65)')
    if not desc:
        fails.append('SEO: no meta description')
    elif not 70 <= len(desc) <= 165:
        warns.append(f'SEO: meta description is {len(desc)} chars (aim 70-165)')
    if len(h1s) != 1:
        fails.append(f'SEO: {len(h1s)} <h1> elements (need exactly 1)')
    if not lang:
        fails.append('SEO: <html> has no lang attribute')
    if not canon:
        warns.append('SEO: no canonical link')
    missing_og = [k for k, v in og.items() if not v]
    if missing_og:
        warns.append('SEO: missing og: tags — ' + ', '.join(missing_og))
    if no_alt:
        fails.append(f'A11Y/SEO: {len(no_alt)} <img> without alt')

    # ---------- GEO ----------
    ld = re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', doc, re.S | re.I)
    types = []
    for block in ld:
        try:
            data = json.loads(block.strip())
        except Exception:
            warns.append('GEO: a JSON-LD block does not parse')
            continue
        for item in (data if isinstance(data, list) else [data]):
            if isinstance(item, dict) and item.get('@type'):
                t = item['@type']
                types += t if isinstance(t, list) else [t]
    if not ld:
        fails.append('GEO: no JSON-LD structured data. Generative engines lean on it to '
                     'cite a page; a business page needs at minimum Organization or '
                     'LocalBusiness, plus WebSite.')
    else:
        notes.append('GEO: structured data types — ' + ', '.join(types or ['(untyped)']))

    # Specificity is what makes a page quotable: named numbers, dates, proper nouns.
    numbers = len(re.findall(r'\b\d[\d,.:]*\b', text))
    if numbers / n < 0.01:
        warns.append(f'GEO: very few concrete figures ({numbers} in {n} words). '
                     'Specifics are what engines quote.')

    ok = not fails
    if a.json:
        print(json.dumps({'pass': ok, 'file': a.file, 'words': n, 'proseHits': hits,
                          'failures': fails, 'warnings': warns, 'notes': notes,
                          'seo': {'title': title, 'descriptionLen': len(desc or ''),
                                  'h1': len(h1s), 'og': og, 'canonical': bool(canon)},
                          'geo': {'jsonLdBlocks': len(ld), 'types': types}}, indent=1))
    else:
        print(f'{a.file}  —  {n} words of visible copy')
        for x in notes:
            print(f'  note  {x}')
        for x in warns:
            print(f'  WARN  {x}')
        for x in fails:
            print(f'  FAIL  {x}')
        print('\nCOPY/SEO/GEO GATE: ' + ('PASS' if ok else 'FAIL'))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""End-to-end test of swipefile scripts/build.py against a synthetic origin."""
import re
import json, os, shutil, socket, subprocess, sys, tempfile, threading, time
import pathlib as _pl
SCRIPTS = str(_pl.Path(__file__).resolve().parent.parent)
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs

BUILD = os.path.join(SCRIPTS, 'build.py')
SERVE = os.path.join(SCRIPTS, 'serve.py')

# ---------------- synthetic origin ----------------
class Origin(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        u = urlsplit(self.path); q = parse_qs(u.query)
        accept = self.headers.get('Accept', '')

        def send(body, ctype='application/octet-stream', status=200, vary=False):
            self.send_response(status)
            self.send_header('Content-Type', ctype)
            if vary: self.send_header('Vary', 'Accept')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers(); self.wfile.write(body)

        if u.path == '/hero.png':
            # vary: Accept — AVIF bytes to a browser-ish Accept, PNG otherwise
            fmt = b'AVIF' if 'image/avif' in accept else b'PNG-'
            w = (q.get('width') or ['0'])[0]
            return send(fmt + f'-w{w}'.encode(), 'image/avif' if b'AVIF' in fmt else 'image/png', vary=True)
        if u.path == '/app.mjs':
            return send((f"import('./chunk.mjs');\n"
                         f"const b = new URL('rel/x', '{ORIGIN}/base/');\n").encode(),
                        'text/javascript')
        if u.path == '/chunk.mjs':
            return send(f"const img = '{ORIGIN}/deep.png';\n".encode(), 'text/javascript')
        if u.path == '/deep.png':
            return send(b'DEEPPNG', 'image/png')
        if u.path == '/data-chunk-abc.json':
            return send(b'{"chunk":1}', 'application/json')
        if u.path == '/data-indexes-abc.json':
            return send(b'{"indexes":1}', 'application/json')
        if u.path == '/broken.png':
            # 200 with an HTML error body — the classic silent integrity failure
            return send(b'<!doctype html><html><body>404</body></html>', 'text/html')
        if u.path == '/theme.css':
            return send(b'@font-face{src:url(fonts/face.woff2)}', 'text/css')
        if u.path == '/fonts/face.woff2':
            return send(b'WOFF2BYTES', 'font/woff2')
        if u.path == '/v/home/images/photo_small.png':
            return send(b'PHOTOSMALL', 'image/png')
        if u.path == '/v/home/images/photo_small_2x.png':
            return send(b'PHOTOSMALL2X', 'image/png')
        if u.path == '/v/home/images/photo_large.jpg':
            return send(b'PHOTOLARGE', 'image/jpeg')
        self.send_error(404)

def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p

PORT = free_port()
ORIGIN = f'http://127.0.0.1:{PORT}'
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Origin)
threading.Thread(target=srv.serve_forever, daemon=True).start()

# ---------------- fixture crawl output ----------------
work = tempfile.mkdtemp(prefix='build-test-')
os.makedirs(f'{work}/_raw')
PAGE = f'''<!doctype html><html><head>
<link rel="stylesheet" href="{ORIGIN}/theme.css" integrity="sha384-DEADBEEF" crossorigin="anonymous">
<script src="{ORIGIN}/app.mjs" type="module" integrity="sha384-CAFE"></script>
<style>:root{{--bg:url({ORIGIN}/hero.png?width=1024);--next-prop:red}}</style>
</head><body>
<img src="{ORIGIN}/hero.png?width=512" srcset="{ORIGIN}/hero.png?width=512 512w, {ORIGIN}/hero.png?width=1024 1024w">
<img src="{ORIGIN}/broken.png">
<picture>
  <source srcset="/v/home/images/photo_small.png, /v/home/images/photo_small_2x.png 2x" media="(max-width:734px)">
  <img src="/v/home/images/photo_large.jpg" alt="students">
</picture>
<a href="/about">About</a>
<a href="https://elsewhere.example/x">Off-site</a>
<form action="/subscribe"></form>
<script>fetch("{ORIGIN}/data-chunk-abc.json")</script>
</body></html>'''
open(f'{work}/_raw/index.html', 'w').write(PAGE)
open(f'{work}/_raw/about.html', 'w').write('<!doctype html><html><head></head><body>about</body></html>')
json.dump({
    'origin': ORIGIN,
    'pages': [{'url': f'{ORIGIN}/', 'slug': 'index.html', 'depth': 0},
              {'url': f'{ORIGIN}/about', 'slug': 'about.html', 'depth': 1}],
    'urlmap': {f'{ORIGIN}': 'index.html', f'{ORIGIN}/about': 'about.html'},
    'skipped': {},
}, open(f'{work}/crawl-manifest.json', 'w'))

r = subprocess.run([sys.executable, BUILD], cwd=work, capture_output=True, text=True)
print(r.stdout)
if r.returncode != 0:
    print(r.stderr); sys.exit('build.py failed')

PASS, FAIL = [], []
def check(name, cond, detail=''):
    (PASS if cond else FAIL).append(name)
    print(f'{"PASS" if cond else "FAIL"}  {name}{"  — " + detail if detail and not cond else ""}')

cdn = os.listdir(f'{work}/cdn')
page = open(f'{work}/site/index.html').read()

check('site/cdn symlink exists', os.path.islink(f'{work}/site/cdn'))
check('site/cdn resolves to the asset dir',
      os.path.isdir(os.path.realpath(f'{work}/site/cdn')))

hero = [f for f in cdn if f.startswith('hero')]
check('query strings kept as distinct assets (2 hero files)', len(hero) == 2, str(hero))
check('hero fetched with browser Accept (AVIF, not PNG)',
      any(open(f'{work}/cdn/{f}', "rb").read().startswith(b'AVIF') for f in hero),
      str([open(f'{work}/cdn/{f}','rb').read() for f in hero]))

check('integrity= stripped from markup', 'integrity=' not in page)
check('crossorigin= stripped from markup', 'crossorigin=' not in page)
check('unmirrored link is #inert, never bare #', 'href="#inert"' in page)
check('no bare href="#" remains', 'href="#"' not in page)
check('form action neutralised to #inert', 'action="#inert"' in page)
check('internal link wired to local slug', 'href="about.html"' in page)
check('no absolute origin refs left in the page', ORIGIN not in page)
check('do-not-publish stamp carries the real host',
      '127.0.0.1' in page and 'framer.com' not in page)

# root-relative <source srcset> — the Apple.com bug: harvested for fetching but
# never rewritten, so a <picture> whose <source> matches renders a blank box
# (browsers do not fall back to <img> when a matching <source> just 404s).
check('root-relative srcset assets were fetched',
      any(f.startswith('photo_small') for f in cdn), str(cdn))
check('<source srcset> rewritten off the origin path',
      '/v/home/images/' not in page, page[page.find('<source'):page.find('<source')+200])
check('srcset descriptor (2x) preserved after rewrite',
      re.search(r'srcset="[^"]*cdn/photo_small_2x[^"]*2x', page) is not None, page)
check('fallback <img src> for the picture also rewritten',
      'src="cdn/photo_large' in page, page)

check('css url() truncated at extension, not swallowed by --next-prop',
      any(f.startswith('theme') for f in cdn) and '--next-prop:red' in page)
check('relative url() inside the stylesheet followed (face.woff2)',
      any(f.startswith('face') for f in cdn), str(cdn))

mjs = [f for f in cdn if f.startswith('app')]
body = open(f'{work}/cdn/{mjs[0]}').read() if mjs else ''
check('module body rewritten root-absolute (/cdn/…)', '/cdn/' in body, body)
check('new URL() base kept absolute via location.origin',
      'location.origin' in body and 'ORIGIN/base' not in body, body)
check('relative dynamic import followed to chunk.mjs',
      any(f.startswith('chunk') for f in cdn), str(cdn))
check('fixed-point: asset referenced only inside chunk.mjs was mirrored',
      any(f.startswith('deep') for f in cdn), str(cdn))
check('CMS -chunk-/-indexes- sibling derived',
      any('indexes' in f for f in cdn), str(cdn))
check('HTML body served as .png was rejected, not written',
      not any(f.startswith('broken') for f in cdn), str(cdn))

# ---------------- the build's own evidence, for report.py ----------------
# Counted during the rewrite rather than reconstructed afterwards: a number
# recovered by re-reading the output is a guess about what the build did.
man = json.load(open(f'{work}/build-manifest.json'))
check('build-manifest.json written', bool(man))
check('every integrity/crossorigin attribute counted as an sri-strip',
      man['markup_changes']['sri-strip'] == 3, man['markup_changes'])
check('wired and inert links counted separately',
      man['links']['wired'] == 1 and man['links']['inert'] == 1, man['links'])
check('form neutering counted', man['markup_changes']['form-inert'] == 1)
check('the do-not-publish stamp counted once per page',
      man['markup_changes']['stamp'] == 2, man['markup_changes'])
check('url relocalisation counted', man['markup_changes']['url-relocalisation'] > 0)
check('0 missing link targets on a mirror whose links all resolve',
      man['links']['missing_targets'] == 0, man['links'])
check('0 bare # hrefs recorded', man['links']['bare_hash_hrefs'] == 0)
check('asset count and bytes recorded',
      man['assets']['mirrored'] == len(cdn) and man['assets']['bytes'] > 0,
      (man['assets']['mirrored'], len(cdn), man['assets']['bytes']))
check('an HTML body served as .png is an integrity problem, not an origin 404',
      man['assets']['problems'] >= 1 and not man['assets']['origin_404s'],
      man['assets'])

# The contract between the two scripts, checked against a real build rather than
# a fixture — test_report.py hand-writes this manifest, so both suites could stay
# green while the shape they agree on drifts apart.
subprocess.run([sys.executable, os.path.join(SCRIPTS, 'report.py'), '--init'],
               cwd=work, capture_output=True, text=True)
rr = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'report.py'),
                     '--site', 'example.com', '--crawl', 'crawl-manifest.json',
                     '--build', 'build-manifest.json', '--measured', 'measurements.json'],
                    cwd=work, capture_output=True, text=True)
links_line = next((l for l in rr.stdout.splitlines() if 'links:' in l), '')
assets_line = next((l for l in rr.stdout.splitlines() if 'content-type' in l), '')
check('report.py consumes the manifest build.py actually writes',
      links_line.strip().startswith('ok'), rr.stdout + rr.stderr)
check('link counts reach the report as measured values, not "not measured"',
      '0 missing, 0 bare #' in links_line, links_line)
check("the build's own content-type tally reaches the report",
      'not measured — no build manifest' not in assets_line, assets_line)

# ---------------- the mirror actually serves ----------------
sp = free_port()
p = subprocess.Popen([sys.executable, SERVE, '--directory', 'site', '--port', str(sp)],
                     cwd=work, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    import urllib.request, urllib.error
    end = time.time() + 10
    while time.time() < end:
        try: socket.create_connection(('127.0.0.1', sp), 0.2).close(); break
        except OSError: time.sleep(0.05)
    ok = True
    for f in hero + [x for x in cdn if x.startswith('app')]:
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{sp}/cdn/{f}', timeout=5) as r:
                ok &= r.status == 200
        except Exception as e:
            ok = False; print('   asset 404:', f, e)
    check('every asset resolves through the served site root', ok)
finally:
    p.terminate(); p.wait(timeout=5)

srv.shutdown()
print(f'\n{len(PASS)} passed, {len(FAIL)} failed')
shutil.rmtree(work, ignore_errors=True)
if FAIL: print('FAILED:', ', '.join(FAIL)); sys.exit(1)

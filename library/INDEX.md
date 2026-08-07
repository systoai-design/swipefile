# Design library — index

One line per site captured. Newest last. Read this before a capture; append to it
after. Full entries live beside this file as `<domain>.md`.

**Every entry is callable by name.** "Build my site, reference: <a name from the
*Call it* column below>"
resolves through the *Call it* column below — match case-insensitively against
the name, the domain, or any alias in the entry — then runs Adapt from the
entry's measured system (see "Design from a named reference" in SKILL.md).

**What belongs here:** design *system* facts — palettes, type scales, spacing,
easing curves, breakpoints, layout mechanics, structural patterns, and the
gotchas hit while rebuilding. Measurements and patterns, which are the shared
vocabulary of web design.

**What does not:** body copy, imagery, logos, or any asset. Those stay in the
local mirror for the job that needed them. The library is knowledge, not content.

| Call it | Site | Captured | Path | Motion fidelity · signature | Notable |
|---|---|---|---|---|---|
| **YouTube** | [youtube.com](youtube.com.md) | 2026-07-29 | rebuild | **partial** · `cubic-bezier(.05,0,0,1)` @ .1–.3s | Tonal white-alpha surface system; grid column count is a JS-set CSS var, not a media query |
| **Phenomenon** | [phenomenonstudio.com](phenomenonstudio.com.md) | 2026-07-30 | mirror (scripted) | **spec** · `cubic-bezier(.22,1,.36,1)` @ .3s | Sticky-stacking section choreography; `.isview`+`.visible` scroll-reveal gate |
| **Lando Norris** | [landonorris.com](landonorris.com.md) | 2026-07-30 | mirror (scripted) | **signature-only** · `cubic-bezier(.65,.05,0,1)` @ .75s | Whole rem scale is one `calc()` pinned to a 1728 design width; WebGL hero randomises its livery per load; Webflow SRI silently voids the mirror |
| **CreateStudio** | [createstudio.framer.media](createstudio.framer.media.md) | 2026-07-30 | mirror (scripted) | **spec** · none in CSS — all motion is JS (Motion lib) | Framer: SSR'd but script-*dependent* (73% static vs 98.5% scripted); `new URL()` bases must stay absolute or all text vanishes; one `#ff6041` accent over a full greyscale ramp |
| **OSA** | [osa.framer.website](osa.framer.website.md) | 2026-07-30 | mirror (scripted) | **partial** · none in CSS — all motion is JS (Motion lib) | Second Framer capture: reusing the hardened build hit 99.37% vs a 99.46% ceiling first try. Satoshi 500 carries the whole UI, Instrument Serif only at 46–54px display. CMS `-chunk-`/`-indexes-` pairs |
| **Phillia** | [philllia.com](philllia.com.md) | 2026-07-30 | capture only (Adapt) | **signature-only** · `cubic-bezier(.22,1,.36,1)` / `(.16,1,.3,1)` @ .42s | Four named curves for four *jobs* + stagger/travel ladders — the most complete motion-token set in the library. Next.js with **no JS animation library at all**. Two palettes in one stylesheet |
| **Systo** | [systo-ai.com](systo-ai.com.md) | 2026-07-30 | rendered-DOM (Adapt content source) | **partial** · word-reveal hero + count-ups | Kyle's own site; first library-composed redesign target (6 donors). SPA shell undercounts content ~8× — extract from rendered DOM. Serif-display-only discipline confirmed a 4th time |
| **FintechX** | [fintechx-wbs.framer.website](fintechx-wbs.framer.website.md) | 2026-07-30 | capture only (Adapt donor) | **partial** · baked-spring fade-up: `translateY(20/10px)`+opacity @ 400/600/1000ms, ~100ms ladder | Fourth Framer capture, and it **settles the onefin easing question**: `cubic-bezier(.44,0,.56,1) @ .4s` and the `linear(0, 0.024, 0.0823, …)` spring appear byte-identical on both unrelated templates — Framer/Motion defaults, not authorship. Reusable bento (3×380/gap 30, 393+393+374-span vs 528+239) and a dashboard-showcase frame whose UI bleeds off the bottom edge. Band names are generic, so identify by geometry |
| **OneFin** | [onefin.framer.website](onefin.framer.website.md) | 2026-07-30 | mirror (scripted) + 1440 runtime addendum + About-section spec | **partial** page-wide; **spec** for the About/statement section (scrub profile, pointer-parallax coefficients, per-character reveal) · `cubic-bezier(.44,0,.56,1)` @ .4s + springs; **per-character `blur(10px)→0` @400ms, 50ms/char uncapped** | Third Framer capture, and the one that broke three priors: Framer **does** ship CSS easing (45 uses, same curve as its appear tween); breakpoint edges are integer *and* `.98`. Found the `vary: Accept` AVIF/PNG trap. 25/25 pages all at ceiling, geometry 100.00% exact at 0px |
| **Apple** | [apple.com](apple.com.md) | 2026-08-03 | mirror (static), scoped 30/846 | **partial** · `ease-in-out` @ 1000ms (fades) + `cubic-bezier(.4,…)` @ 320ms (UI); only 1/43 scroll-triggered | Hand-built, no framework fingerprint; SF Pro Display/Text, no fluid rem driver. Found and fixed a real engine bug: `srcset` was fetched but never rewritten, leaving real photos blank (`<picture>` doesn't fall back to `<img>` on a 404'd `<source>`). Real JSON-LD present (rare in this library). Homepage is largely load-time motion, not scroll-choreographed — a first for this library |
| **Wise** | [wise.com](wise.com.md) | 2026-08-08 | mirror, scoped 142/174 | **partial** · `cubic-bezier(.34,1,.64,1)` @ 1500/1600ms; 50/100ms stagger | Next.js, geo-personalized homepage (no redirect — verify locale before trusting a capture). Found and fixed three real engine bugs: a JS template-literal interpolation crashed build.py's URL resolver; a raw space in a CDN filename raised InvalidURL; an inline GTM/Mixpanel bootstrap survived every markup rewrite and still beaconed production analytics. Also fixed motion-extract.js: a naive comma-split truncated 4-param cubic-beziers, and CSSAnimation was double-recorded against CSSTransition's own "covered by events" exclusion, manufacturing phantom `linear` curves. One real-time pricing-comparison widget is 100% client-fetched with no SSR fallback — architecturally uncapturable, drives every reported delta (68.66% text, 1 vs 28 animations) |


**Motion fidelity gates the named-reference path.** Only `spec` lets a build take
its motion from the entry; `partial` saves most of a capture but not the mapping;
`signature-only` and `none` mean the motion must be re-captured or the build
ships without it and says so. **Phenomenon** and **CreateStudio** are `spec` as of 2026-07-31 — both
re-measured with `scripts/motion-extract.js` through `cdp-run.py --pre`, so both
can be ordered by name and will animate. The rest still need a motion-only
re-capture before their motion can be built from; it is one cheap pass each.

- **A design system can ship two palettes at once.** philllia.com carries a warm
  editorial set (`--background`/`--primary`/`--accent`) *and* a separate cooler
  `--sig-*` set with its own display scale, both live in one stylesheet. Tally
  token prefixes before assuming one system, or you will average two languages
  into a muddle that matches neither.
- **Name curves by job, not by signature.** The richest motion token set measured
  so far uses four curves for four purposes — reveal, soft settle, hover, swap —
  plus a stagger ladder (40/80/140ms) and a travel ladder (12/24/48px), so
  "reveal this grid looser" is a token swap rather than a hand-tuned delay. This
  is the architecture to copy; values are cheap to re-derive. Seen on philllia.
- **A serif display face earns its keep only at display size.** Two independent
  confirmations — osa (Instrument Serif at 46–54px only) and philllia (Fraunces
  at 20–48px, weight 400 only), each with a geometric sans carrying the entire
  interface. If a rebuild's serif is showing up at 15px body copy, it has drifted.
- **An IntersectionObserver only reports transitions it witnesses**, so any
  reveal gate needs a self-healing sweep on load/scroll/resize that reveals
  anything already at or above the trigger line. Without it, landing on an
  anchor, restoring a scroll position, or jumping to the page bottom strands
  every skipped section at `opacity: 0` permanently — measured on a fresh build:
  a bottom jump revealed 1 of 11 sections and left 30 items invisible. The guard
  must test `rect.top < line` **only**; adding `rect.bottom > 0` re-breaks the
  jump case by excluding anything already scrolled past. Same guard belongs on
  count-ups and any progress element, and under reduced motion they must resolve
  to their final value up front rather than waiting for a view that never comes.
- **`.parent > .child` is the wrong combinator for a reveal gate.** Items are
  routinely nested a level deeper than the gate element (inside a `.prose` or
  `.section-head` wrapper), so a direct-child selector silently skips them —
  they get neither the hidden state nor the transition and just render static,
  which looks like "the animation didn't run" rather than a selector bug.
- **The in-app browser pane's IntersectionObserver does not fire.** A fresh
  observer at threshold 0.05, on an element demonstrably on screen, with working
  scroll, never fired — while the identical page in headless CDP revealed 11/11
  sections. Combined with the pane rendering a working page fully black on an
  earlier capture: use the pane for interaction only, and verify all
  scroll-driven behaviour through CDP.

## Cross-site patterns observed

Accumulating notes — the point of keeping the library. Update as N grows.

- **Move the mouse before calling anything static.** Three independent probes
  on onefin's About tiles — a 19-point scroll sweep, an entry-opacity trace and
  a pre-load WAAPI capture — all reported "no motion", and all three were wrong:
  the tiles carry Framer's `data-parallaxfloating` and track the POINTER
  (≈ −0.035×dx, −0.055×dy from viewport centre, ±22/±19px, ~600ms settle).
  Scroll, entry and WAAPI instrumentation share a blind spot, and it covers the
  most visible motion on that section. Grep for `data-parallaxfloating` and run
  a pointer pass as part of Step 1's interaction states, not as an afterthought.

- **Scroll-reveal is almost always a two-class gate**: a base class sets
  `opacity:0`, JS adds a second class for the end state. Find both class names and
  you can render the end state statically without running their JS. Seen on
  phenomenonstudio (`.isview` → `.visible`).
- **Column counts are increasingly JS-computed, not media queries.** Grep the CSS
  for the variable before assuming a breakpoint ladder exists. Seen on youtube.
- **A site's "signature" easing is the one with the highest use count**, and it is
  usually custom, not a Material/standard curve. Tally `cubic-bezier(...)` by
  frequency across the whole stylesheet rather than reading one component.
- **Dark UIs increasingly layer white at low alpha** rather than using opaque
  greys, so interactive surfaces composite over any background. Seen on youtube
  (8/10/20% white).
- **`@font-face` frequently lives in an inline `<style>` block**, not the linked
  stylesheets — attribute-level URL rewriting misses it, cross-origin fonts are
  CORS-blocked, and the fallback is silent. Computed `fontFamily` echoes the
  request, so it cannot detect this; only `document.fonts.check()` + a canvas
  width A/B can. Seen on phenomenonstudio.
- **WordPress sitemaps overstate the site ~7×.** 585 URLs → 368 blog machinery
  (articles/FAQ/tags), 114 portfolio, ~40 actual nav surface. Histogram by first
  path segment before crawling; the design surface is the small slice.
- **Subresource Integrity silently voids a mirror.** A linked stylesheet carrying
  `integrity="sha384-…"` stops loading the instant you rewrite its `url()`s,
  because the bytes no longer hash to the recorded value — and the browser drops
  the *entire* sheet with no console error. Symptom is a page rendering in Times
  with `document.fonts.size === 0`. Strip `integrity` and `crossorigin` from every
  `<link>`/`<script>` in any mirror. Seen on landonorris (Webflow); assume every
  Webflow and every CDN-hosted stylesheet ships it. This also sharpens the
  font-face pattern below: `document.fonts.check()` returned **true** throughout,
  so only the canvas width A/B detected it.
- **A fluid rem driver beats a breakpoint ladder, and it is one line.** Root
  font-size set to `calc(clamp(min,100vw,max) / <design-width> * 16)` makes the
  entire rem-based type and spacing scale fluid between two clamps, with no
  per-step media queries. Verify by reading computed root font-size at a known
  viewport (landonorris: 11.8519px at 1280 = 1280/1728×16). Grep for
  `--design-width` / `--fluid-font` before assuming breakpoints drive the scale.
- **Runtime-built asset paths are invisible to static analysis.** Bundles
  increasingly construct texture/model URLs from a descriptor at load time, so no
  literal string exists to grep. Build the mirror, load it in a real browser, and
  read the network log for 404s — that pass found 13 assets the source scan
  missed on landonorris. Do this before concluding a region "failed to mirror".
- **Sites randomise a visual variant per page load**, which caps the achievable
  diff and is not a defect in your build. Detect it by loading the reference N
  times and reading the relevant runtime state, not by staring at screenshots.
  Where the runtime exposes a writable params object, pin it identically on both
  sides before capturing. Seen on landonorris (helmet livery, 5 variants).
- **Interrogate the runtime before grepping the bundle.** A globals-exposed
  control object (`window.landoGL`) answered asset paths, scene parameters and
  colour values in one `evaluate` call that minified-source grep could not.
  Check `Object.keys(window)` for a project-named global first.
- **A CDN that answers `vary: Accept` hands your mirror different bytes than it
  hands the browser.** framerusercontent.com serves **AVIF** to Chrome's
  `image/avif,image/webp,…` and **PNG** to `Accept: */*` — which is what every
  mirroring fetch sends by default. The mirror then renders lossless PNG where
  the reference renders lossy AVIF. This is invisible to every structural check:
  geometry, text, fonts, decode sizes and node counts all verify perfectly. Its
  only signature is a pixel diff showing a uniform 1–2 level delta across ~90%
  of *background* pixels with **text untouched** — nothing is misplaced, so
  there is nothing to inspect. Send the browser's Accept header, keep the
  original filenames so references stay valid, and set `Content-Type` from magic
  bytes in the server. Seen on onefin (128 of 160 rasters were actually AVIF).
- **Never drop the query string from a CDN asset URL until you know what it
  does.** The recipe's "strip `?v=` cache-busters" is right for cache-busters and
  catastrophic for a CDN that *resizes from the query*: srcset candidates like
  `?scale-down-to=512&width=1024` and `?width=1024` are different images sharing
  one path, so stripping collapses every candidate onto the full-size original
  and the browser downscales a far larger source. Fetch each distinct
  `(path, query)` as its own file. Detect it in one cheap pass — compare
  `naturalWidth`/`naturalHeight` for every image across both sides; no pixel
  diff needed. Seen on onefin (186 variants in markup, 157 more in modules).
- **A clean network log does not mean the right assets loaded.** The two traps
  above both fail *silently with HTTP 200* — wrong format, wrong resolution,
  nothing to 404 on. Asset verification therefore needs a positive check
  (decode sizes match, content-type matches) rather than an absence of errors.
- **`grep -r` does not follow symlinks, so the origin sweep can lie.** build.py
  symlinks `cdn/` into each variant directory, so a recursive grep over the page
  dirs covers markup only and reports a clean 0 while mirrored bundles still
  reference — or assemble — live URLs. Sweep the asset directory explicitly, and
  treat `performance.getEntriesByType('resource')` filtered to non-origin
  entries as the authority: a grep cannot find a URL a bundle builds at runtime.
  Seen on onefin, where a mirror reporting "0 origin refs" was loading an iframe
  from framer.com on every page.
- **Strip a framework's editor/analytics bootstrap at the module level, not just
  the tag level.** Removing `<script src="…/edit/init.mjs">` does nothing when a
  bundle contains `await import('https://framer.com/edit/init.mjs')`. Because it
  is awaited at module top level and its result is consumed
  (`{default: createEditorBar()}`), deleting the import rejects the module and
  takes the surrounding lazy factory with it — point it at a local stub whose
  export returns a component rendering `null`. Seen on onefin.
- **When an animated region caps a diff, measure one side against itself at two
  different waits.** Capturing the mirror at 12s vs 13s reproduced the exact
  reference-vs-mirror score on a scrolling marquee band (98.07% vs 98.02%),
  while two mirror captures at the same wait scored 99.84% against the
  reference's own 99.79% ceiling. Two screenshots separate animation phase from
  replication error, and turn "probably just the animation" into a measurement.
  Seen on onefin; supersedes eyeballing a diff map for motion residuals.
- **Framer is now characterised — but two of the "constants" were only priors.**
  Across three captures, these hold: breakpoints are always
  `0–809 / 810–1199 / 1200+`; root font-size is a flat 16px with no fluid driver;
  colour tokens are UUID-named so the values are the system and the names carry
  nothing; `@font-face` is in inline `<style>`; and the *bulk* of motion runs
  through the bundled Motion library as `type="framer/appear"` payloads.
  **Two claims made from the first two captures did not survive the third**
  (onefin), and both were generalisations from N=2:
  *"zero CSS easing"* — onefin ships `cubic-bezier(.44,0,.56,1)` 45 times, and it
  is the same curve as its one appear-tween's ease, so a Framer site can have a
  real CSS motion signature. Always tally rather than assume.
  *"`.98` fractional edges"* — onefin emits integer edges (`max-width:809px`,
  `max-width:1199px`) 145 times each *alongside* the `.98` forms (50). A missing
  `.98` is not evidence a site is not Framer.
  Read this as the standing caution: a two-site pattern is a hypothesis, and the
  entry that breaks it is worth more than the two that built it. Framer also
  registers metric-compatible "… Placeholder" faces, which are not a mirroring
  artifact but *will* make a naive font A/B report `differs: false` for a family
  that is genuinely loaded — probe the display face, where the gap is obvious.
  Reusing the hardened Framer build on a second site scored 99.37% against a
  99.46% ceiling on the first attempt, versus a multi-round debug on the first.
- **Serve mirrors with a server that honours `?range=a-b` AND `?range=a-b,c-d`.**
  Framer's CMS loader slices data chunks with a *query parameter*, not the HTTP
  `Range` header, and validates the response length. Python's `http.server`
  ignores it and returns the whole file, so the loader throws `Unexpected
  response length`, which Framer treats as fatal and tears the rendered tree down
  to an empty shell. It races the rest of the render, so it looks intermittent —
  headless captures can pass while the interactive page collapses. Critically the
  loader also issues **multi-range** requests (`?range=12650-18880,25241-31599`,
  comma encoded as `%2C`) and expects the concatenation of every slice; a handler
  that honours only the first pair fails exactly the same way, and only on the
  pages whose collections are big enough to be split. One page measured **9.76%**
  against a 99.93% ceiling from this alone while its 20 siblings sat at 99.7%+.
  Ship a `serve.py` that handles both forms with any Framer mirror.
- **Never neutralise links to `href="#"` on a Framer site — use `#inert`.**
  Framer's anchor component calls `document.querySelector(href)`, and
  `querySelector('#')` raises `SyntaxError: '#' is not a valid selector`. On at
  least one page that throw stopped the component tree rendering entirely. Any
  valid-but-unmatched selector works and is equally dead as a link target. This
  is a self-inflicted wound from the standard mirroring recipe, so it is worth
  checking on every framework that treats `href` as a selector.
- **One bad page hides behind a good mean.** A 21-page run averaged well while a
  single page sat at 9.76%. Always print the per-page table and flag outliers
  against each page's own ceiling; never report only an aggregate.
- **CMS collections come in `-chunk-`/`-indexes-` pairs and only one name is a
  literal.** The sibling is built by runtime substitution, so a scan finds one and
  the loader 404s on the other, rendering the collection empty with no error.
  Derive the sibling from every chunk found; a derived name that 404s upstream is
  expected and harmless.
- **A sitemap can list pages no crawl reaches, and a crawler can silently drop
  real ones.** Paginated indexes hide entries from link-following, and the
  bundled `AUTH_PAT` treats `/projects/` as an account area — correct for app
  dashboards, wrong for a portfolio, and it dropped 5 case studies as
  "auth-gated". Always set-difference the crawl against `/sitemap.xml` and read
  the skip reasons before trusting a page count.
- **Server-rendered does NOT mean script-independent.** The `curl`-and-grep test
  in mirror.md tells you the *markup* is there; it cannot tell you the markup is
  *visible*. Framer server-renders everything and then hides most of it, revealing
  it from its own runtime — scripts stripped measured 73.4% against 98.5% scripted
  on the same page. Always shoot the static variant once before assuming it is the
  safe default; the gap, not the stack, decides.
- **Never rewrite a URL that is used as a `new URL(rel, base)` base.** A base must
  be absolute, so relativising it throws `TypeError: Failed to construct 'URL'`,
  and one uncaught error in a framework bundle takes down the whole render. The
  failure mode is badly misleading: images and layout boxes paint normally while
  **all text disappears** and every counter/clock freezes at its initial value —
  it reads like a font or CSS fault and is neither. When the base sits in a
  template literal, inject `${location.origin}` to keep it absolute with no
  hardcoded port. Seen on createstudio (Framer CMS chunks).
- **Inside module bodies, rewrite to root-absolute (`/cdn/x`), never `./x`.** The
  same URL string is resolved against the *module* when it is an import specifier
  and against the *document* when it becomes a DOM `src` at runtime. `./` is
  correct for one and 404s at the site root for the other; `/cdn/` is correct for
  both.
- **Follow relative dynamic imports, not just absolute CDN urls.** Bundler chunks
  reference each other as `import('./X.mjs')`, which a host-based scan cannot see.
  Resolve relative specifiers against each module's own origin URL and iterate to
  a fixed point.
- **Truncate a captured URL at its first valid extension**, rather than stripping
  trailing punctuation. The stop-character rule in crawl.md is necessary but not
  sufficient: asset urls inside CSS custom properties in inline `<style>` blocks
  are followed by `);--next-prop:…`, and `;`/`:`/`-` are not stop characters, so
  the match runs into the next declaration and no amount of trailing-strip
  recovers it. Seen on createstudio.
- **A doubled DOM node count means hydration did not complete**, not that the
  mirror is broken. Framer emits every breakpoint variant server-side and switches
  them with `display:contents`/`none`, so the un-hydrated tree is ~2× the hydrated
  one (13,228 vs 7,042). Compare node counts across reference and mirror early;
  it is a fast, cheap hydration check.
- **Framework globals often come from the analytics script you correctly removed.**
  `__framer_events` and friends are set by `events.framer.com`, not by the app
  bundle, so their absence on a mirror proves nothing about whether the runtime
  booted. Check for loaded module count or rendered output instead. Corollary:
  neutralise tracker scripts by deleting the tag, not by pointing `src` at
  `about:blank` — that raises `ERR_UNKNOWN_URL_SCHEME` and pollutes the console
  you are trying to read.
- **The in-app browser pane is not a measurement instrument.** It rendered a fully
  black frame for a page that headless CDP captured correctly at 64% non-black
  pixels. Screenshot through CDP for anything you intend to reason about; use the
  pane only for interaction.
- **A production bundle's licence comments lie about its stack.** landonorris's
  bundle name-drops gsap.com and rive.app, but `window.gsap` and
  `window.ScrollTrigger` are undefined — the motion is CSS transitions plus a
  hand-rolled renderer. Confirm libraries by probing globals, not by grepping
  strings. Related: dat.GUI shipped hidden in production and inflated the
  hover-rule tally 3×; filter debug-tool selectors out of any state census.

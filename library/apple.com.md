# apple.com

**Callable as: Apple** (aliases: apple.com, apple)

Apple's global marketing homepage and top-level product pages. Captured
2026-08-03 @ 1440×900. Stack: server-rendered, hand-built (no detectable
framework signature — no React/Vue/Framer globals, no build-tool query params).
**Mirror path**, static (scripts stripped).

## Type — SF Pro, two roles, no fluid driver

`SF Pro Display` for headlines (56px/60 line-height on the hero H2, weight 600),
`SF Pro Text` for everything else (12–21px, weights 400/600). Both are Apple's
own system faces, served locally via `@font-face` — not a Google Fonts or
Adobe Fonts dependency. Root font-size is a flat value, no `vw`-clamped fluid
driver (contrast with the Framer sites in this library, which mostly use one).
72 face variants load on the live reference across nav, footer and interactive
states; a static mirror loads 18 — the two families agree on both sides, which
is the actual font-gate condition, not the face count.

## Layout

1440px+ desktop breakpoint captured. Hero content is centered, ~570px measure
for the primary headline block. Sections are full-bleed, alternating flat
background colors (`#f5f5f7`-class greys) with occasional light-blue gradient
bands between product sections — confirm exact tokens on a full breakpoint
pass; only the primary width was measured this round.

## Colour

Near-black text (`rgb(29,29,31)`) on light grey/white surfaces. Accent blue for
CTAs (`Shop` pill button). Restrained palette — no bold hero background colours
observed on this pass; product photography and the signature "cutout" halftone
illustration style (dot-pattern die-cut photos, seen on the back-to-school
promo) carry most of the visual interest instead of the palette.

## Motion

**Motion fidelity: partial**

43 animations measured via `motion-extract.js` (two-phase capture, hooks
installed before load). By kind: 28 `CSSTransition`, 15 `CSSAnimation`. Durations
by frequency: **1000ms ease-in-out ×20** (hero/section fades), 320ms ×12 across
two curves (`cubic-bezier(0.4,…)` and `linear`, both used for UI-state
transitions), 250/400ms minor. Only **1 of 43** animations fired scroll-triggered
— this homepage's motion is almost entirely load-time and interaction-driven,
not scroll-choreographed, a real contrast with every Framer/marketing-site
entry elsewhere in this library.

The one named component-level system found: the **global nav search overlay**
(`globalnav-searchresults`) stages its result list in on a **20ms per-item
stagger**, `cubic-bezier(0.4,…)` @ 320ms. This is the richest single mechanism
on the page and it is interaction-gated (fires when a visitor types a query),
not part of the passive homepage experience.

`prefers-reduced-motion`: **absent** on the live reference. Notable given
Apple's public accessibility position — worth re-checking on a future capture
in case it is conditionally injected by a script this pass didn't trigger.

No per-animation spec table yet — this entry is `partial`: real curves and
durations, no target/trigger/from-to mapping. Promote to `spec` with a full
`motion-diff.py`-verified pass before building motion from this entry by name.

## Interaction states

Not captured this pass (no dedicated hover/focus sweep run). Add on a future
capture.

## Template taxonomy (multi-page crawl)

Scoped crawl, 30 of 846 sitemap pages — see gotcha below for why 30, not more.

| Template | Instances | Fixed | Varies |
|---|---|---|---|
| Product marketing page (Mac, iPad, iPhone, Watch, Vision Pro, AirPods, TV) | 7 | Global nav, footer, hero-then-feature-sections structure | Hero copy, feature count, media type (video vs photo) |
| Shop/buy configurator (`shop/buy-*`) | 5 | Same nav/footer shell | Product options, price panel |
| Accessory/compare/specs sub-pages | ~10 | Table-driven layout | Row count, comparison targets |

## Gotchas hit while rebuilding

1. **Sitemap seeding order starves a scoped crawl of its own nav breadth.**
   `crawl.py`'s default sitemap seeding queues all 846 sitemap URLs
   *alphabetically*, and they sit in the queue ahead of the homepage's own
   extracted nav links (FIFO — sitemap seeding happens before the homepage's
   own links are appended). A capped scoped crawl (`--max-pages 26`) burned
   its entire budget on `accessibility/*` and `airpods-*` query-string variants
   before reaching Mac/iPhone/Watch at all. **Fix:** run with `--sitemap ""` for
   a scoped homepage crawl — pure breadth-first from the page's own nav order,
   which is what "the design surface" actually means for a site this size.
   Verify by checking page 2–5 of the crawl log are real top-level nav targets,
   not alphabetically-early sitemap noise.
2. **`srcset` was harvested for fetching but never rewritten for serving — a
   real bug, now fixed in `scripts/build.py`.** Every `<picture><source
   srcset="...">` still pointed at the origin's root-relative path after the
   build, even though `harvest()` correctly fetched the referenced assets into
   `cdn/`. Symptom: three real photographs in the homepage hero rendered as
   blank grey boxes. The reason it's silent: a `<picture>` element does **not**
   fall back to its `<img>` when the `<source>` it selected 404s — fallback
   only triggers when no `<source>` matches the media query at all. So the
   failure looks like a missing-image bug, and the actual asset is sitting
   right there in `cdn/`, just never pointed at. Fixed with a dedicated
   `srcset`-list rewrite pass (comma-separated candidates, each with an
   optional `Nx`/`Nw` descriptor to preserve) and covered by 4 new assertions
   in `scripts/tests/test_build.py` using this exact `<picture>`/root-relative
   shape. Re-verify on any future capture: `grep -c '/v/' site/*.html` should
   be 0, or the site-specific asset path prefix equivalent.
3. **A live geolocation banner adds real layout height and must be measured,
   not guessed.** Headless Chrome resolved to a Philippines IP and apple.com
   served a "Choose another country or region" banner absent from the mirror
   (correctly — it's server-driven and transient, the same class as a cookie
   banner). Guessing its height for the diff crop (74px) left enough residual
   ghosting to look like a real layout bug; measuring the actual banner height
   via a live CDP box-geometry query on a stable heading (**70px**, confirmed
   because font/color/width/height were otherwise pixel-identical) resolved it
   immediately. Lesson generalizes: always measure the crop offset from a
   live DOM query, never estimate it from a screenshot by eye.
4. **The homepage's below-the-fold content appears to vary between separate
   page loads.** Two live CDP queries for the same landmark text, seconds
   apart, returned different DOM neighborhoods (footer-nav headings vs.
   content headings at the same viewport position) — consistent with real
   session-to-session personalization/promotional rotation, the same
   mechanism serving the geolocation banner. A pixel diff residual in the
   footer transition band (54.73% within-16 vs. 94–99% elsewhere) was
   **not resolved** and is recorded honestly rather than claimed fixed; a
   second reference capture in the same session would confirm whether it is
   personalization or a genuine mirroring defect.
5. **No JS framework globals, no build-tool fingerprint.** Confirmed by
   probing runtime globals rather than grepping bundle comments (this
   library's standing rule): no `window.React`, no Vue, no Framer-style
   content-hash class names. Apple's frontend appears to be a hand-built,
   heavily componentized system (`globalnav-*`, `-elevated`, `-flyout`
   naming) rather than a framework output.

## Verification achieved

Whole-page pixel diff (1440×900, banner-cropped by measured 70px): **98.32%
similarity, 88.45% within 16/255** — clears the similarity floor, just under
the within-16 target. Region-split: photo band (the srcset fix) **99.99%/
99.94%**; nav+hero text 96.66%/94.57%; footer transition band 97.12%/54.73%
(unresolved, see gotcha 4). Font gate: families agree (SF Pro Display, SF Pro
Text) on both sides, `zeroFaces: false` both. Motion gate: **fails**, entirely
on the interaction-gated search overlay (see Motion section) — homepage
content motion (1000ms fades, 320ms UI transitions) reproduces correctly.
Copy/SEO/GEO gate (`--match`, captured copy never rewritten): **passes** on
homepage and `/mac/`; real `Organization`/`WebSite`/`WebPage`/`Brand` JSON-LD
present — one of the few references in this library shipping real structured
data. Assets: 5725/5800 mirrored (75 failures: Apple Pay favicons, ~10 Apple
Music thumbnails, one stray non-asset URL — none on the design surface
crawled). Scope: 30 of 846 sitemap pages (bulk excluded and quoted: 140 legal,
127 locale variants, 94 education, 79 feedback, 51 business).

# framer.media (homy.framer.media)

**Callable as: Homy** (aliases: homy.framer.media, framer.media, homy)

Real-estate marketing template — property listings, detail pages, buy/rent
services, testimonials, FAQ. Captured 2026-08-10 @ 1440x900 (crawl + scripted
mirror; also spot-checked @ 1280x800; motion not separately captured this
pass — see fidelity note).
Stack: Framer (SSR + React hydration, bundled Motion library, `rolldown`
runtime chunks). **Mirror path**, scripted (`crawl.py` + `build.py`), 21/21
pages, 371 assets, 0 external requests after cleanup.

## Type — two families, one workhorse

- **Switzer** carries essentially the whole UI: nav, body copy, buttons, card
  titles, FAQ — 71 of 74 counted `font-family` declarations on the homepage.
- **Special Gothic** appears 3 times only — a display-only accent face,
  consistent with this library's standing "serif/display-only" pattern (here a
  geometric display sans instead of a serif, but the same discipline: a second
  face earns its keep only at a handful of high-impact spots).
- Root font-size is the flat Framer default (no fluid-rem driver observed on
  this site, unlike landonorris/onefin).

## Layout

- **Breakpoints: 0–809.98 / 810–1199.98 / 1200+**, integer+`.98` edges — this
  is now the *fourth* Framer capture in this library confirming the same
  triad (youtube isn't Framer; createstudio/osa/onefin/homy all are).
  Framer emits one full SSR variant per breakpoint gated by
  `hidden-<hash>` classes, so expect ~3x the "real" DOM node count.
- Multi-page site: home, about-us, contact-us, privacy-policy,
  terms-of-service, a `properties` listing, and **15** individual
  `properties/<slug>` detail pages — all nav-reachable, all mirrored (no bulk
  section to scope down; sitemap listed 22, one 404'd `/404` page correctly
  excluded).

## Colour

Fully **achromatic** — no accent color anywhere in the 10 distinct
`--token-*` custom properties sampled:

| Role | Value |
|---|---|
| Ink (primary dark) | `rgb(8, 11, 15)` (also seen as `rgb(11, 17, 23)` in one variant) |
| White | `rgb(255, 255, 255)` |
| Pure black | `rgb(0, 0, 0)` |
| Grays (borders/surfaces) | `rgb(199,199,199)` · `rgb(245,245,245)` · `rgb(238,239,240)`/`rgb(246,246,246)` · `rgb(75,91,99)` |

A CTA-button or accent color would be the obvious place to introduce one and
the template deliberately doesn't — worth reusing this restraint on an Adapt
build from this entry rather than defaulting to a brand accent.

## Motion

**Motion fidelity: none** — not separately captured this pass (`motion-extract.js`
was not run); this entry cannot license building motion without a fresh
capture. One mechanism *was* identified empirically while debugging a stuck
section, recorded here as a signature-only observation, not a spec:

- The page runs **Lenis** (confirmed via `<html class="lenis">`), a
  virtualized smooth-scroll library. At least one hero-adjacent text band
  ("Focused on discovery…") scales from 12px → 54px as a function of Lenis's
  own internal scroll progress, not the native `scroll` event.

## Gotchas hit while rebuilding

1. **Synthetic `window.scrollTo()` does not drive Lenis-owned scroll effects.**
   Step-scrolling a mirror with `page.evaluate('window.scrollTo(...)')` (the
   standard fix for the library's own documented IntersectionObserver-miss
   gotcha) correctly revealed every IO-gated section but left one Lenis-driven
   scale-text effect frozen at its 0% state (12px instead of 54px) even after
   a full top-to-bottom sweep. Fix/verify: drive real `page.mouse.wheel(0, dy)`
   events instead of `scrollTo` for any page confirmed to carry `class="lenis"`
   on `<html>` — wheel events land on Lenis's own listener and update its
   virtual position; `scrollTo` doesn't. Confirmed live: 12px before, 54px
   after switching to wheel events on the same page.
2. **A live analytics tag can be an *async* tag build.py's asset pass never
   touches.** `<script async src="https://events.framer.com/script?v=2">`
   survived the mirror untouched — it's a bare external `<script src>`, not a
   `url()`/asset reference build.py's rewrite pass looks for. Grep every
   mirrored page for the site's own analytics domain before calling a build
   clean; don't assume "0 origin refs in the asset scan" covers script tags.
3. **Framer's hydration reverts *static text nodes* you edited in place, not
   just components.** This is a step beyond what this library already knew
   (that Framer re-renders hidden content from its own runtime): editing the
   served HTML's `<title>`, a `meta[content]`, or even an ordinary footer
   `<p>` (a contact email) is not durable — Framer's bundle sets these from
   page-config data baked into its own JS at mount, independent of the HTML
   it hydrates against, and silently overwrites the edit within the first
   render pass. Confirmed live with a raw-HTML vs. live-DOM diff: served HTML
   read the corrected string, `document.title` read the original. Fix: don't
   rely on a static edit for anything Framer might treat as page metadata;
   guard it with a live corrector instead (next gotcha).
4. **A MutationObserver-based text corrector must scope to the mutation
   records, never re-walk the whole document.** First version called a
   full-document `TreeWalker` inside the observer callback on every mutation;
   this page has live count-up/countdown elements that mutate text every
   animation frame, so the callback fired dozens of times a second and each
   one re-scanned the entire DOM. Measured effect: `page.goto()` with
   `wait_until: 'load'` timed out at 30s (never fired) with the naive
   version, and completed in under a second once the callback was rewritten
   to only inspect `mutation.target`/`mutation.addedNodes` from its own
   records. A full sweep is fine at fixed points (init, `DOMContentLoaded`,
   `load`); it must never live inside the observer's own callback.
5. **Anything inserted *inside* `#main` (Framer's hydration root) gets wiped
   on mount if it doesn't match Framer's own render output — including a
   plain `<canvas>`, not just text.** Confirmed with React error #418
   (hydration mismatch) the moment a hand-authored Three.js canvas was
   inserted as a child of `<main id="hero">`. This generalizes the library's
   existing "redefine the svg def, don't touch the `<use>` site" logo lesson
   to injected content generally: build anything new as a sibling *outside*
   `#main` (this site's `#svg-templates` container is one confirmed-safe
   landing spot, sitting immediately after `#main` closes) and self-position
   it against the target element's `getBoundingClientRect()` instead of
   relying on DOM nesting for placement.
6. **A sibling of a `position:static` ancestor can still lose a z-index fight
   to a `position:sticky` descendant inside it, in practice, against the
   plain CSS2.1 painting-order reading.** The new canvas sat as a sibling of
   `#main` with `z-index:0`; `#main` itself is `position:static`, so by the
   spec's painting order (step 3, in-flow non-positioned content, before
   step 6, positioned z-index:0 siblings) the canvas should have painted on
   top of everything in `#main` regardless of what's nested inside it. It
   didn't — `#hero` (`position:sticky`, Framer's own `z-index:1`, nested well
   inside `#main`) painted over it every time, confirmed with a zoomed
   screenshot in a real GPU-accelerated browser (not just a headless one —
   see the false lead below). Fix: give the sibling a z-index that beats the
   *page's* highest relevant z-index directly (`2` here), not `0` — don't
   trust that a non-positioned ancestor "contains" its positioned
   descendants' stacking for the purpose of a fight against an outside
   sibling.
   - `document.elementFromPoint()` is **not evidence either way** for this
     kind of check if the element in question has `pointer-events:none`
     (as any purely-decorative overlay should) — it performs a hit-test,
     which skips non-interactive elements entirely regardless of visual
     paint order, so it will report the same "element underneath" result
     at z-index 0 and at z-index 999999 alike. Diagnose actual paint order
     with a screenshot (zoomed into the exact region), never with
     `elementFromPoint`, whenever `pointer-events:none` is in play.
   - A red herring worth recording precisely because it looked so
     convincing: `renderer.info.render.calls/triangles/points/lines` were
     all correctly non-zero and a same-task `gl.readPixels()` (with
     `preserveDrawingBuffer: true`, since the default `false` clears the
     buffer before a *later* separate `evaluate()` call can read it) showed
     real drawn color/alpha — strong, correct evidence the GL layer itself
     was rendering — and headless Playwright's `page.screenshot()` still
     showed nothing, which pattern-matched this library's existing
     "the in-app browser pane isn't a measurement instrument" finding
     closely enough to nearly get written up as a second confirmed instance
     of it. It wasn't: the *same* real GPU browser that finally revealed the
     globe also showed nothing at `z-index:0`, and correctly showed it the
     moment the z-index changed. API-level rendering evidence is real
     evidence that the GL layer works — it is not evidence about *paint
     order relative to other page content*, which is a separate question
     answerable only by looking at (or hit-testing correctly around) the
     actual composited page.
7. **A correct `href` does not stop Framer's own client router from
   hijacking the click.** build.py rewrote every internal link's `href`
   correctly (confirmed: "Explore Homes" → `href="properties.html"`), but
   clicking it still did a client-side `pushState` to the site's *original*
   pretty URL (`/properties`, no `.html`) and left `#main` nearly empty —
   there's no backend here to resolve that route. Reported live by the user
   as "buttons go to a blank page." Fix: a capture-phase `document` click
   listener (`addEventListener('click', fn, true)`) that resolves the
   nearest `<a>`'s real `href`, calls `stopImmediatePropagation()` to keep
   Framer's bubble-phase handler from ever seeing the event, and forces
   `window.location.href` instead. Applies to every mirrored Framer page,
   not just this one — worth promoting to a general mirror-hardening step
   in `build.py`/`references/mirror.md` rather than a per-site patch next
   time this comes up on a second Framer capture.
8. Also reported live in the same pass: the giant **"Made in Framer"**
   free-plan badge (`#__framer-badge-container`, fixed bottom-right,
   `z-index: calc(var(--infinity,2147480000))`) survives the mirror and
   reads as obviously wrong on a rebranded site — remove the div outright
   rather than hide it with CSS (its `pointer-events:none` doesn't stop it
   from being visually present). And the hero globe (gotcha 6) initially
   spun with unbounded acceleration under mouse movement: the tilt term was
   added directly to `rotation.y` every frame (`+= targetTiltY * 0.4`)
   instead of eased toward it like `rotation.x` was — an uncapped per-frame
   velocity term. Fix: ease every rotation component toward a target every
   frame, never add a raw pointer-derived value as a velocity.
9. **CMS collection chunk/index `.framercms` files 404 as usual** (23 of 371
   assets) — the library's existing `-chunk-`/`-indexes-` pairing gotcha,
   unremarkable here since all property content was already server-rendered
   into the static HTML; the client-side collection loader failing to
   re-fetch doesn't blank anything visible.

## Template taxonomy

| Template | Instances | Fixed | Varies |
|---|---|---|---|
| Property detail | 15 | Hero image, price, sq ft, gallery layout, CTA | Address, photo set, description |
| Marketing page | 5 (home/about/contact/privacy/terms) | Nav, footer | Section composition |
| Listing | 1 (`properties`) | Filter/grid chrome | Card count (15) |

One property-detail page plus the homepage captures the full system; the
other 14 detail pages are template repeats with no new design information.

## Verification achieved

Full 21-page mirror served locally, 0 external requests, 0 console errors
after the hydration-guard/analytics fixes above. Text/brand-swap verified
against the **live DOM** (not just served HTML) via Playwright, including a
sweep for residual case-insensitive brand mentions (0 found outside an
intentional build-attribution comment). The Three.js hero globe (gotcha 6)
is confirmed visually correct in a real GPU-accelerated browser after the
z-index fix — a zoomed screenshot shows the wireframe globe and pulsing
pins clearly composited behind the hero headline on a fresh page load, not
just under a live debugging patch. No pixel-diff run against the reference
this pass (rebrand target, not a pure Match) — Motion fidelity above is
`none` for the same reason: prioritized the rebrand + hydration correctness
work over a full motion-spec capture.

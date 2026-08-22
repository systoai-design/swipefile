# threeui.com

**Callable as: ThreeUI** (aliases: threeui, three ui, designcode threeui, @designcodeio/threeui)

**This entry is a different kind of thing from every other one in the library — read this paragraph before using it.** Every other entry measures one live site's design system by capture, because the values have to be re-derived (the reference's assets aren't ours to use). ThreeUI is the opposite case: it's an MIT-licensed (Community tier), npm-installable **component source**, explicitly built "for agents" ("Copyable as prompts" is the site's own tagline). There is no single Type/Layout/Colour/Motion system to measure — it's 220 independently-authored components, each its own micro-system, and the actual source code is legally reusable, not just informative. Treat this as a **donor catalog**, not a site to Match or Adapt.

Surveyed 2026-08-21 via the public GitHub repo (`MengTo/threeui`, MIT, 1112 stars) — README, file tree, and full source read for several components. Live `/browse` gallery structurally read (220 components, category filters: Landing Pages, Hero, Three.js, Backgrounds, Buttons, Text Animation, UI Elements, CSS, Motion Design, Sections) but **not visually screenshotted** — the in-app Browser pane hit this library's own documented "pane is not a measurement instrument" failure (`computer{screenshot}` errored "not displayed, so the page is not compositing frames"). Evidence here is source-level, not pixel-level; a future pass through CDP/headless would add the visual side.

## What it actually is

- **Stack**: React + Three.js + TypeScript + Vite. Install: `npm install @designcodeio/threeui`, then `import { AtTheHorizon } from "@designcodeio/threeui"`.
- **License**: MIT for application code and every Community-tier component. Bundled fonts under SIL OFL 1.1. **Pro and Beta components are excluded from the public repo** — only Community-tagged results on the site are actually in the GitHub source / npm package. Don't try to source a Premium-tagged component from the repo; it isn't there.
- **Scale**: 50 Community parent components, 111 routes, 164 browseable results. The full commercial catalog (220, including Premium) is larger than what's redistributable.
- **Shape on disk**: `src/package-components/*.ts` (the published, importable components — `AtTheHorizon`, `BrandOrbs`, `CloudField`, `DotMatrixBackground`, `FlowField`, `GenerateButton`, `LiquidMetalButton`, etc.) and `src/shaders/<name>/` (one self-contained `.html` + a React `.tsx` wrapper per effect — `liquid-metal-button`, `condensation`, `energy-orb`, `globe`, `dot-matrix`, `ribbon-field`, `portal-field`, `fluid-field-background`, `koi-studies`, and more).

## Structural patterns worth naming

Read one component's full source (`LiquidMetalButton.tsx` + its `liquid-metal-button.html`) end to end. Three techniques generalise well beyond this one component:

- **Explicit-clock scrubbing instead of a free-running `requestAnimationFrame` loop.** The shader HTML exposes `window.__seek(v)` — external code sets the clock value and the component renders that exact frame, rather than ticking its own rAF internally. **This is the same seek-safe/deterministic-render discipline HyperFrames' own `THREEJS-PATTERN.md` had to hand-roll for the Systo video builds** (a WebGL scene must be keyed off the timeline's own seek, never an independent clock, or an arbitrary-timestamp screenshot/render shows the wrong frame). Independent confirmation, in unrelated production code with no connection to HyperFrames, that this is the correct pattern for any embeddable/scrubbable Three.js component — worth citing directly if `hyperframes-keyframes` or a future video build needs to justify the approach to someone unfamiliar with why a plain rAF loop is wrong here.
- **iframe + `postMessage` config bridge.** Each shader effect ships as a self-contained HTML document (its own `<canvas>`, its own inline WebGL/GLSL, zero React/build-tool coupling) and is configured post-mount by posting a message into the iframe (`{ liquidMetalButton: { text, pillWidthUnits, embedded } }`). This isolates the heavy WebGL runtime completely from the host page's bundle and DOM — genuinely easy to drop into any stack (a Framer mirror, a Next.js site, a plain static page) regardless of what that stack's own JS framework is, since the component never touches the parent's React tree at all.
- **One reference-unit variable drives the whole component's scale**, exactly the `--u` pattern already in this library from Sylva (`library/sylva.md`) — a second, independent confirmation of "one fluid constant pinned to an explicit reference measurement" in completely unrelated production code. Here: `--h` is the one ergonomic knob (button height), and every other dimension is `calc(N * var(--u))` where `--u: calc(var(--h) / 516)` — 516 being the reference artwork's own measured height. Change `--h`, the whole button rescales losslessly.
- **Physically-reasoned shadow/glow layering, explained in comments, not tuned by eye.** `LiquidMetalButton`'s CSS comments justify each shadow layer by what it represents physically ("A shadow needs something to fall on: a soft ambient pool lifts the ground just off black", "deepen it while the metal is lit, so the bright face keeps its edge") — the same why-not-what comment discipline this project holds code to, applied to visual design decisions. Worth modeling future glassmorphism/metal/glow work on this reasoning style rather than a flat "looks about right" value.

## Notable components by category (non-exhaustive, from the Community tier)

- **Buttons / interactive**: `LiquidMetalButton` (pill / circle / play variants, colored or monotone rendering), `GenerateButton`, `DotBorderButton`, `CircleButtons`, `FloatingDotsCta`.
- **Backgrounds / fields**: `FlowField`, `DotMatrixBackground`, `CloudField`, `BellFieldBackground`, `FluidFieldBackground`, `ElementsBackground`, `EmeraldHorizonBackground`, `CondensationBackground`, `CrtBackground`, `DimensionalField`, `ExpanseField`, `RibbonField` (shader dir), `PortalField` (shader dir).
- **Data / abstract 3D**: `ConstellationField`, `ConnectivityGraph`, `DataField`, `DiagnosticsPanel`, `DefenseLines`, `EnergyOrb` (shader dir), `Globe` (shader dir).
- **Character / showcase**: `CharacterCarousel`, `CharacterFilmstrip`, `CharacterWave`, `BallStudy`, `ClothStudy`, `BookshelfScene`, `Gallery`.
- **Brand / identity**: `BrandOrbs`, `AudioWordmark`, `EngravedCertificate`, `AtTheHorizon`.

Category filters on the live browse grid (`/browse`) — useful search terms when looking for a donor by job rather than by name: Landing Pages, Hero, Three.js, Backgrounds, Buttons, Text Animation, UI Elements, CSS, Motion Design, Sections.

## Motion

**Motion fidelity: none**

Not "unmeasured" in the usual sense — the gate's four-value scale (`spec` /
`partial` / `signature-only` / `none`) is for *measured* motion on a site
whose animation has to be re-derived from a live capture. `none` is the
correct, honest value here, and `motion-spec.py`'s refusal to build from it is
correct behavior too: this entry never stood in for measuring, because the
actual source (every tween, easing, and timing constant) is directly readable
in the repo and importable via the npm package. There is nothing to
re-measure and nothing this entry could hand `motion-spec.py` as a mapping.
**Do not re-capture this "site" to try to promote it to `spec`** — read the
specific component's own source before using it, the same as reading any
other dependency's code.

## What this entry is good for

The first place to check — before hand-authoring a CSS/SVG approximation or reaching for a generic gradient — whenever a brief's ambition reads as "premium," "wow," or calls for a specific expressive 3D/WebGL moment (a hero background, an animated button, a data-visualization field, a brand mark reveal) and the register isn't obviously served by the site's own existing system. Pairs with the "wow ambition" check in `SKILL.md` alongside Sylva: Sylva shows *that* a bespoke three.js register can carry a whole page with zero DOM color; ThreeUI supplies actual, licensed, ready components to build that register from, in minutes rather than from scratch.

Poor fit for: anything that needs to match an *existing* brand's measured system exactly (this is a donor catalog, not a brand system — see `references/adaptation.md`'s ownership line before landing one of these components into a client build with no license/attribution check), and anything where the "wow" budget doesn't justify a real WebGL dependency (bundle size, GPU cost) over a cheaper CSS effect.

## Gotchas hit while surveying

1. **The in-app Browser pane could not screenshot or composite this page** — same documented failure as everywhere else in this library (`computer{screenshot}` → "the Browser pane is not displayed, so the page is not compositing frames"). Used `read_page` (accessibility tree) plus the GitHub REST API and raw `githubusercontent.com` file fetches instead. If a future job needs actual pixel screenshots of a specific component's live render (not just its source), route through CDP/headless per this library's standing rule, not the pane.
2. **`/browse` redirected to `/` in the pane's navigation** — the site is a client-rendered SPA; the route resolved fine (page title and content matched `/browse`'s content) but the tab's reported URL didn't update. Not investigated further since source-reading answered the actual question; worth knowing if a future capture pass tries to script navigation by URL rather than by clicking.
3. **Only Community-tagged results are real for sourcing purposes.** The live grid interleaves Community and Premium/Beta labels in the same list (e confirmed via `read_page`, e.g. "Sylva — Living Green... Community component" next to "Sylva — Sakura Sunset... Premium component") — don't assume every visually-similar result is available in the public repo just because a sibling variant is.

## Verification achieved

Source-level only: README claims cross-checked against the actual repo file tree (component/shader directory listings via the GitHub Contents API) and one full component read end-to-end (`LiquidMetalButton.tsx` + `liquid-metal-button.html`, 895 lines) to confirm code quality and extract the structural patterns above. Not verified: visual rendering quality of any component (screenshot capture failed, not retried through CDP), whether every category-filter count on the live site matches the repo's actual file count, and the exact terms/pricing of the Premium tier (irrelevant to this entry, which only concerns the redistributable Community tier).

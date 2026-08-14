# Taste — the design loop for work we author

Match has a target to diff against, so Step 4 can measure it: same boxes, same
pixels, same motion. **Adapt, Brand, and any original build have no such
target.** Nothing in the fidelity report applies, and historically that meant
the build shipped on an adjective — "looks good" — which is precisely the
handover the report exists to replace.

This file is the loop for those builds. It has two halves, and the split is the
whole point: what can be measured is measured, and what cannot is sent to
someone who did not write the page.

---

**Which taste skill?** `design-taste-frontend` is the hub, and `design-stack`
decides what else loads beside it. That matters here because several installed
packs claim the same job and two of them contradict the hub outright — a build
that loads `gpt-taste` alongside it is built to two motion doctrines. Route
first, then apply the precedence below.

## 1. Where the taste rules and the measured reference meet

An Adapt build carries a reference's *system*. It does not carry everything —
the reference does not dictate the copy, the CTA labels, the form states, the
sections it does not have. **Every gap gets filled with a default, and the
defaults are the problem.** A build can carry a reference's proportions
faithfully and still ship Fraunces, an AI-purple gradient and three equal
feature cards in the space between them.

So a taste skill governs the gaps. Precedence, in order:

1. **A measured value from the reference wins** wherever the reference has one.
   A captured `cubic-bezier(.22,1,.36,1)` @ .3s is not replaced by a house
   default spring, and an `8.3333vw`-against-1440 type scale is not replaced by
   `text-4xl md:text-6xl`. The measurement is the reason the capture happened.
2. **The taste rule wins wherever the reference is silent.** Type pairings,
   icon family, empty and error states, section rhythm the reference had no
   equivalent of, copy register — all house rules.
3. **The taste skill's hard bans win always, over the reference itself.** WCAG
   contrast on every CTA and form control, `prefers-reduced-motion`, a hero that
   fits its viewport, a nav on one line. Reference sites break these constantly.
   An Adapt build is the user's own site, shipped publicly under their name; a
   Match is a local study that is never published. That difference is what makes
   the bans non-negotiable here and inapplicable there.

**Match takes none of this.** Match copy is captured verbatim and rewriting it
to satisfy a house rule breaks the Step 4 diff outright — `design-gate.py --mode
match` exempts the copy checks for that reason and says so in its own output.

## 2. Dials from measurement, not from vibes

A taste skill sets dials (variance / motion / density) from the brief. When the
brief names a reference — a URL, or an entry by name from `library/INDEX.md` —
those dials have measured values available and should not be guessed:

| Dial | Read it off |
|---|---|
| `MOTION_INTENSITY` | the entry's motion signature: animation count, duration ladder, travel distance. A page whose reveals travel 5px over .3s is not a 9. |
| `VISUAL_DENSITY` | measured section padding and content-per-viewport from the capture. |
| `DESIGN_VARIANCE` | the layout-family census across sections — how many distinct structures the reference actually uses. |

A named reference resolves through the library with no capture at all, subject
to the `Motion fidelity:` rule in SKILL.md — **below `spec` the entry cannot
carry motion**, so either re-capture it (Step 1 + Step 2, motion only) or say in
one line, up front, that the build ships without it.

The failure this replaces: a design read that says *"leaning toward a
Linear-style minimalist language"* and then builds from a recollection of
Linear. That is the same failure Step 1 exists to prevent, arriving through the
brief instead of through a URL.

## 3. The loop

```
build  →  design-gate.py  →  fix FAILs  →  re-gate  →  fresh-eyes critique  →  fix  →  report
```

Two rounds usually converges. Stop when the gate is clean and the critique has
nothing structural left — not when the page looks fine to you, which is the
judgement the next section exists to route around.

### Gate A — mechanical

```bash
python3 design-gate.py http://127.0.0.1:8791/ --mode adapt --src ../src --out design.json
```

It drives the same headless-Chrome instrument as every other measurement here
(`cdp-run.py`), at 1440 and 390 by default, and returns pass / FAIL / WARN /
UNVERIFIED per check. It measures what a self-review reliably gets wrong:
composited background colours behind translucent surfaces, real contrast ratios,
button labels that wrap, the eyebrow census against its own budget, painted vs
merely-declared font families, the light/dark sequence across sections, the
radius and accent censuses, and the source-level rules the rendered page cannot
show (`h-screen`, scroll listeners, icon family).

Three properties it inherits from the gates already in this folder:

- **UNVERIFIED is never a pass.** No `--src` supplied means the source rules
  were not checked, and the row says so rather than going quiet.
- **Warnings do not block.** Checks whose measurement is a heuristic — the hero
  visual, duplicate CTA intent, a single deliberate theme switch — report and
  let you decide. Say what you decided. A gate that fires on a legitimate build
  is a gate that gets ignored, and then the failures go unread too.
- **A passing row never carries a violation in its detail.** Enforced by a test,
  because the first version of this gate printed `ok — no prefers-reduced-motion
  rule anywhere in the page CSS`.

Feed the JSON into the report so the design gate sits beside the fidelity ones:

```bash
python3 report.py --site mysite.com --mode adapt --path rebuild \
    --design design.json --motion motion.json --copy copy.json --measured measurements.json
```

### Gate B — fresh eyes

**The half the gate cannot see, and must not pretend to.** Nothing mechanical
can tell you whether the copy reads like an LLM trying to sound thoughtful,
whether each animation is motivated, whether the composition is derivative, or
whether the whole thing reads as templated. Those are the failures that actually
make a page feel like AI output.

They are also the failures the author is worst placed to catch. Self-grading in
the same context is the weakest form of review: the model defends what it just
wrote, and every rule it followed feels like evidence that the result is good.

So this half goes to a **subagent that never watched the build happen**. Give it
only:

- the rendered screenshots at 1440 and 390,
- the rendered text (`design.json` carries it, or take it from the page),
- the brief in one line,
- and nothing else — no reasoning, no rationale, no "here's why I chose this".

Ask for a scored critique against the taste skill's judgement rules — visual
hierarchy, copy quality, motion motivation, whether it looks templated, what a
skeptical designer would say first. The `critique` skill covers this if it is
installed; without it, the prompt is the ask above plus "name the three things
you would change first, in priority order."

The rationale-withholding matters. Supplying the reasoning is how you get a
reviewer that agrees with the reasoning instead of looking at the page.

## 4. What neither gate covers

Say these out loud rather than letting the pass imply them:

- **Whether the design is right for the brief.** Both gates check execution. A
  beautifully executed page for the wrong audience passes everything here.
- **Content truth.** Fake-precise numbers, invented claims, wrong product facts.
  `copy-gate.py` catches AI-writing tells and the SEO floor; neither gate knows
  what is true.
- **Real-device rendering.** Two viewports in headless Chrome is not a device
  matrix. This library has twice measured a browser pane disagreeing with CDP
  about the same page — the instrument is not the last word on what a person
  sees.
- **Anything at a viewport you did not pass.** The gate measures where it is
  pointed. `--width` is repeatable.

And the standing rule from SKILL.md applies to the number this loop produces:
**say "reported", not "verified", while any check is UNVERIFIED.**

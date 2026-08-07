# The content layer: copy, SEO, GEO

The skill measures design to the pixel and, until this file, said nothing about
the words. A page can diff at 99%, carry the signature curve, pass the font gate,
and still read like a machine wrote it, ship no `<title>`, and be invisible to
the engines that increasingly decide what gets cited.

`scripts/copy-gate.py` is the mechanical half. This file is the judgement around
it: who owns the copy, where the rewrite guidance lives, and what a page has to
state to be quotable.

## 1. Who owns the copy — settle this before anything else

Copy ownership follows the job, and the two cases are opposites. Conflating them
is the sharp edge of this whole file.

**Match — the copy is the reference's, captured verbatim, and is never
rewritten.** Not improved, not tightened, not "humanized", not corrected. Text is
data already in the DOM and it is captured programmatically in either path
(mirror or hand-rebuild). Rewriting it corrupts the replication and destroys the
verification: every changed string changes text wrap, box height, and every
position below it, so the Step 4 diff can never converge and the similarity
number stops meaning anything. This is the same defect class as placeholder text,
listed under "The fidelity bar for Match" in `SKILL.md`, and it arrives dressed
up as helpfulness rather than laziness, which is why it survives review.

`copy-gate.py --match` skips the prose checks for exactly this reason, and prints
a note saying it did.

**Adapt, Brand, and from-scratch — the copy is newly written, therefore ours,
therefore checked.** This is the only path where the prose gate applies. In the
two-URL Adapt form the copy is the *user's own*, crawled from their site; that is
still not the reference's copy, and anything you write to bridge the gap is yours
and gets checked with the rest.

| Job | Copy source | Prose gate | SEO / GEO gate |
|---|---|---|---|
| Match | Captured verbatim from the reference | **Never** — `--match` | Reported; see below |
| Adapt (brief) | Newly written for the user's subject | Yes | Yes |
| Adapt (two-URL) | The user's own, plus anything new you write | Yes, on what you wrote | Yes |
| Transfer | Whatever the user's page already says | Untouched unless they ask | Their page, their call |
| Brand / from-scratch | Newly written | Yes | Yes |

The failure this table prevents: a Match gets "helpfully" reworded on the way
past, and an exactly verifiable build becomes an unverifiable one. Nobody notices
until the diff refuses to converge and the cause is three steps back.

**Match mode still reports SEO and GEO, and can still exit 1 on them** — a
reference with two `<h1>`s or no meta description hands its defects to the
mirror. That output is a fact about the reference, not a defect in your copy of
it. Do not fix it. Adding a JSON-LD block or an invented `alt` string to a mirror
is a deviation from the reference markup, and `references/report.md` counts
unexplained markup changes as a gate failure. Record it in the report's honesty
rows instead.

## 2. Prose — detection here, judgement in `humanizer`

The rewrite guidance already exists and is not duplicated here. The `humanizer`
skill (`~/.claude/skills/humanizer/SKILL.md`, 622 lines, 33 numbered categories,
no scripts) holds it: what each tell is, why it reads as machine-written, and
before/after pairs for fixing it.

The split is deliberate:

- **`copy-gate.py` detects.** Only the mechanically detectable subset — ten of
  humanizer's categories, matched by regex against the page's visible text. Every
  finding is labelled with that skill's own heading number so it routes straight
  to the fix.
- **`humanizer` judges.** Everything the regexes cannot see: rule-of-three
  cadence, copula avoidance, elegant variation, sycophancy, manufactured
  punchlines, whether the writing has a pulse at all.

**Load `humanizer` before writing shipping copy, not after.** A skill read after
the words exist means rewriting the words, and rewriting always keeps more of the
original shape than starting from the guidance would have. Same rule as every
other skill in the routing table.

What the gate actually watches, with the budget each category is allowed. A
category fails only when occurrences **exceed** its budget — the budgets are
there because one em dash is punctuation and one "crucial" is a word, while six
of one and fourteen of the other is a tell:

| humanizer category | Budget | Fails at |
|---|---|---|
| 7 AI vocabulary (delve, leverage, seamless, robust, curated, myriad…) | 6 | 7+ |
| 4 promotional language (world-class, unparalleled, best-in-class…) | 2 | 3+ |
| 5 vague attribution (experts say, studies show, it is believed) | 0 | 1+ |
| 3 superficial -ing analysis (", highlighting…", ", underscoring…") | 2 | 3+ |
| 9 negative parallelism (not just, isn't merely, more than simply) | 1 | 2+ |
| 1 inflated significance (stands as a testament, marks a turning point) | 1 | 2+ |
| 12 false range ("from X to Y, ") | 3 | 4+ |
| 18 emoji | 1 | 2+ |
| 19 curly quotes | 40 | 41+ |
| 14 em-dash density | `max(2, words/150)` | above that |

The prose pass runs on **visible text only**. HTML comments, `<script>`,
`<style>`, `<svg>` and `<noscript>` are stripped first, because a build's own
design notes sitting in `<!-- -->` are not copy, and counting them produces
phantom findings about text no reader ever sees.

**The honest baseline: on the two builds measured when this gate was written, the
classic tells scored at or near zero.** The prose was not the problem. That is
worth stating plainly, because it says where the real gap was — not in the
adjectives, but in the layer below: no structured data, thin specifics, SEO
essentials left to chance. Do not read a clean prose pass as a clean content
layer.

## 3. SEO essentials

Presence checks, and the gate distinguishes what breaks a page from what merely
weakens it. Failures exit non-zero; warnings never do.

| Check | Severity | Why |
|---|---|---|
| `<title>` present | **FAIL** | It is the page's name everywhere it is listed. Absent means the browser and every index invent one. |
| `<title>` 15–65 chars | WARN | Under 15 says nothing; over 65 gets cut mid-phrase in results. |
| Meta description present | **FAIL** | Absent means the snippet is scraped from whatever text happens to be first. |
| Meta description 70–165 chars | WARN | Same truncation logic, wider window. |
| Exactly one `<h1>` | **FAIL** | Zero leaves the page's subject unstated; more than one leaves it ambiguous. This is a document-structure error before it is an SEO one. |
| `lang` on `<html>` | **FAIL** | Screen readers pick pronunciation from it, and translation and indexing both key off it. One attribute. |
| `<link rel="canonical">` | WARN | Cheap insurance against the same page being counted twice under query strings. |
| `og:title`, `og:description`, `og:image` | WARN | These are what a shared link looks like. Missing means the unfurl is whatever the scraper guesses. |
| `alt` on every `<img>` | **FAIL** | Accessibility first, indexing second. An image with no alt is invisible to a reader who cannot see it. |

An `alt` is a failure when the attribute is **absent**. `alt=""` is a valid,
deliberate answer for decorative images and passes — say nothing about an image
that says nothing.

## 4. GEO — generative engine optimisation

The part nothing else in this skill covered, and the part with the worst measured
record: **structured data was absent on 2 of 2 measured builds.**

Generative engines lean on JSON-LD to work out what a page is about and whether
it can be cited with confidence. A page without it is not penalised so much as
unreadable in the way that matters: everything it claims is prose the engine has
to infer, and inference loses to a page that simply declared it.

**The floor for a business page:** `Organization` or `LocalBusiness`, plus
`WebSite`. Add `BreadcrumbList`, `FAQPage`, `Product` / `Offer` where the content
genuinely supports them.

**Never fabricate a schema the page does not back up.** No `FAQPage` for
questions the page does not answer, no `Product` with an invented price, no
`AggregateRating` at all unless real ratings exist. Invented structured data is a
lie told to a machine that will repeat it, at scale, with the page's name
attached. It is also the one defect here that survives every visual check.

The gate parses each `application/ld+json` block and lists the `@type`s it found
as a note; a block that does not parse is a warning, because malformed JSON-LD is
read by nothing and is worse than none — it looks done.

Three things beyond the markup, and they are writing decisions, not tagging ones:

1. **Concrete figures, dates and named entities are what gets quoted.** "Batch
   0412 charged at 195C, first crack at 9:05" is quotable; "expertly roasted" is
   not. The gate warns when fewer than 1% of a page's words are numeric — a blunt
   proxy, deliberately blunt, and it fires on exactly the pages that have nothing
   specific to say.
2. **Headings should answer real questions.** A heading that states the question
   a reader actually asked gives an engine a retrievable unit. A one-word section
   label gives it nothing to anchor to.
3. **State facts, not adjectives.** "Open Wednesday to Sunday, 7am to 2pm, at
   1841 SE Division" survives being extracted and repeated. "Unparalleled
   experience" does not survive being read.

Note the overlap: point 3 is also humanizer category 4. Promotional language and
unquotable copy are the same defect seen from two sides, which is why one clean
pass does not excuse the other.

## 5. The gate

```bash
python3 copy-gate.py index.html            # Adapt / Brand / from-scratch
python3 copy-gate.py index.html --match    # captured copy: SEO/GEO only, prose skipped
python3 copy-gate.py index.html --json     # same findings, machine-readable
```

Exit **0** when there are zero failures, **1** when there is at least one.
Warnings and notes never change the exit code — a gate that cries wolf gets
ignored, which is the failure the whole file exists to prevent.

Output is three tiers: `note` (what was found, including the JSON-LD types and
the Match-mode skip), `WARN` (weakens the page, does not fail it), `FAIL` (the
gate). Prose findings are sorted by count, worst first, and are followed by a
routing line naming `humanizer` as the place to fix them.

**Where it sits:** after Step 3, before you show the user anything.

- **Adapt / Brand / from-scratch** — run it clean before the feel-check in
  `references/adaptation.md`. Fix prose findings by loading `humanizer`, not by
  deleting the offending word and moving on.
- **Match** — run it with `--match` alongside the report gates. Findings describe
  the reference; carry them into the report's honesty rows rather than editing
  the mirror.

`scripts/selftest.py` covers it: a deliberately sloppy fixture must fail on named
categories, and a clean fixture must pass with zero prose findings. Both
directions matter — a gate that misses obvious slop is useless, and a gate that
fails clean copy gets switched off.

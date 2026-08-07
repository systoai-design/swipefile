# swipefile

A Claude Code skill that captures a reference website's design system — layout,
tokens, typography, interaction states, animations — verifies it by measurement,
and remembers it in a local library that compounds with every site it studies.

`SKILL.md` is the procedure and is the file Claude reads. This README is for the
human installing it.

## Install

Clone into your Claude Code skills directory:

```bash
git clone <your-remote> ~/.claude/skills/swipefile
```

The folder is self-contained and framework-neutral: plain Markdown plus plain
Python. Nothing in the workflow requires a particular agent harness.

## Requirements

| For | Needs |
|---|---|
| Everything except live capture | Python 3.9+, standard library only |
| Driving a real browser (`cdp-run.py`, the `motion` and `font` suites) | Google Chrome or Chromium, plus `pip install websockets` |
| The Playwright capture path (`capture.py`) | `pip install playwright && playwright install chromium` |

Both browser-dependent test suites **skip cleanly** when Chrome or `websockets`
is missing, so the suite is green on a bare machine — it just verifies less.

## Verify the install

```bash
python3 scripts/selftest.py
```

Ten suites, no network and no downloaded fixtures: each stands up a synthetic
origin, runs the real script against it, and asserts on the artifacts. Every
case corresponds to a failure measured on a real capture, so a pass means the
engine still does the thing that was paid for.

```bash
python3 scripts/selftest.py serve     # one suite
```

## The gates

Each is an instrument rather than a paragraph, because this project has measured
that written rules get quoted back correctly while being skipped.

| Command | Refuses |
|---|---|
| `python3 scripts/library-lint.py` | a library entry the resolver would silently mis-read |
| `python3 scripts/motion-spec.py --name X` | building motion from an entry that never measured it |
| `python3 scripts/copy-gate.py page.html` | AI-writing tells, missing SEO, absent structured data |
| `python3 scripts/motion-diff.py ref.json build.json` | a build whose motion does not match the reference |
| `python3 scripts/report.py --measured m.json` | calling a replication done on numbers nobody read |
| `python3 scripts/package.py` | shipping anything the machine captured |

## Your library is yours

`library/` accumulates what this installation has measured, one entry per site.
It is knowledge — ratios, curves, breakpoints, mechanisms — and never contains a
site's copy, imagery, or assets.

**It is also a record of what you have studied.** If you publish this repository,
publish it from `scripts/package.py`, which builds a distributable with the
library reset to an empty scaffold and refuses to write the archive if a captured
entry, a mirror artifact, or a build product is anywhere inside it:

```bash
python3 scripts/package.py            # -> dist/swipefile/ and dist/swipefile.skill
python3 scripts/package.py --verify dist/swipefile
```

A private repository syncing your own machines is a different case — there the
library travelling with you is the entire point.

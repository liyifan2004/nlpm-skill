# Contributing

## Two kinds of files

Generated, do not edit by hand:

- `skill/references/<name>/SKILL.md` and the files under
  `skill/references/<name>/references/`
- `skill/scripts/nlpm-check.py`
- `skill/references/INDEX.md`
- `UPSTREAM_FILES.txt`

They come from `tools/build.py`. A change to the rules belongs upstream at
https://github.com/xiaolai/nlpm.

Authored here and open to edits:

- `skill/SKILL.md`, `skill/references/workbuddy.md`
- `skill/scripts/discover.py`, `vague-scan.py`, `history.py`, `recalibrate.py`
- `tools/`, `tests/`, `docs/`, `.github/`, and the repository metadata

## Local workflow

```bash
git clone https://github.com/xiaolai/nlpm .cache/upstream
python tools/build.py --upstream .cache/upstream
python -m unittest discover -s tests -v
python tools/pack.py
```

`tools/build.py --check` compares generated files against the pinned upstream
commit without writing anything. CI runs it on Linux and Windows.

## Before opening a pull request

1. Keep the tests passing on Python 3.11+.
2. If you change a scoring rule, update `docs/design.md` and
   `skill/references/workbuddy.md` too.
3. Add a line to `CHANGELOG.md` under the unreleased heading.
4. Use Conventional Commits for the subject, for example
   `fix: count example blocks outside fenced code`.
5. Do not bump `UPSTREAM_PIN` in the same commit as a feature change.

Contributions are accepted under the ISC License in `LICENSE`.

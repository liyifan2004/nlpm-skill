# Design

## The question

Can a Claude Code plugin be turned into one portable Agent Skill without
losing what it does? This repository is the working answer. The phrase "what
it does" has to be split before it can be measured.

## Three layers

1. **Content.** The 100-point rubric, the 50 rules, the writing guides, the
   standalone validator. Format-independent, copied verbatim. No loss.
2. **Orchestration.** Twelve commands that dispatch eight subagents.
   Replaced by one five-step workflow plus four scripts. Output is the same;
   entry points and parallelism change.
3. **Host runtime.** Slash-command namespace, PostToolUse hooks, marketplace
   versioning. The skill format has no slot for these. This is the only layer
   with real loss.

Calling the whole port lossy because of layer 3 is as inaccurate as claiming
zero loss by ignoring it. The split is the answer.

## Component mapping

| Upstream | This project | Loss |
|---|---|---|
| 17 knowledge skills, scoring tables | `references/` | none |
| `bin/nlpm-check` | `scripts/nlpm-check.py` | none |
| 12 slash commands | `SKILL.md` workflow | `/nlpm:*` entry point |
| 8 subagents | `discover.py`, `vague-scan.py`, `history.py`, `recalibrate.py` + host model | parallelism depends on host |
| PostToolUse hook | pre-commit / CI, optional host hook | in-session reminder |
| trend state, config, reports | `history.py`, `templates/` | none |
| manifest, namespace, marketplace | optional thin host shell | automatic updates |

Mechanical work moved out of the model. Upstream itself notes that a
deterministic grep counts vague quantifiers more reliably than a heuristic
agent, so this part of the port is more predictable than the original.

## Why two deliverables

One universal skill is the trunk. It runs anywhere that reads Agent Skills.
A thin host shell is added only where the host has commands, hooks and a
plugin system; it forwards to the same workflow and adds no rules of its own.
The trunk does not depend on the shell, and the shell does not fork the
rubric. This is the structure that satisfies both portability and the full
host experience. Port Master's `full` and `nested` modes and the cc2agy
bridge take a similar direction; both stop at format conversion and leave
host-specific scoring out.

## Scoring profile

Upstream scores by artifact type. A few rows in its Skills table are Claude
Code conventions written as universal rules. On a 319-artifact WorkBuddy
corpus, R06 hit 297 skills for `-10` each because they had no `<example>`
block; the mean was 75.0 and no file could exceed 90. Removing that one row
gave a mean of 84.3 and cut files below 70 from 83 to 18.

The profile is recorded as data, not decided per run:
`references/workbuddy.md` lists which rules apply and why, and
`scripts/recalibrate.py` recomputes findings under a named profile. R01's
mention-versus-use exclusion still needs a per-line reading; the script
flags high-hit files instead of changing their score.

## Role of the scoring tests

Running the skill against a real skill corpus checks three things: the rubric
loads in a host, the scripts produce reproducible counts, and findings can be
recomputed from a profile. That is verification. The scores of a personal
skill collection are test fixtures, not the product, and a second scoring run
is not a product iteration by itself.

## Open items

- The optional host shell is not built yet.
- `discover.py` classifies by path pattern; it does not read host specs.
- `recalibrate.py` does not re-judge R01; a per-line reviewer is still needed.
- Upstream has no WorkBuddy tier. `references/workbuddy.md` fills the path
  and rule gaps, and should grow into a full scoring reference file.

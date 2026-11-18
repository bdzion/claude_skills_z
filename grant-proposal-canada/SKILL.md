---
name: grant-proposal-canada
description: Plan, draft, review and check research funding proposals for Canadian and international funders — Mitacs (Accelerate, Elevate), NSERC (Discovery, Alliance), SSHRC, NFRF, OMAFA and other provincial programs, private foundations, and international development funds — including logic models, objectives and work plans, partner contributions and benefits, training of highly qualified personnel, EDI, knowledge mobilization, budgets and justifications, risk registers, reviewer-criteria mapping, and compliance with section limits. Use whenever the user is writing or revising a grant, proposal, letter of intent, concept note for a funder, or responding to a funding call, even if they only paste one section.
---

# Grant proposals (Canadian funders)

Reviewers score what the call asks for, in the call's own terms. A proposal wins when every
evaluation criterion has a clearly labelled, evidence-backed answer, the work plan is
credible for the budget and team, and the text respects every limit.

## Workflow

1. **Get the current rules first.** Open the funder's official program page and
   instructions for this competition (web search or the user's PDF) and record the URL and
   access date. Page and word limits, eligible costs, partner cash ratios, deadlines and
   criteria change between competitions; never state them from memory. If the official
   source cannot be reached, say so and leave the limit as a placeholder.
2. **Build the criteria map** with [references/structure.md](references/structure.md):
   one row per evaluation criterion, the section that answers it, the evidence used, and
   gaps. Show it to the user before drafting long text.
3. **Draft section by section** from the logic model (problem → objectives → activities →
   outputs → outcomes → impact). Keep objectives measurable and tie each to work-plan
   activities, milestones, people and budget lines.
4. **Write in the user's voice.** For prose that will go out under Dr. Bodrud-Doza's name,
   apply the bodrud-doza-scholarly-voice skill; for text co-written with Evan Fraser on
   food systems, the evans-writing skill. When editing the user's own text, change grammar
   and clarity only and show every change.
5. **Check compliance** with `scripts/compliance_check.py draft.md limits.json` (copy
   `assets/limits_template.json` and fill it from the official instructions), then run
   the review checklist in [references/structure.md](references/structure.md).

## Standing rules

- Never invent numbers: budgets, partner contributions, prior funding, outcomes or
  citations come from the user or a checked source. Mark gaps as `[TO CONFIRM]`.
- Separate established evidence (cited), contested points, and the team's own proposal.
- Partner-funded programs (e.g. Mitacs, NSERC Alliance): state what the partner
  contributes (cash, in-kind, data, expertise) and what the partner gains, in terms the
  partner would use. Do not overstate commitments the partner has not confirmed.
- Training (HQP), EDI and knowledge mobilization are scored sections, not boilerplate:
  give concrete activities, numbers and timelines.
- Canadian spelling, unless the funder's own template uses another convention.

---
name: food-system-stress-test
description: Design, model and communicate food-system stress tests and anticipatory action — defining shocks (animal disease, fertilizer and phosphate disruption, cold-chain cyberattack, trade restrictions, climate extremes), mapping how they propagate through supply-chain nodes and buffers, comparing early versus delayed responses, estimating avoidable disruption and losses with explicit assumptions, building shock registers and early-warning indicators, and turning the results into concept notes, pitch text, briefing notes and dashboard or demo specifications for government and funders. Use whenever the user works on food-system resilience, shocks, buffers, absorptive capacity, early warning, anticipatory action, scenario what-ifs or a food-system risk dashboard, even if they only ask for "a one-pager" or "a demo".
---

# Food-system stress testing

A stress test asks: if this shock happened, where would the system break first, how long
would buffers hold, and how much disruption would acting earlier avoid? Its value to
decision-makers comes from making those mechanics visible and the assumptions checkable.
False precision destroys that value, so every number is labelled sourced or illustrative.

## Workflow

1. **Frame the decision.** Who decides what, and when? A stress test is useful when it
   informs a choice (stockpile, pre-position, trigger a response, invest in redundancy).
   Write the decision question before the scenario.
2. **Write a shock card** for each shock using
   [references/shock-card.md](references/shock-card.md): trigger, onset speed, duration,
   first node hit, propagation path, buffers, early signals, decision points, response
   options and their lead times.
3. **Build the propagation sketch**: nodes (production, processing, storage and cold
   chain, distribution, retail and food service, households), dependencies, and buffer
   sizes in days of demand. Name the data source for each parameter or mark it as an
   assumption.
4. **Run the early vs delayed comparison** with `scripts/shock_scenarios.py` (copy
   `assets/example_poultry_disease.json` and replace its placeholder numbers). Report
   avoided shortfall by response start day, the shape of that curve, and its sensitivity
   to the least certain parameters (buffer sizes, severity, response magnitude). A
   non-monotonic curve is a finding: some responses carry their own costs when started
   too early.
5. **Translate to decisions**: what signal would trigger action, how much lead time it
   gives, and what is lost per week of delay, in the units decision-makers use (tonnes,
   days of supply, households affected, CAD), with ranges.
6. **Communicate** using [references/communication.md](references/communication.md) for
   concept notes, briefing notes, pitches and dashboard specifications.

## Ground rules

- **Label every number.** "Illustrative" (assumed to show mechanics), "sourced" (with
  citation or dataset), or "estimated" (from a stated model with uncertainty). The script
  prints ILLUSTRATIVE unless the scenario file says every parameter is sourced.
- **Separate three layers** in any write-up: established findings (cited), contested
  questions (say who disagrees and why), and the project's own inference or proposal.
- **Signals are not forecasts.** An early-warning indicator raises the probability of a
  shock or shows a buffer thinning; say what it does and does not predict.
- **Concepts with a literature behind them** (resilience, vulnerability, buffers,
  absorptive and adaptive capacity, cascading risk) are defined in
  [references/concepts-and-sources.md](references/concepts-and-sources.md); use those
  definitions and cite them rather than inventing new terms.
- **Canadian context**: check the current mandate and programs of the relevant agencies
  (e.g. AAFC, CFIA, Public Safety Canada, Global Affairs Canada) from their official pages
  before describing them; do not describe programs from memory.
- For prose in the user's own voice, apply the bodrud-doza-scholarly-voice skill; for
  food-system papers and public pieces, the food-system-scholarship-writing or food-system-scholarship-public-writing skills.

## Model limits to state

The bundled model is a fixed-proportion, single-commodity flow with daily steps: no
prices, trade substitution beyond what a response adds, behavioural change, or spatial
detail. It is a teaching and scoping tool for the logic of buffers and timing. For
published estimates, use or build an empirical model (input-output, network, agent-based
or system dynamics) calibrated to Canadian data, and say which.

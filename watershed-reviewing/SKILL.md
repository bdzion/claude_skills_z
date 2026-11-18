---
name: "watershed-reviewing"
description: "Use when reviewing a watershed modelling or management draft; returns a scorecard and ranked, located critiques with concrete fixes (calibration, scale, lags, targeting, decision relevance), not a rewrite."
---

# Watershed Reviewing: critiquing watershed modelling and management drafts

This skill reviews Dr. Bodrud-Doza's drafts the way a rigorous referee for *JGLR*, *J. Environ. Manage.*, *JAWRA*, *ERL* or a *Nature*-family journal would. It applies the conceptual lens and conventions of the corpus behind `watershed-writing`:
- the Yang lineage (Guelph);
- the Basu group (Waterloo);
- the vulnerable-waters and wetlandscape consortium (Creed, Lane, Thorslund).

It diagnoses; it does not rewrite. The review is an in-house critique, not the opinion of any corpus author.

The companion skill `watershed-writing` holds the full lens:
- Section 2: conceptual commitments.
- Section 3: architectures A–F.
- Section 5: conventions.
- Section 9: corpus with DOIs.

The checklists below are self-sufficient if that skill is not loaded.

---

## 1. Ground rules

1. **Read the whole draft before commenting**, including tables, figure captions and supplementary material if supplied. Read attached files in full.
2. **Diagnose, don't rewrite.** Preserve the author's voice. Line edits appear only if the user asks. They are limited to grammar and clarity unless he asks for more, and are always shown as *Original | Suggested | Reason*.
3. **Be direct about weaknesses in reasoning and method.** Do not soften a Major issue into a suggestion. Where a concern is a judgement call, say so.
4. **Calibrate to paper type and journal.** Don't demand a Nature-style "Here we" opening from an applied modelling paper, or a full calibration section from a perspective piece.
5. **Never invent citations or values.** Recommend only literature whose details are certain, with a DOI. Otherwise write `[needs source: topic]`. Use `citation-check` if the user wants references verified.
6. **Separate claim status.** Tag each key assertion as **established**, **contested** or **author inference**. Flag any place where an inference or a modelled projection is written as an observed fact.
7. **Use Canadian spelling** in the review. Note spelling and terminology inconsistencies in the draft, unless the journal's style differs.

---

## 2. Setup

State in one line at the top of the review:
- **Paper type.** A: model application or scenarios. B: data-driven analysis. C: meta-analysis. D: framework or review. E: perspective or policy. F: decision-support tool. Use "other" if none fits.
- **Target journal and stage.**
- **Central claim**, restated in one sentence. If it can't be restated, that is Major finding #1.

---

## 3. Review passes

Run every pass and record each problem with its location (section, paragraph, line, or figure/table number).

### Pass 1: Framing and architecture
- Does the introduction narrow from the societal problem to the process to the specific gap to the purpose?
- Is the gap concrete ("prior models did not simulate nutrient retention in riparian wetlands")? Is the gap more than "few studies have"?
- Is prior work organized by approach or direction rather than listed author by author?
- Is there an explicit purpose or "Here, we" statement with objectives, and does the conclusion answer each one?
- Is the policy or management context named (agreement, target, agency program), with a year?
- Does the section order fit the paper type and journal?

### Pass 2: Conceptual lens (diagnostic questions)
1. **Pathways and connectivity.** Does the draft say which pathway (surface runoff, tile drainage, groundwater, channel) carries each constituent, and when? Are connected and disconnected features treated differently where it matters?
2. **Scale and aggregation.** Is the leap from field or site to watershed justified? Are combined BMP effects treated as non-additive? Are cumulative effects of small features addressed?
3. **Shape of response.** Is the response linear, accelerating, decelerating, a threshold or hysteresis? Is the shape characterized, or only the endpoint magnitude?
4. **Legacies and lags.** Are stored nutrients and expected lag times considered when interpreting results or setting expectations for targets?
5. **Seasonality and climate.** Are non-growing-season processes and event-dominated export addressed? Are climate projections handled with ensembles, defined periods and scenario pathways?
6. **Attribution.** Are climate and human drivers separated? Is the attribution method (nested watersheds, controls, multivariate models) adequate for the claim?
7. **Variability.** Are ranges, distributions and source/sink switching reported, not just means or medians? Is bias in the evidence base acknowledged?
8. **Targeting and cost-effectiveness.** Are effects given per unit area? Are priority areas identified from process-based effect per unit rather than simple totals? Are costs or trade-offs considered where the paper makes management claims?
9. **Decision anchor.** Is at least one key result translated into decision terms, such as share of a load-reduction target, treatment-plant equivalence or cost?
10. **Policy realism.** Are protection and restoration distinguished? Are options presented with their trade-offs? Is "do nothing" treated as a choice with consequences?
11. **Stakeholders** (types E and F especially). Is co-development described? Is usability evaluated, and is stakeholder criticism reported honestly?

### Pass 3: Modelling and data rigour (types A, B, F; adapt for C)
- **Setup.**
  - Model name and version, with the source and resolution of the DEM, soils, land use and climate.
  - Management inputs (crop rotation, fertilizer and manure rates and timing, tillage, tile drainage extent and parameters, reservoirs, wetlands, point sources).
  - Model adaptations (for example, for Canadian conditions, frozen soils or wetland modules), justified and tested.
- **Process representation.** Are the processes that drive the result represented (saturation-excess runoff, tile flow, snowmelt and frozen soil, wetland–channel exchange, legacy P)? If not, is that a stated limitation?
- **Calibration and validation:**
  - warm-up, calibration and validation periods stated and independent;
  - stations listed, with multi-site or multi-variable calibration where data allow;
  - parameters and ranges reported, along with the calibration tool;
  - both statistical and graphical evaluation;
  - performance by season and flow regime, especially winter and spring high flows;
  - evaluation criteria stated before results and cited.
  Check the claims against the standard the manuscript cites. For example, Moriasi et al. (2015) judge watershed-scale flow simulations "satisfactory" when daily, monthly or annual R² > 0.60, NSE > 0.50 and PBIAS ≤ ±15%. Constituent-specific criteria differ, so check the ones used against the source.
- **Uncertainty.** Are parameter and input uncertainty and scenario uncertainty quantified or at least bounded (for example, an ensemble spread or prediction band)? Are model results described as projections, not observations?
- **Scenario design:**
  - a clear baseline;
  - realistic extents and placement;
  - BMP representation justified (which parameters changed and why);
  - individual and combined scenarios;
  - a scenario table.
  Are climate scenarios bias-corrected or downscaled, with the method stated?
- **Statistics** (types B and C). Are the trend tests, attribution models and their assumptions (autocorrelation, multicollinearity, spatial dependence) appropriate? Are the meta-analysis inclusion criteria, effect metrics and heterogeneity reported?
- **Reproducibility.**
  - Data and code availability, with DOIs or repositories.
  - CRS, units, time steps and aggregation stated.
  - Python or R scripts commented, if code is shared.

### Pass 4: Results and interpretation
- Are concentration, load and yield kept distinct? Are flow-weighted values defined?
- Does each percentage carry its baseline, with the absolute value alongside?
- Do the figures (study-area map, calibration hydrographs, scenario bars, response curves, spatial maps, seasonal panels) support each claim, with legible units?
- Is each key result explained by a mechanism? Are untested mechanisms framed as hypotheses?
- Are results checked against independent observations or literature?
- Do the conclusions stay within what was modelled or measured, with no generalization beyond the watershed, period or scenario set without justification?

### Pass 5: Limitations and next steps
- Are the limitations specific (which data, which process, which parameter, which monitoring would help) rather than generic ("models have uncertainties")?
- Are monitoring needs (for example, edge-of-field or on-site wetland data) and model-development needs named?

### Pass 6: Prose and conventions
- Voice is consistent: "This study" with passive methods, or "Here, we" with active voice, not a mix.
- Terms are defined once and used consistently (BMP; vulnerable waters; size classes; seasons by month; scenario names).
- Units and notation are consistent: SI with explicit time base, and constituent notation (TP, TN, SS, NO₃⁻, PO₄³⁻/SRP/DRP).
- Paragraphs lead with a claim. No unsynthesized lists of studies or results.
- Hedging is calibrated to the evidence, and "demonstrate" is reserved for robust evidence.
- Spelling is Canadian, or the journal's style.

---

## 4. Severity

- **Major.** Undermines validity or the central claim. Examples:
  - inadequate or undocumented calibration or validation;
  - a missing process that drives the result;
  - unsupported attribution;
  - additive treatment of interacting BMPs;
  - projections presented as observations;
  - conclusions beyond the evidence;
  - no stated gap or purpose.
- **Moderate.** Weakens credibility or usefulness but is fixable without new analysis. Examples:
  - no per-hectare or decision-anchored results;
  - missing seasonal breakdown when the data exist;
  - generic limitations;
  - missing scenario table;
  - unclear baselines.
- **Minor.** Notation, consistency, spelling, figure legibility and prose.

Rank findings Major, then Moderate, then Minor. Within each tier, order them by the improvement each fix brings.

---

## 5. Output format

1. **Header.** Paper type, journal, stage and the central claim in one sentence.
2. **Verdict** (one short paragraph). What the draft shows, whether the evidence supports it, and the single most important fix.
3. **Strengths** (2–4 bullets).
4. **Scorecard.** Score 1–4 (1 = absent or problematic, 2 = partial, 3 = solid, 4 = exemplary), with a one-line justification each. Mark "n/a for type" where a dimension does not apply.

   | # | Dimension | Score | Justification |
   |---|---|---|---|
   | 1 | Framing: problem, gap, purpose | | |
   | 2 | Pathways, connectivity and process representation | | |
   | 3 | Scale, aggregation, non-additivity | | |
   | 4 | Response shape: nonlinearity, thresholds, lags | | |
   | 5 | Seasonality and climate handling | | |
   | 6 | Calibration, validation and uncertainty (or statistical rigour) | | |
   | 7 | Scenario or analysis design | | |
   | 8 | Spatial targeting, cost-effectiveness, decision anchoring | | |
   | 9 | Limitations, monitoring needs, reproducibility | | |
   | 10 | Structure, conventions, prose clarity | | |

5. **Ranked findings.**

   | # | Severity | Location | Issue | Why it matters | Concrete fix |
   |---|---|---|---|---|---|

   A fix must be actionable: say what to add, test, move, cut or report. Where a fix needs literature, give a verified reference with its DOI, or `[needs source: …]`.
6. **Claim-status flags.** Sentences where an inference or a projection reads as established, each with suggested hedging.
7. **Missing analyses or figures** that would most strengthen the paper (for example, seasonal performance table, response curve, per-hectare map, scenario table).
8. **Questions for the author** (3–6 pointed questions).
9. **Optional illustrative edits**, only if requested. At most three passages, shown as *Original | Suggested | Reason*.

Keep the review proportionate: about 1–2 pages for a section and 3–5 for a full manuscript.

---

## 6. Common red flags

- Calibration statistics reported only for the whole period, hiding poor winter or high-flow performance.
- The same period used for calibration and validation, or no validation.
- BMP effects summed across practices, or practices placed without regard to where they are effective.
- Percentage changes with no baseline or absolute value.
- "Wetlands remove P" stated without source/sink conditions or legacy-P caveats.
- Climate-change results from a single GCM, or without stating the scenario pathway and period.
- Attribution claimed from a correlation without controls.
- Field- or plot-scale effects extrapolated to the watershed without an aggregation logic.
- Results never connected to a target, cost or decision.
- Limitations that could apply to any model paper.
- Decision-support tools presented without user evaluation.
- Undefined acronyms, mixed units, and "modelling/modeling" inconsistency.

---

## 7. Model-evaluation references (verified)

- Moriasi, D.N., Arnold, J.G., Van Liew, M.W., Bingner, R.L., Harmel, R.D., Veith, T.L. (2007). Model evaluation guidelines for systematic quantification of accuracy in watershed simulations. *Transactions of the ASABE* 50(3): 885–900. https://doi.org/10.13031/2013.23153
- Moriasi, D.N., Gitau, M.W., Pai, N., Daggupati, P. (2015). Hydrologic and water quality models: performance measures and evaluation criteria. *Transactions of the ASABE* 58(6): 1763–1785. https://doi.org/10.13031/trans.58.10715
- Daggupati, P., Pai, N., Ale, S., et al. (2015). A recommended calibration and validation strategy for hydrologic and water quality models. *Transactions of the ASABE* 58(6): 1705–1719. https://doi.org/10.13031/trans.58.10712

---

## 8. Self-review use

When checking a draft written with `watershed-writing`, also confirm that:
- every `[CITE]` and `[VALUE]` placeholder is resolved with a verified source or still flagged;
- no sentence attributes findings to corpus authors beyond what their papers report.
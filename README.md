# claude_skills_z

Claude skills for research on agricultural watersheds, water quality, precision
conservation and food-system resilience, maintained by Md Bodrud-Doza (University of
Guelph). Each skill is a folder with a `SKILL.md` that Claude reads when a request
matches its description, plus scripts, reference notes and test cases where useful.

## Skills

| Skill | Use it for | Bundled tools |
|---|---|---|
| [water-quality-analysis](water-quality-analysis/) | Long-term tributary monitoring data: audits, loads, trends, censored values, ML with SHAP | `wq_trends.py` (Mann-Kendall, seasonal Kendall, Sen slope, Hamed-Rao), `wq_loads.py` (interpolation, FWMC, Beale) |
| [watershed-model-calibration](watershed-model-calibration/) | IMWEBs, SWAT and SWAT-CUP calibration, validation and BMP scenarios | `model_metrics.py` (NSE, KGE, KGE′, PBIAS, RSR, FDC biases, Moriasi ratings), `baseflow.py`, `bmp_scenarios.py` |
| [precision-conservation-gis](precision-conservation-gis/) | LiDAR terrain analysis, flow paths, critical source areas, BMP siting, Earth Engine cover and residue mapping | `terrain_targeting.py` (DEM checks + WhiteboxTools pipeline), Ontario CRS notes, GEE recipes |
| [food-system-stress-test](food-system-stress-test/) | Shock scenarios, early vs delayed action, avoidable losses, concept notes and dashboard specs | `shock_scenarios.py` (transparent propagation model), example scenario |
| [research-figures-maps](research-figures-maps/) | Publication figures and maps: hydrographs, FDCs, load-duration curves, obs vs sim, scenarios | `zfig.py` (house style and plot recipes) |
| [grant-proposal-canada](grant-proposal-canada/) | Mitacs, NSERC, SSHRC, NFRF, OMAFA and foundation proposals | `compliance_check.py` (section limits from current guidelines) |
| [manuscript-revision-response](manuscript-revision-response/) | Revise-and-resubmit rounds in Word: comment plan, triage, item-by-item changes, response letter | `parse_comments.py` (decision letter → numbered plan), `build_response_letter.py` (.docx letter) |
| [research-poster](research-poster/) | Conference posters as editable PowerPoint + PDF: takeaway, section plan, grid layout, checks | `build_poster.py` (JSON spec → .pptx, overflow and image-resolution checks, preview) |
| [watershed-writing](watershed-writing/) | Drafting watershed modelling and management manuscripts | — |
| [watershed-reviewing](watershed-reviewing/) | Scorecard reviews of watershed drafts | — |
| [bodrud-doza-scholarly-voice](bodrud-doza-scholarly-voice/) | Editing or drafting in my published scholarly voice | — |
| [food-system-scholarship-writing](food-system-scholarship-writing/), [food-system-scholarship-reviewing](food-system-scholarship-reviewing/), [food-system-scholarship-public-writing](food-system-scholarship-public-writing/) | Food-system scholarship in the vulnerability, resilience and buffers tradition: drafting papers, reviewing drafts, and plain-language pieces | — |
| [fable-playbook](fable-playbook/) | Planning and self-checking multi-step, high-stakes tasks | — |

Shared conventions: Python first, commented and reproducible; every analysis states its
CRS, units and time step; Canadian spelling unless a journal's style differs; no citation
from memory. Every DOI in the skills was checked against Crossref (`tools/check_dois.py`).

## Install

**claude.ai or Claude Desktop (paid plans): whole repository as a plugin.**
Customize → Plugins → Add → Add marketplace → Add from a repository → `bdzion/claude_skills_z`,
then install `claude-skills-z`. New commits sync without reinstalling. If the same skills
are already uploaded to your account as personal skills, remove those copies, or each
skill will appear twice.

**claude.ai: one skill at a time.** `python tools/package_skill.py water-quality-analysis`
writes `dist/water-quality-analysis.zip`; upload it under Customize → Skills → Add →
Upload skill. The packager leaves out tests and refuses zips the uploader rejects (more
than about 180 files, or a zip inside the zip).

**Claude Code.** `/plugin marketplace add bdzion/claude_skills_z` then
`/plugin install claude-skills-z`; or clone the repository and copy skill folders into
`~/.claude/skills/`.

## Tools

| Command | What it does |
|---|---|
| `python tools/validate_skills.py` | Frontmatter, description length, upload limits, test-case format, plugin manifest |
| `python tools/selftest.py` | Runs every bundled script's self-test (no network) |
| `python tools/check_dois.py [skill]` | Resolves every DOI in the skills against Crossref |
| `python tools/package_skill.py <skill>` / `--all` | Builds upload zips in `dist/` |
| `python tools/run_evals.py --list` / `<skill>` | Lists or runs test cases with `claude plugin eval` (Claude Code ≥ 2.1.269; billed model runs) |

GitHub Actions runs the validator and the script self-tests on every push.

## Adding or changing a skill

1. Create `<skill-name>/SKILL.md` with `name` (same as the folder) and a `description`
   that says what the skill does and when to use it (at most 1024 characters).
2. Put long material in `references/`, runnable code in `scripts/` (with a `selftest`),
   and test cases in `evals/<case-name>/` (`prompt.md`, `case.yaml`, `graders/*.md`).
3. Add the folder to `.claude-plugin/plugin.json` and `marketplace.json`.
4. Run `validate_skills.py`, `selftest.py` and `check_dois.py` before committing.

## Status and limits

- The six new skills have test cases but have not yet been scored with model runs;
  run `tools/run_evals.py` on one skill to get a with/without-skill comparison.
- The WhiteboxTools steps in `terrain_targeting.py` match the `whitebox` package's
  function signatures but were not executed when the skill was written; run them once on
  a small DEM and inspect the outputs.
- The bundled models (stress-test propagation, load estimators) are deliberately simple
  and transparent; each skill says when to move to EGRET/WRTDS, NADA2 or a calibrated
  empirical model.

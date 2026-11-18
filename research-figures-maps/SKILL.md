---
name: research-figures-maps
description: Plan, script and check publication figures and maps for watershed, water-quality, agricultural and food-system papers — hydrographs with precipitation, flow-duration and load-duration curves, observed-versus-simulated plots, BMP and scenario comparisons with uncertainty, study-area and result maps (scale bar, north arrow, CRS, data credits), colour-blind-safe palettes, journal sizes and captions. Use whenever the user asks to make, fix, critique or redesign a figure, plot model or monitoring results for a manuscript, build a study-area map, choose colours or a chart type, or write figure captions, even for a single plot.
---

# Research figures and maps

A figure earns its place when it shows something a table cannot (a pattern over time or
flow, a distribution, a spatial arrangement) and reads at print size in grey scale. Every
scripted figure reads its data from files, so it cannot drift from the numbers in the text.

## Workflow

1. **Decide what the figure must show** in one sentence and check that a table would not
   do it better. Note the target journal and its column widths.
2. **Pick the form** from [references/figure-guide.md](references/figure-guide.md):
   variable types, axes, transformations (log for flow and loads), and how uncertainty is shown.
3. **Script it** with the house style module `scripts/zfig.py`: `use_style()`,
   `figure("single"|"onehalf"|"double", height_mm)`, and recipes
   `hydrograph_with_rain`, `flow_duration`, `load_duration`, `obs_vs_sim`,
   `scenario_bars`. One script per figure (`figN_short_name.py`), data read by explicit
   path, units in every axis label, and an `assert` for each number the text quotes from
   the figure. Run `python scripts/zfig.py` once to self-test in a new environment.
4. **Maps**: follow the map checklist in the guide (CRS stated, scale bar, north arrow
   when orientation is not obvious, inset locator, legend with units, data sources and
   licence credits in the caption). For final layouts QGIS or ArcGIS Pro is usually
   quicker than matplotlib; script the data preparation either way.
5. **Look at the rendered file** at its final size before calling it finished: labels
   clipped or overlapping, legend covering data, ticks unreadable, colours collapsing in
   grey scale or for colour-vision deficiency.
6. **Caption**: what is shown, then how to read it (symbols, lines, shading, units,
   period, n). Keep interpretation in the text.

## Defaults that matter

- Okabe–Ito qualitative palette (built into `zfig`); viridis, cividis or Crameri
  scientific colour maps for continuous data; diverging maps only around a meaningful
  zero (e.g. change from baseline). No rainbow or jet (Crameri et al. 2020).
- 8 pt text at final size, 7 pt minimum; line widths 0.6–1.0 pt.
- Observed data in black or dark grey and simulations in colour, consistently across figures.
- Log axes for flow, loads and concentrations spanning orders of magnitude; say so in the label.
- Show uncertainty (95PPU bands, ranges across scenarios or climate members, confidence
  intervals); a bar without its spread overstates certainty.
- Do not invent data, coordinates or labels; if data are missing, write the script with
  a clear `NotImplementedError` and list what is needed.

Python first and commented; state units, CRS and time step in each figure script's docstring.

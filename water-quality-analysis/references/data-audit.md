# Data audit checklist

Run before any statistic. Record findings in the assumptions block.

## Units and identity
- Concentration units per parameter and over time (mg/L vs µg/L; "as P", "as N", "as NO3").
  A step change of exactly 1000× or 4.43× (NO3 vs NO3-N) is a units problem, not a trend.
- Parameter codes: total P vs total dissolved P vs SRP/orthophosphate; nitrate vs
  nitrate+nitrite. Do not merge them silently.
- Station identity: moved stations, renamed codes, upstream/downstream pairs.

## Detection limits and censoring
- Locate the censoring flag ("<", qualifier codes, negative values used as flags).
- List detection limits by year; laboratory changes often lower them, which creates a
  false downward trend if substituted values are used.
- Fraction censored per station-parameter. Above about 15 %, avoid substitution entirely;
  above about 50 %, report detection frequency instead of central tendency.

## Sampling design
- Samples per year and per month; gaps longer than a season.
- Flow representativeness: compare the flow distribution on sample days with all days
  (`wq_loads.py` flags unsampled high flows). Storm-targeted programs bias concentration
  statistics upward and fixed-schedule programs miss events; either way loads differ by method.
- Changes in sampling frequency or season coverage over the record (a source of artefact trends).

## Flow pairing
- Flow source (Water Survey of Canada HYDAT station, conservation-authority gauge, modelled),
  drainage-area ratio if the gauge is not at the sampling point (state the ratio).
- Daily mean vs instantaneous flow; time zone and the date convention for samples taken near midnight.
- Estimated or ice-affected flow codes (winter records in Ontario often carry them).

## Record completeness
- Missing flow days per period; do not report annual loads for incomplete years without a flag.
- Water year vs calendar year: choose one and keep it across stations.

## Outliers
- Check against physical plausibility and field notes before removing; never delete
  because a value is large. High-flow values are often the most important ones.

# What Gets Counted Gets Found

Code, data and preregistration for the paper

**What Gets Counted Gets Found: Capping versus Zero Weight for Prolific Accounts in Social Sensing**

Jingrui Tian and Benjamin C. M. Fung (McGill University)

arXiv: link to be added

The paper compares counting rules for social media monitoring on two objectives, retrieving ransomware events
(scored against ransomware.live registry listings) and selecting topics that draw subsequent discussion, in
cybersecurity posts on Bluesky. Its central comparison is between counting each author once and giving prolific
accounts zero weight.

Posts are public Bluesky posts. This repository contains no post text, no post URIs and no account identifiers:
accounts are salted hashes, and a public handle is kept only for accounts profiled as news, organisation or
security-feed accounts. Registry records are public ransomware.live listings.

## reproduce/
Every number, table and figure in the paper is generated from the JSON files in `reproduce/data/`:

    cd reproduce
    python tables/gen_paired.py      # paired comparisons (data/paired.json)
    python tables/gen_tables.py      # number macros and per-topic table (tables/numbers.tex, tables/topics.tex)
    python tables/gen_dualwin.py     # Table 2 (tables/dualwin.tex)
    python tables/gen_audit.py       # audit macros (tables/audit.tex)
    python figures/fig_forest.py     # and the other fig_*.py: figures/*.pdf

Requirements: Python 3.10+, numpy, scipy, matplotlib; figures use pgf with a LaTeX installation that has the
biolinum and fontawesome5 packages.

### Fresh-window registry snapshots (event task)
- `crossover_fresh.json`: reported in the paper. Registry updated on 2026-11-15, the preregistered date for the
  complete-registry re-run; original eight evaluation days (keys `b1`, `b5`, `b10`). The same file holds the
  maturity sensitivity analysis (`mature_cand_8d`: only candidates first posted on or before 2026-10-31, i.e. with
  the full +-14-day listing window, are credited; original eight days), the variant restricted to evaluation days up
  to 2026-10-31 (`mature_days_4d`), and the listings each rule retrieved (`retrieved_any_order`).
- `crossover_fresh_interim.json`: the interim evaluation on the registry ingested on 2026-11-07.
- `crossover_fresh_complete.json`: an intermediate re-run on the registry ingested on 2026-11-14.
- `crossover_fresh_capped*.json`: the exploratory rule "at most three posts per author" for the same snapshots.

### Other analyses added in revision
- `paired.json`: distinct authors minus zero feed weight (non-feed posts), both tasks and windows, with the maturity
  sensitivity; 100,000 bootstrap resamples over days.
- `feedrule_sensitivity.json`: main-window event replay under six feed-rule thresholds.
- Deletion control (equal-budget removal of flagged accounts' posts, of the same number of posts from the
  highest-output accounts, and of random posts): `eval_monitor.json` (`E_E_suppression_k3`, discussion),
  `eval_registry.json` (`E_E_on_registry_b5`, main-window events) and `crossover_fresh.json` (`E_E_b5`, fresh-window
  events).
- `contrast_perday.json`: per-day discussion totals of the fresh window (re-run of the original analysis; totals
  identical).
- `same_unit_main.json`, `same_unit_fresh.json`: same-unit check, i.e. the event task's candidates scored by the
  discussion objective (subsequent responders); only about 0.3% of candidates have any, so the rules cannot be
  separated.

## data/
- `main_sample/`: seed posts of the main sample (topic, actor type, human feed labels, outcome flags) and their reply
  and quote edges (hashed source account, depth, time, delay).
- `audit/`: the human audits T1-T4 (one author) and the model rater (Qwen3.5-4B), as item id, internal post id,
  sampling stratum and weight, the system's label, and the raters' labels. Post text is omitted. Added in revision
  (one author, blind to the rules): `C_retrieved_matches_*` checks all 172 exact registry matches retrieved by any
  ranking rule (the key lists which rules retrieved each); `C2_unflagged_extraction_*` checks victim extraction on
  40 posts by accounts the feed rule does not flag.

## code/
Analysis scripts that produced the JSON files (`code/scripts/`) and the interaction collector (`code/sensor/`). They
read a PostgreSQL database built by the collector from the public Bluesky API and are included for inspection.

## preregistration/
Pre-registrations written before the corresponding data were collected or evaluated, the amendment, and the log of
deviations, including the post-hoc analyses added in revision.

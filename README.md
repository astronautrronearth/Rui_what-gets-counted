# What Gets Counted Gets Found

Code, data, annotations and preregistration for the paper

**What Gets Counted Gets Found: Capping versus Zero Weight for Prolific Accounts in Social Sensing**

Jingrui Tian and Benjamin C. M. Fung (McGill University)

arXiv: link to be added

## The study in brief

Social media monitors rank content by counts of posts, authors or interactions. The paper evaluates these counts
on two tasks at once, in English cybersecurity posts on Bluesky:

- **Discussion task.** Each day, select three topics. A topic is credited with its *subsequent responders*: the
  accounts that reply to or quote its posts of that day within 24 hours after the daily cutoff and had not
  responded before it.
- **Event task.** Each day, review five victim candidates (normalised victim names extracted from ransomware
  posts). A candidate scores when its name matches a victim listed on the ransomware.live registry within ±14 days
  of its first post.

Prolific accounts, flagged by a posting-volume rule and mostly automated feeds, write most of the posts that name
ransomware victims, and these posts draw few replies or quotes. The central comparison is between counting each
author once (a cap on each account's contribution) and giving flagged accounts zero weight: both reach similar
discussion yields, but the cap retrieves several times as many registry-listed claims from the same candidates.

Two windows are evaluated: a main window (2026-08-22 to 2026-09-23, exploratory) and a fresh window (2026-10-21 to
2026-11-04), whose core comparisons were preregistered before labelling, registry ingestion and evaluation.

## Repository layout

```
reproduce/          regenerate every number, table and figure in the paper
  data/             result files (JSON) produced by the analysis scripts
  tables/           gen_*.py: number macros and tables
  figures/          fig_*.py: figures
data/
  main_sample/      de-identified posts of the main sample and their reply and quote edges
  audit/            all human and model annotations (no post text)
code/
  scripts/          analysis scripts that produced reproduce/data/
  sensor/           the Bluesky reply and quote collector
preregistration/    preregistrations, amendment, and the log of deviations
```

## Reproducing the paper

Requirements: Python 3.10+, numpy, scipy, matplotlib. The figures are rendered through matplotlib's pgf backend
and need a LaTeX installation with the `biolinum` and `fontawesome5` packages.

```
cd reproduce
python tables/gen_paired.py      # paired comparisons -> data/paired.json
python tables/gen_tables.py      # number macros and the per-topic table -> tables/numbers.tex, tables/topics.tex
python tables/gen_dualwin.py     # results table -> tables/dualwin.tex
python tables/gen_audit.py       # audit numbers -> tables/audit.tex
python figures/fig_cartoon.py    # likewise fig_method.py, fig_rq1.py, fig_forest.py, fig_budget.py -> figures/*.pdf
```

Where the paper's tables and figures come from:

| Paper element | Script | Main inputs in `reproduce/data/` |
|---|---|---|
| Figure 1: volume and participation | `figures/fig_cartoon.py` | `teaser.json` |
| Figure 2: the replay | `figures/fig_method.py` | none (process diagram) |
| Figure 3: victim-naming posts and coverage | `figures/fig_rq1.py` | `story_checks.json`, `cases.json`, `registry.json` |
| Figure 4: change relative to post volume | `figures/fig_forest.py` | `eval_monitor.json`, `eval_registry.json`, `eval_contrast.json`, `crossover_fresh.json`, `crossover_fresh_capped.json`, `story_checks.json` |
| Figure 5: review budgets | `figures/fig_budget.py` | `eval_registry.json`, `crossover_fresh.json`, `crossover_fresh_capped.json` |
| Table 1: per-topic counts and feed shares | `tables/gen_tables.py` | `sensitivity.json` |
| Table 2: each rule, both tasks, both windows | `tables/gen_dualwin.py` | as Figure 4, plus `paired.json`, `story_checks_random.json` |
| Numbers in the text | `tables/gen_tables.py`, `tables/gen_audit.py` | all files; audits from `audit_scores.json` and `audit_retrieved.json` |

### Fresh-window registry snapshots

The event task depends on when the registry was read, so three snapshots are kept:

| File | Registry read | Role |
|---|---|---|
| `crossover_fresh.json` | updated 2026-11-15 (695 listings), the preregistered date for the complete-registry re-run | **reported in the paper**. Also holds the follow-up sensitivity analysis (`mature_cand_8d`: only candidates first posted by 2026-10-31, which have the full ±14-day window, are credited) and the listings each rule retrieved (`retrieved_any_order`) |
| `crossover_fresh_interim.json` | ingested 2026-11-07 (446 listings) | interim evaluation |
| `crossover_fresh_complete.json` | ingested 2026-11-14 | intermediate re-run |

`crossover_fresh_capped*.json` hold the exploratory rule "at most three posts per author" on the same snapshots.

### Other analyses

| File | Content |
|---|---|
| `paired.json` | distinct authors minus zero feed weight, both tasks and windows, with 95% bootstrap intervals over days (100,000 resamples) |
| `feedrule_sensitivity.json` | main-window event task under six feed-rule thresholds |
| `contrast_perday.json` | per-day discussion totals in the fresh window |
| `same_unit_main.json`, `same_unit_fresh.json` | same-unit check: the event task's candidates scored by subsequent responders |
| `eval_monitor.json` (`E_E_suppression_k3`), `eval_registry.json` (`E_E_on_registry_b5`), `crossover_fresh.json` (`E_E_b5`) | deletion control: removing flagged accounts' posts, the same number of posts from the highest-output accounts, or random posts |

## Data

### `data/main_sample/`

- `seeds_with_feed_flags.csv`: 2,631 seed posts; the paper's main sample is the 2,452 with `in_main` = 1 and
  `status` = observed. One row per post with its topic (`topic_v2`), actor type, the two rule-based feed flags (`feed_volume_only`, the rule
  used in the paper, and `feed_behavioral_v1`), collection status, and reply, quote and repost counts.
- `edges.csv`: reply and quote edges of these posts (seed post, edge type, depth, hashed source account, whether
  the source is the seed's author, time and delay).
- `seeds_with_feed_flags.meta.json`: how the file was derived (hash function, flag definitions).

Accounts appear only as `author_hash` / `source_actor_hash`, the first 16 hex characters of sha256(salt || DID).
One salt is shared by every file in this repository, so hashes link across files (for example, the accounts of the
feed annotation below match `author_hash` in the main sample). A public handle is kept only for accounts profiled
as news, organisation or security-feed accounts. There is no post text and there are no post URIs.

## Annotations (`data/audit/`)

Each annotation task has a **key** file (what was shown, the sampling stratum and the system's label) and one or
more **label** files. Post text is not included; `post_id` is an internal identifier.

- Labels marked *author* were made by one of the authors.
- Labels marked *model* come from a second language model, **Qwen3.5-4B**, used as a second rater. Agreement
  statistics for T1 to T4 are therefore between an author and this model, as stated in the paper.
- Annotators did not see which ranking rule selected an item.

| Task | Question | Sample | Who labelled | Files |
|---|---|---|---|---|
| **F** feed status | Is this account an automated or templated feed (`feed`: feed / non_feed / unclear), and what is its role (automated feed, news media, organisational broadcast, security professional, individual, unclear)? | 201 accounts of the main sample: 75 flagged by the rules, 86 unflagged with at least three seed posts, 40 random | two human annotators: A on all 201, B on 75 for agreement; 17 labels adjudicated afterwards (16 A/B disagreements, one revision by A) | `F_feed_key.csv`, `F_feed_labels_annotatorA.csv`, `F_feed_labels_annotatorB.csv`, `F_feed_adjudicated.csv` |
| **T1** topic | Is the post about cybersecurity (`cyber`: yes / no / unsure), and which topics apply? | 425 posts, stratified by assigned topic, plus 80 posts the model rejected; stratum weights in `weight` | author on 120; model on all 425 | `T1_topic_key.csv`, `T1_topic_labels_author.csv`, `T1_topic_labels_model.csv` |
| **T2** victim extraction | Are the extracted names the victims the post reports (all correct / partly correct / wrong / none extracted, correctly / unsure), and which victims were missed? | 150 ransomware posts | author on 50; model on all 150 | `T2_extraction_key.csv`, `T2_extraction_labels_author.csv`, `T2_extraction_labels_model.csv` |
| **T3** registry matching | Do the candidate name and the registry victim name the same organisation (`same`: yes / no / unsure)? | 245 candidate–registry pairs, exact and fuzzy (`match_type`, hidden from the annotator) | author on 60; model on all 245 | `T3_matching_key.csv`, `T3_matching_labels_author.csv`, `T3_matching_labels_model.csv` |
| **T4** domain precision | Is the post on topic for its comparison domain (`in_domain`), and what kind of source wrote it? | 150 posts: 50 each from NBA basketball, AI / large language models, cryptocurrency | author on 50; model on all 150 | `T4_domain_key.csv`, `T4_domain_labels_author.csv`, `T4_domain_labels_model.csv` |
| **C** retrieved matches | Do the post's victim and the registry listing name the same organisation (`same_organisation`)? | all 172 exact matches retrieved by any non-random rule at five candidates a day (main window 78, fresh window 94); the key records which rules retrieved each (`rule_*`) | author on all 172 | `C_retrieved_matches_key.csv`, `C_retrieved_matches_labels_author.csv` |
| **C2** extraction on unflagged accounts | Does the post name a victim (`names_victim`), is the extraction correct (`extraction`), and which victims were missed? | 40 ransomware posts by accounts the feed rule does not flag: 10 per window and per stratum (with / without an extraction) | author on all 40 | `C2_unflagged_extraction_key.csv`, `C2_unflagged_extraction_labels_author.csv` |

Item identifiers are unique within a task. T3 and C both use the prefix `M`, so read each from its own files.

Results reported in the paper:

| Task | Result |
|---|---|
| F | 103 audited feeds; κ = 0.58 on 74 double-coded accounts; the volume rule has precision 0.67 and recall 0.49 against these labels |
| T1 | cybersecurity label correct for 99% of 92 sampled posts (stratum-weighted), κ = 0.85; assigned topic correct for 84% |
| T2 | extracted victims correct in 87% of 30 posts and found in 96% of 27 posts that name one, κ = 0.43 |
| T3 | all 19 audited exact matches and at least 73% of 41 fuzzy matches name the same organisation |
| T4 | NBA posts on topic in 81% of 16 |
| C | all 172 retrieved exact matches name the same organisation, including 7 whose country differs between post and registry |
| C2 | 11 of 12 named victims extracted, none missed in 20 posts without an extraction, 11 of 19 extracted names correct (the others are ransomware groups, vendors or generic phrases) |

Scoring code: `code/scripts/www_audit_score.py` (T1 to T4) and `code/scripts/www_sensitivity.py` (F). Summaries:
`reproduce/data/audit_scores.json`, `reproduce/data/sensitivity.json` and `reproduce/data/audit_retrieved.json`.
The annotation pages were built by `www_topic_audit.py` and `www_annotation_tasks.py`; the C and C2 samples by
`www_match_audit.py` and `www_extraction_audit_unflagged.py`.

## Code (`code/`)

`code/scripts/` holds the analysis scripts that produced every file in `reproduce/data/`, among them
`www_eval_monitor.py` (discussion task, main window), `www_eval_registry.py` (event task, main window),
`www_crossover_fresh*.py` (fresh window and its registry snapshots), `www_eval_contrast.py` (fresh-window
discussion task and the NBA comparison), `www_same_unit*.py`, `www_eval_registry_feedrule.py` and
`www_story_checks.py`. `code/sensor/` is the collector for reply and quote threads.

The scripts read a PostgreSQL database built by the collector from the public Bluesky API and the ransomware.live
API. The database is not distributed, so these scripts are included for inspection; `reproduce/` regenerates the
paper from their outputs.

## Preregistration (`preregistration/`)

- `PREREG.md`: the decision-level evaluation (2026-11-06), including the NBA comparison.
- `PREREG_CROSSOVER.md`: the fresh-window replication (2026-11-07). `PREREG_CROSSOVER_AMEND1.md` adds hypotheses
  H2 to H6 and the complete-registry re-run, written before evaluation.
- `DEVIATIONS.md`: every departure from these plans and every analysis added afterwards, with dates.

## Citation

```
@misc{tian2026counted,
  title  = {What Gets Counted Gets Found: Capping versus Zero Weight for Prolific Accounts in Social Sensing},
  author = {Tian, Jingrui and Fung, Benjamin C. M.},
  year   = {2026},
  note   = {arXiv preprint}
}
```

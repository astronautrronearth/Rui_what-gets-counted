# Deviations and incidents (frozen_eval)

- 2026-11-06: collection runs 4567-4568 (`bluesky_nba`, `nba_v1`) inserted 40,303 NBA posts with
  `posts.source_key = 'bluesky'`, because the collector stamps each RawPost with a module constant rather than
  the class attribute. Before any labelling or analysis touched them, they were moved to `source_key =
  'bluesky_nba'` (`UPDATE posts ... WHERE first_seen_run IN (4567, 4568) AND source_key = 'bluesky'`).
  No frozen result used these rows. The contrast collector now restamps posts after collection.
- E-B: candidate victim names are extracted with the topic_v2s model (Qwen3-4B, greedy) from ransomware-topic
  roots, because `post_entities` covers only the earlier Canada-labelled posts (PREREG named post_entities).
- E-A: tie-breaking by the mean over 100 random orders (not specified). Added sensitivity without 'unassigned'.
- E-C: producer-activity strata <= 1, 2-4, 5+ history posts (PREREG: 1, 2-4, 5+; authors absent from the
  history days are placed in <= 1).
- E-F: the stratified sample keeps one post per text hash within each cell, so small template cells could not
  be filled: 345 cybersecurity posts (target 400) plus 80 rejected posts; 120 double-labelled.
- E-D: the volume-only feed rule (>= 5 posts on >= 4 days) cannot be met in 3 history days; E-D uses >= 5 posts
  on all 3 history days. Concurrent cyber topics labelled with the topic_v2s configuration (label_topics_contrast.sh).
- E-B/E-A tie-breaking: E-B results first used one random tie-break per run, and candidate order depended on
  Python string hashing, so totals moved by up to six claims between identical runs. Final E-B results average
  50 tie-break orders over a sorted candidate pool (E-A: 100 orders, own seeded stream per decision); two runs
  give identical output. Only the averaged results are reported.
- E-E: added the PREREG's E-B outcome (registry claims under equal-budget suppression, b = 5).
- Evaluation window: the P_scale manifest was frozen when rules_v2 labels ended on 2026-09-21, so it has no roots
  on 2026-09-22/23 (found by the blind review: zero target for every policy on those days). E-A and E-B evaluate
  the 12 days 2026-09-10..21. Point estimates are unchanged; intervals recomputed over 12 days.
- E-A: added paired comparisons against all reply+quote edges (the strongest baseline) and relative-gain
  intervals bootstrapped as ratios of resampled totals.
- E-C2 (added after the blind review, not pre-registered): selection policies P2/P4 computed from a uniform
  10/25/50% sample of each day's roots, target on all roots, 100 draws.
- Dose-response (PREREG_DOSE): the 'all' stratum was listed both as unit 1 and among units 2-9; it is counted
  once, giving 12 units. Crypto/AI collection skips posts already stored under the cybersecurity source (shared
  posts are not re-inserted), so posts that are both cybersecurity and crypto/AI stay out of the new domains.
- Crypto/AI manifest: posts matching both domains were inserted under both sources (the two collectors ran
  concurrently); they are excluded from both domain populations before sampling.
- After the second blind review: (i) P10 persistent-topic baseline added to E-A and E-D (topics ranked by their
  mean target over the development days, fixed for evaluation); (ii) E-D now uses edges within 48 h of the root
  (the first version used 24 h, which truncated the target window for posts published early in the day; the
  target ends 24 h after the day-end cutoff). E-D's feed rule is >= 5 posts on all 3 history days (recorded above).
- Dose-response result (2026-11-06, run once): only 8 of the 12 units have both a concentration value and a defined
  gain. Canada, India and Australia have fewer than 4 topics with >= 30 posts (C undefined); Germany and India have
  no posts-ranked target on evaluation days (gain undefined). The pre-registered test is therefore computed on
  8 units, not 12: rho = 0.643, permutation p = 0.0498 ("supported" by the pre-registered rule, at the margin).
  Domain-only (5 units): rho = 0.80, p = 0.067. The small strata (UK P1 total 2.2, US 28) carry noisy gains.
- Post-hoc story checks (2026-11-07, NOT pre-registered; story_checks.json, scripts/www_story_checks.py, run once):
  (i) leave-one-day-out / leave-two-days-out of the E-A and E-D gains from the frozen per-day values (E-D per-day
  values recomputed with the frozen code); (ii) discordance C from history + development posts only;
  (iii) E-B simulation with clusters ranked by reply+quote edges and by distinct external responders (b = 5, exact).
  These are reported as exploratory.
- Post-hoc (2026-11-07, after the cold review): random ranking of candidate clusters on the E-B simulation (b = 5,
  50 orders) and the share of candidates without any reply or quote (story_checks_random.json). Exploratory.
- PREREG_CROSSOVER: registry ingested from 2026-10-08 (not 10-07) so that frozen main-window queries
  (published < 2026-10-08) are unchanged; candidates first posted on 2026-10-21 lose one day of the 14-day window.
- Post-hoc (2026-11-07, final cold review): timing of matched registry claims vs first candidate post (claim_timing.json, scripts/www_claim_timing.py). Exploratory.

- PREREG_CROSSOVER_AMEND1, complete registry (decided 2026-11-09): the promised re-ingest of ransomware.live on or
  after 2026-11-15 and the unchanged re-run as a complete-registry version were not performed before submission.
  The reported replication uses the registry as ingested on 2026-11-07 05:32 UTC (listings published up to
  2026-11-07), so candidates from about 2026-10-24 onward have a truncated 14-day match window. This affects every
  ranking rule alike; the paper states it in the replication paragraph.

- Post-hoc (2026-11-14, after the pre-registered reading): the main-window rule "posts with at most three per
  author" added to the fresh-window event replay (scripts/www_crossover_fresh_capped.py, identical code plus that
  rule; output crossover_fresh_capped.json, only the capped entries are used because the added rule shifts the
  random streams). b = 5: 14.6 claims vs 13.3 by posts (difference 1.3, 95% day-block interval 0.4 to 2.8).
  Exploratory. Pre-registered H5 (distinct authors >= posts, point estimate) did not hold: 13.0 vs 13.3.

- Post-hoc (2026-11-14, review response; no new data): (i) paired difference distinct authors minus non-feed posts
  on both tasks and windows, 95% percentile bootstrap over days of the summed daily differences of one replay (paper
  tables/gen_paired.py; fresh-window discussion per-day totals from scripts/www_eval_contrast_perday.py, a re-run of
  www_eval_contrast.py that only keeps per-day totals; totals identical). (ii) Feed-rule threshold sensitivity of the
  main-window event replay (scripts/www_eval_registry_feedrule.py): at least 3/5/10/20 posts with at least 4 active
  days, and at least 5 posts with at least 3/5 active days. The paper text was corrected to state the rule as
  implemented (at least five posts over the history days, active on at least four of seven; fresh window: active on
  all three). Exploratory.

- PREREG_CROSSOVER_AMEND1, complete registry (run 2026-11-14, superseding the 2026-11-09 decision not to re-run):
  ransomware.live re-ingested on 2026-11-14 (one day before the promised date; candidates first posted 2026-11-01..04
  still lack the full +14-day window), 231 new listings (148 published after 2026-11-07, 83 back-filled earlier
  listings), 677 in total. scripts/www_crossover_fresh_complete.py = www_crossover_fresh.py with the registry read
  up to 2026-11-14 instead of 2026-11-08; output crossover_fresh_complete.json (capped: crossover_fresh_capped_complete
  .json). The interim registry is backed up in outputs/interaction_experiment/www_eval/registry_snapshots/
  registry_20261107_fresh.jsonl (rows unchanged by the insert-only ingest; ingested_at <= 2026-11-07). Results (b = 5):
  posts 13.46, distinct authors 13.34, non-feed posts 5.02, replies and quotes 3.74, random 5.78; H1 replicated
  (edges - posts interval -17.1 to -3.8), H2-H4 hold, H5 not met, H6 not met (non-feed - posts interval -16.2 to
  0.02); distinct authors - non-feed posts 8.3 (interval -0.04 to 15.7); capped 14.76 (0.34 to 2.78). As of
  2026-11-14 the paper (main_v2) still reports the interim version; the complete version is documented in
  PROGRESS_1114.md of the paper repository for the authors to decide.

- 2026-11-15 (review response): registry re-ingested on 2026-11-15, the preregistered date (18 more listings, 695
  in total since 2026-10-08). The paper now reports the fresh window on this updated snapshot over the original 8
  evaluation days (scripts/www_crossover_fresh_mature2.py, output crossover_fresh_mature2.json, which also records
  the retrieved listings per rule); the November 7 interim snapshot moves to the supplementary material. Updated
  b = 5: posts 13.46, distinct authors 13.34, non-feed posts 5.02, replies and quotes 3.74; H1 replicated, H5 not
  met, H6 not met (interval -16.2 to 0.02). Maturity sensitivity (post hoc): only candidates with first post on or
  before 2026-10-31 (first post + 14 days <= 2026-11-14, the last full listing day before the ingest) are credited,
  original 8 days: posts 9.42, distinct authors 9.60, non-feed posts 2.90; distinct authors - non-feed posts 6.7
  (2.2 to 11.7). Also evaluation days up to 2026-10-31 only: difference 5.9 (2.1 to 10.0). Paired intervals now use
  100,000 bootstrap resamples (2,000 put the updated 8-day lower bound at -0.04 or +0.2 depending on the draw; with
  100,000 it is 0.1 to 0.2). Same-unit check (scripts/www_same_unit*.py): discussion objective on the event task's
  candidates; only 0.3% of candidates have any subsequent responder, so the check cannot separate the rules.
  Human verification of all retrieved exact matches (scripts/www_match_audit.py, 172 listings, blind to rules) is
  in progress.


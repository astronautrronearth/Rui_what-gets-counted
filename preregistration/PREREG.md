# Pre-registration: decision-level evaluation of counting policies (2026-11-06)

Written after the 2026-11-06 review round and before any of the analyses below were run. The P_scale corpus
(59,085 analysed seeds, frozen_scale) has been examined descriptively, so E-A to E-C are a **retrospective
held-out evaluation**, not an untouched confirmation. E-D uses newly collected data.

## Common definitions
- Root: an analysed P_scale seed (English, `rules_v2.is_cyber`, topic `topic_v2s`, 11 topics including
  unassigned). Day d: UTC calendar day of `published_at`. Cutoff c_d = end of day d.
- Edges: reply (depth <= 2) and quote edges with `event_created_at`. External: source account != root author.
- Information at cutoff c: posts with `published_at` < c and edges with `event_created_at` < c only.
- Feed rules for evaluation are computed **on the history days only** (days 1-7), never on later days.
- Split by day of the 33-day window (2026-08-22 .. 2026-09-23): days 1-7 history, days 8-19 development,
  days 20-33 evaluation (14 days). Choices below are fixed now; nothing is tuned on the evaluation days.

## E-A Discussion monitoring
- Decision: at each cutoff c_d, rank the topics using roots published on day d, select the top k (k = 3;
  sensitivity k = 1, 5).
- Target: distinct external accounts that respond (reply or quote) to those day-d roots during (c_d, c_d+24h]
  and had not responded to any day-d root of that topic before c_d. Summed over selected topics
  (an account counted once per topic-day).
- Policies (same k for all): P1 posts; P2 all reply+quote edges before c_d; P3 distinct authors; P4 distinct
  external responders before c_d; P5 text-deduplicated posts (normalised text hash); P6 author-capped posts
  (at most 3 per author per topic-day); P7 posts after removing history-rule feeds (volume-only rule);
  P8 non-self edges before c_d (self-edge correction only); P9 oracle (best possible; reported for scale only).
- Primary metric: total target over evaluation days, each policy against P1 (posts). Paired per-day
  differences, 95% CI by day-block bootstrap (B = 2000, block = 1 day). Secondary: NDCG@k against the target.
- Reported regardless of outcome: every policy, every k, the number of evaluation days with any target > 0.

## E-B Registry-claim discovery
- Ground truth: ransomware.live victim records published in the window (all countries, as ingested).
- Candidates: from P_scale roots in the ransomware topic, clusters keyed by normalised victim-organisation
  entity (`post_entities`, type org); a cluster is first eligible on the day of its first post.
- Daily review budget b = 5 previously unreviewed clusters (sensitivity b = 1, 10). Ranking policies: Q1 mention
  posts; Q2 distinct authors; Q3 text-deduplicated posts; Q4 author-capped posts; Q5 posts after removing
  history-rule feeds.
- Matching to registry: normalised organisation-name match (exact after lowercasing, punctuation and legal-suffix
  removal), then fuzzy (token-set ratio >= 90) reviewed blind to policy; unmatched candidates are not treated
  as false claims.
- Metrics: unique registry claims recovered over evaluation days per policy; also coverage conditional on a
  claim having any observed post (separates retrieval from prioritisation); median delay to registry
  publication. Paired event-level comparison against Q1, CI by publication-day block bootstrap.

## E-C Reporting protocol under partial neighbourhood collection
- Quantity: external-response incidence per topic-week, the share of roots with >= 1 external reply/quote
  within 24 h. Full-retrieval value is the reference.
- Designs: uniform root sampling and sampling stratified by topic x producer activity (author's posts in the
  history days: 1, 2-4, 5+), at 10%, 25%, 50%; 500 repetitions; weighted estimator sum_h (N_h/N) ybar_h.
- Cost: API requests from `interaction_snapshots` (pages actually requested per root and endpoint).
- Metrics: mean absolute error per topic-week, 95% interval coverage (normal approximation within strata),
  top-3 topic recovery, requests used.

## E-D Contrast domain (NBA)
- Collection: `bluesky_nba` / `nba_v1` (scripts/collect_contrast.py), 2026-10-21 .. 2026-11-04, 3 pages per term
  and day. Units: the matched term (team or league); posts matching several terms belong to each.
- Concurrent cybersecurity slice: bluesky `rules_v2.is_cyber` English posts of the same days.
- Roots: random sample of up to 10,000 per domain (seed 20261106); neighbourhoods with the same collector
  settings; only edges within 24 h of the root are used, so both domains have the same observation window.
- Measures per domain: concentration (posts vs N_eff Spearman over units), self share, continuation share,
  and E-A with units = teams / topics, days split in the same proportions (first 3 history, then 4 dev,
  last 8 evaluation), policies and k frozen as above.
- Readings: "transfers" if the sign of P3 - P1 and P4 - P1 is the same in both domains with CIs excluding 0;
  otherwise report the boundary together with concentration and self share.

## E-E Equal-budget suppression (replaces the output-binned placebo as the main control)
- B = number of posts removed by the volume-only history-rule feeds in the evaluation days.
- Remove exactly B posts by: uniform random deletion; deletion from the highest-output accounts; duplicate-text
  suppression then uniform random for the remainder (1,000 draws where random).
- Outcomes: E-A target under P1 after suppression, E-B registry coverage, retained distinct producers.

## E-F Topic-label audit (human)
- 400 posts stratified by topic x producer activity x template repetition (text hash seen >= 3 times), seed
  20261106; 80 rejected-or-unassigned posts if available. Producer and engagement hidden.
- Two authors label cybersecurity relevance and topic (multi-label, unsure allowed); 120 double-labelled;
  adjudication. Report weighted precision, topic confusion and differences between templated and other posts,
  and propagate stratum-specific errors to E-A.

Every outcome is reported, including nulls and results favouring raw post counts.

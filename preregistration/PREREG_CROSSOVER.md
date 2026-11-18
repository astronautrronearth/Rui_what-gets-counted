# Pre-registration: does the crossover replicate in a fresh window? (2026-11-07)

Written after the post-hoc finding in the main window (story_checks.json: ranking victim clusters by reply+quote
edges retrieved 8.3 registry claims vs 28.0 by posts, b = 5) and before any of the data below were labelled,
collected or matched. The discussion side of the fresh window (E-D: edges +42% over posts) is already known.

## Claim under test
In a new two-week window of the same cybersecurity collection, the count that is best for discussion monitoring
(reply+quote edges) is worse than post volume for registry-claim retrieval, and removing feed accounts is worse
still: the crossover seen in the main window recurs.

## Data (fixed now)
- Posts: source `bluesky`, lang en*, non-empty text, rules_v2 is_cyber, 2026-10-21 <= published_at < 2026-11-05.
- Ransomware candidates: topic_v2s = ransomware (same model, revision and prompt as the main window). For cost,
  topic_v2s is run only on posts matching the prefilter regex below; in the main window this regex covers
  8,150 of 8,167 ransomware-topic posts (99.8%).
  `(ransom|leak|extort|lockbit|akira|qilin|blackcat|alphv|clop|cl0p|play |medusa|rhysida|8base|bianlian|hunters|
  inc ransom|safepay|dragonforce|data breach|victim|hack|breach|stolen data|darkweb|dark web)` (case-insensitive)
- Neighbourhoods: same collector, depth and endpoints as E-D, for every ransomware candidate; edges within 48 h.
- Victims: www_extract_victims.py prompt and model (Qwen3-4B-Instruct-2507, greedy), clustered by normalised name.
- Registry: ransomware.live, countries CA, US, FR, GB, published 2026-10-07..2026-11-08 (ingested after this file
  is committed). Exact normalised-name match within 14 days of the cluster's first post (as E-B).

## Protocol (as E-B, adapted to the E-D day split)
- Days 2026-10-21..11-04: history = first 3 days, reviews from day 4, claims counted when found on the 8
  evaluation days (2026-10-28..11-04). Budget b = 5 clusters per day (b = 1, 10 reported as sensitivity).
- Policies: posts; reply+quote edges before the day's cutoff; distinct external responders before the cutoff;
  posts without feed accounts. Feed rule as E-D: >= 5 posts on each of the 3 history days, computed on all posts of
  the window's cybersecurity population (not only candidates).
- Equal-budget removal (as E-E): remove B = number of feed candidate posts by feeds / top-output accounts /
  uniformly at random (40 draws), then rank by posts.
- 50 random tie orders per policy; paired difference to posts bootstrapped over registry publication days.

## Readings
- "Replicated" if edges-ranking retrieves fewer claims than posts-ranking with the 95% bootstrap interval of the
  difference below 0, at b = 5. Same rule reported for responders and for feed removal.
- "Not replicated" if the point estimate is >= 0; "inconclusive" otherwise, or if fewer than 10 registry claims
  are attainable at all (any cluster matched) in the evaluation days.
- Known limitation fixed in advance: registry records published after the ingest date are missing, which shortens
  the match window for the last days equally for every policy.
- All outcomes are reported in the paper, whatever they are.

# Amendment 1 to PREREG_CROSSOVER (2026-11-07, before any fresh-window candidate, neighbourhood, victim or registry
# match has been evaluated; topic labelling of the candidate pool still running at the time of commit)

Motivation: after the main-window cold review, random-order retrieval (9.1 claims) and the zero-engagement share
of candidates (91% of clusters) were computed post hoc (story_checks_random.json). They suggest the mechanism
"engagement carries no information about events". The tests below are added before the fresh-window evaluation.
The primary test and reading of PREREG_CROSSOVER are unchanged.

## Added hypotheses (fresh window, exact match, b = 5 unless stated)
- H2 (mechanism): >= 80% of candidate victim clusters have no reply or quote edge within 48 h.
- H3 (mechanism): >= 80% of candidate posts are written by feed accounts (E-D feed rule).
- H4 (engagement is uninformative for events): claims by edges-ranking minus claims by a random order (50 orders),
  bootstrapped over registry publication days; supported if the 95% interval includes 0 or lies below 0.
- H5 (producer count as compromise): claims by distinct authors >= claims by posts (point estimate), with the
  interval of the difference reported.
- H6: feed removal (posts without feeds) retrieves fewer claims than posts (interval below 0); this was already a
  reported rule in PREREG_CROSSOVER and is now named.

## Added sensitivity analyses (reported, not used for the primary reading)
- All review days (days 4-15) instead of the 8 evaluation days.
- b = 1 and b = 10 (already planned), and the sum over b in {1, 5, 10}.
- Fuzzy name matching (E-B fuzzy rule).
- Complete registry: the registry is ingested again on or after 2026-11-15 so that every candidate has its full
  14-day match window; the whole analysis is re-run unchanged and reported as the complete-registry version, next
  to tonight's interim version.

All outcomes are reported, whatever they are.

"""Generate every number in the paper from the frozen results (data/, see data/FROZEN_README.md).

    python3 tables/gen_tables.py  → tables/topics.tex, tables/robustness.tex, tables/numbers.tex
Never type a number into main.tex; add it here as a macro.
"""
import json
from scipy.stats import spearmanr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
J = lambda n: json.loads((ROOT / "data" / n).read_text())
S, R, G = J("sensitivity.json"), J("registry.json"), J("countgap.json")["count_gap_main"]
V, AU = S["variants"], S["audit"]
M, H = V["main"], AU["main_with_human_feeds"]
SC, SCH = V["strict_canada"], AU["strict_canada_with_human_feeds"]
NAME = {"data_breach": "Data breach", "vulnerability_cve": "Vulnerability / CVE", "unassigned": "(unassigned)",
        "ransomware": "Ransomware", "gov_advisory": "Gov.\\ advisory", "phishing_scam": "Phishing / scam",
        "malware_infostealer": "Malware / infostealer", "policy_regulation": "Policy / regulation",
        "critical_infrastructure": "Critical infra.", "ddos_outage": "DDoS / outage", "fraud_financial": "Financial fraud"}
from decimal import Decimal, ROUND_HALF_UP
_r = lambda x, q: str((Decimal(str(x)) * 100).quantize(Decimal(q), rounding=ROUND_HALF_UP))
pct = lambda x: _r(x, "1")          # half-up on the stored value (floats would turn 7.55 into 7.5)
pct1 = lambda x: _r(x, "0.1")
ci = lambda c: f"[{pct1(c[0])}, {pct1(c[1])}]"
cnum = lambda n: f"{n:,}".replace(",", "{,}")


def p(x):
    return "$<$0.001" if x < 0.001 else f"{x:.3f}"


def prel(x):  # for running text: "$p$\numX" renders "p < 0.001" or "p = 0.023"
    return "${}<0.001$" if x < 0.001 else f"${{}}={x:.3f}$"


# Table 1: per topic, all accounts vs human-audited feeds removed.
# Ranks are competition ranks (ties share the better rank and are marked "="); rates divide integer counts.
def crank(vals):
    return {t: (1 + sum(v > vals[t] for v in vals.values()), sum(v == vals[t] for v in vals.values()) > 1) for t in vals}


def rk(r):
    return f"={r[0]}" if r[1] else f"{r[0]}"


def tied(r):
    return f"{r[0]} (tied)" if r[1] else f"{r[0]}"


def rate(a, b):
    return str((Decimal(a) / Decimal(b)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


T0, TH = M["topics"], H["topics"]
RK = {"posts": crank({k: v["posts"] for k, v in T0.items()}),
      "raw": crank({k: v["inter_raw"] for k, v in T0.items()}),
      "ns": crank({k: v["inter_nonself"] for k, v in T0.items()}),
      "hposts": crank({k: v["posts"] for k, v in TH.items()}),
      "hns": crank({k: v["inter_nonself"] for k, v in TH.items()})}
SHORT = {"data_breach": "Data breach", "vulnerability_cve": "Vulnerability", "unassigned": "(unassigned)",
         "ransomware": "Ransomware", "gov_advisory": "Gov.\\ advisory", "phishing_scam": "Phishing",
         "malware_infostealer": "Malware", "policy_regulation": "Policy", "critical_infrastructure": "Critical infra.",
         "ddos_outage": "DDoS", "fraud_financial": "Fin.\\ fraud"}
SWATCH = {"ransomware": "ccblue", "vulnerability_cve": "ccorange"}
D2f = lambda x: str(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
rows = []
for k, a in sorted(T0.items(), key=lambda kv: (-kv[1]["posts"], kv[0])):
    h = TH[k]
    nm = (f"\\rowcolor{{{SWATCH[k]}!8}}\\sw{{{SWATCH[k]}}}{SHORT[k]}" if k in SWATCH else f"\\nosw{{}}{SHORT[k]}")
    rows.append(f"{nm} & {a['posts']} & \\fbar{{{pct(1 - h['posts'] / a['posts'])}}} & "
                f"{rate(a['inter_raw'], a['posts'])} & {rate(a['inter_nonself'], a['posts'])} & "
                f"{h['posts']}\\rk{{{rk(RK['hposts'][k])}}} & {rate(h['inter_nonself'], h['posts'])} \\\\")
(ROOT / "tables/topics.tex").write_text("\n".join(rows) + "\n")
_v = T0["vulnerability_cve"]
VULN_CROSS_PP = rate(_v["inter_nonself"], _v["posts"])   # cross-user replies and quotes per vulnerability post


# Table 2: robustness, grouped rows
def rrow(name, v):
    r = v["ransomware"]
    return (f"\\quad {name} & {cnum(v['n'])} & {pct1(v['self_share'])} & {pct1(v['CSR_raw'])} & "
            f"{pct1(v['CSR_nonself'])}\\ci{{{ci(v['CSR_nonself_ci'])}}} & {r['posts']} & "
            f"{D2f(r['ratio_vs_rest'])} \\\\")


grp = lambda t: f"\\multicolumn{{7}}{{@{{}}l}}{{\\grp{{{t}}}}} \\\\"
lines = [grp("Main sample"), rrow("All seeds", M),
         grp("Feeds removed, defined by"), rrow("Human audit", H),
         rrow("Behavioural rule", V["feeds_behavioral"]), rrow("Volume-only rule", V["feeds_volume_only"]),
         grp("Other exclusions"), rrow(f"{S['n_partial_main']} partial seeds", V["main_no_partial"]),
         rrow("Top-10 producers", V["main_minus_top10"]),
         grp("Strict Canada subset"), rrow("All seeds", SC), rrow("Human feeds removed", SCH)]
(ROOT / "tables/robustness.tex").write_text("\n".join(lines) + "\n")

c, f = AU["canada"], AU["feed"]
D2 = lambda x: str(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
fd = R["by_feed_definition"]
mt, ht = M["topics"], H["topics"]
rw = lambda v: v["ransomware"]
others = [k for k in mt if k not in ("ransomware", "vulnerability_cve", "gov_advisory")]
m = {
    "NSeeds": cnum(M["n"]), "NEdges": M["edges"], "NSelf": M["self_edges"], "SelfPct": pct(M["self_share"]),
    "SelfPctH": pct(H["self_share"]), "SelfPctSC": pct(SC["self_share"]),
    "CSRall": pct1(M["CSR_raw"]), "CSRns": pct1(M["CSR_nonself"]), "CSRnsCI": ci(M["CSR_nonself_ci"]),
    "CSRallH": pct1(H["CSR_raw"]), "CSRnsH": pct1(H["CSR_nonself"]),
    "PermAll": prel(M["perm_p_nonself"]), "PermH": prel(H["perm_p_nonself"]),
    "PermV": prel(V["feeds_volume_only"]["perm_p_nonself"]), "PermSC": prel(SC["perm_p_raw"]),
    "PermSCH": prel(SCH["perm_p_nonself"]),
    "RWseeds": rw(M)["posts"], "RWleftH": rw(H)["posts"], "RWfeedH": rw(M)["posts"] - rw(H)["posts"],
    "RWfeedPctH": pct(1 - rw(H)["posts"] / rw(M)["posts"]), "RWrankH": tied(RK["hposts"]["ransomware"]),
    "RWratioH": f"{rw(H)['ratio_vs_rest']:.2f}", "RWselfAll": rw(M)["self_edges"], "RWedgesAll": rw(M)["edges"],
    "RWfeedPctB": pct(1 - V["feeds_behavioral"]["topics"]["ransomware"]["posts"] / rw(M)["posts"]),
    "RWfeedPctV": pct(1 - V["feeds_volume_only"]["topics"]["ransomware"]["posts"] / rw(M)["posts"]),
    "VulnFeedPctH": pct(1 - ht["vulnerability_cve"]["posts"] / mt["vulnerability_cve"]["posts"]),
    "GovFeedPctH": pct(1 - ht["gov_advisory"]["posts"] / mt["gov_advisory"]["posts"]),
    "OtherFeedMin": pct(min(1 - ht[k]["posts"] / mt[k]["posts"] for k in others)),
    "OtherFeedMax": pct(max(1 - ht[k]["posts"] / mt[k]["posts"] for k in others)),
    "VulnAll": mt["vulnerability_cve"]["inter_raw"], "VulnNS": mt["vulnerability_cve"]["inter_nonself"],
    "VulnSelfPct": pct(1 - mt["vulnerability_cve"]["inter_nonself"] / mt["vulnerability_cve"]["inter_raw"]),
    "VulnRankRaw": tied(RK["raw"]["vulnerability_cve"]),
    "VulnRankNS": tied(RK["ns"]["vulnerability_cve"]),
    "VulnRankBoth": tied(RK["hns"]["vulnerability_cve"]),
    "CritRankRaw": tied(RK["raw"]["critical_infrastructure"]),
    "CritRankNS": tied(RK["ns"]["critical_infrastructure"]),
    "SCn": SC["n"], "SCRW": rw(SC)["posts"], "SCRWrank": SC["topics"]["ransomware"]["rank_posts"],
    "SCRWleft": rw(SCH)["posts"], "SCRWedges": rw(SC)["edges"], "SCVuln": SC["topics"]["vulnerability_cve"]["posts"],
    "CaPrec": pct(c["precision"]), "CaPrecCI": f"{pct(c['precision_ci'][0])}--{pct(c['precision_ci'][1])}",
    "CaN": c["n_primary"], "CaDouble": c["reliability"]["double_coded"], "CaAgree": pct1(c["reliability"]["raw_agreement"]),
    "CaKappa": f"{c['reliability']['kappa']:.2f}",
    "StrictPrec": pct(c["strict_filter"]["precision"]), "StrictRec": pct(c["strict_filter"]["recall"]),
    "FeedN": f["n_primary"], "FeedYes": f["counts"]["feed"], "FeedDouble": f["reliability"]["double_coded"],
    "FeedAgree": pct1(f["reliability"]["raw_agreement"]), "FeedKappa": f"{f['reliability']['kappa']:.2f}",
    "FeedAdj": f["reliability"]["adjudicated_items"],
    "BehP": D2(f['rules']['behavioral_v1']['precision']), "BehR": D2(f['rules']['behavioral_v1']['recall']),
    "VolP": D2(f['rules']['volume_only']['precision']), "VolR": D2(f['rules']['volume_only']['recall']),
    "RegEvents": R["events"], "RegVisible": R["events_with_cyber_post"], "RegCorpus": R["events_in_corpus"],
    "RegHits": R["cyber_hits"], "RegAccts": R["accounts"], "RegZeroLikes": R["hits_with_zero_likes"],
    "RegMaxLikes": R["max_likes_any_hit"], "RegTopA": R["top3_accounts_event_coverage"][0],
    "RegNFvol": fd["volume_only"]["events_with_nonfeed_post"],
    "GapDoneSelf": G["reply_d1"]["self_reported"], "GapDoneGot": G["reply_d1"]["retrieved"],
    "GapQ": G["quote"]["retrieved"], "GapRPself": cnum(G["repost"]["self_reported"]), "GapRPgot": cnum(G["repost"]["retrieved"]),
    "NPartial": S["n_partial_main"],
}
(ROOT / "tables/numbers.tex").write_text("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m.items()))
print(json.dumps(m))

# producer decomposition (data/producer.json, frozen_1106)
P = J("producer.json")
PA, PS = P["all|human"], P["strict_canada|human"]
pt = PA["topics"]
k_ = PA["ransomware_kitagawa"]
m2 = {
    "NeffRW": f"{pt['ransomware']['N_eff']:.1f}", "NeffRWci": f"{pt['ransomware']['N_eff_ci'][0]:.1f}--{pt['ransomware']['N_eff_ci'][1]:.1f}",
    "NeffDB": f"{pt['data_breach']['N_eff']:.0f}", "NeffVuln": f"{pt['vulnerability_cve']['N_eff']:.0f}",
    "NeffGov": f"{pt['gov_advisory']['N_eff']:.1f}", "PostsDB": pt["data_breach"]["posts"],
    "PostsVuln": pt["vulnerability_cve"]["posts"], "PostsGov": pt["gov_advisory"]["posts"],
    "PartRW": pt["ransomware"]["cross_participants"], "PartVuln": pt["vulnerability_cve"]["cross_participants"],
    "PartDB": pt["data_breach"]["cross_participants"], "TopFiveRW": pct(pt["ransomware"]["top5"]),
    "RankNeffRW": pt["ransomware"]["rank_N_eff"], "RankNeffVuln": pt["vulnerability_cve"]["rank_N_eff"],
    "RankNeffGov": pt["gov_advisory"]["rank_N_eff"],
    "RhoPostsNeff": f"{spearmanr([pt[t]['posts'] for t in pt], [pt[t]['N_eff'] for t in pt]).statistic:.2f}",
    "RhoPostsAuth": f"{spearmanr([pt[t]['posts'] for t in pt], [pt[t]['authors'] for t in pt]).statistic:.2f}",
    "AuthRW": pt["ransomware"]["authors"], "AuthVuln": pt["vulnerability_cve"]["authors"], "AuthDB": pt["data_breach"]["authors"],
    "NonfeedDispUp": pct(-PA["dispersion"]["reduction_nonfeed"]),
    "StdRed": pct(PA["dispersion"]["reduction_std"]),
    "StdRedCI": f"{pct(PA['dispersion']['reduction_std_ci'][0])}--{pct(PA['dispersion']['reduction_std_ci'][1])}",
    "StdRho": f"{PA['rank_corr']['r_vs_r_std']:.2f}", "PooledFeed": pct(PA["dispersion"]["pooled_feed_share"]),
    "RHrw": f"{pt['ransomware']['rH']:.2f}", "RHdb": f"{pt['data_breach']['rH']:.2f}",
    "KitComp": pct(k_["composition_share"]),
    "KitCompCI": f"{pct(k_['composition_share_ci'][0])}--{pct(k_['composition_share_ci'][1])}",
    "KitCompB": pct(P["all|behavioral_v1"]["ransomware_kitagawa"]["composition_share"]),
    "KitCompV": pct(P["all|volume_only"]["ransomware_kitagawa"]["composition_share"]),
    "SCStdRed": pct(PS["dispersion"]["reduction_std"]), "StdRedB": pct(J("producer.json")["all|behavioral_v1"]["dispersion"]["reduction_std"]), "SCNeffRW": f"{PS['topics']['ransomware']['N_eff']:.1f}",
    "SCPartRW": PS["topics"]["ransomware"]["cross_participants"], "SCKitComp": pct(PS["ransomware_kitagawa"]["composition_share"]),
}
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m2.items()))
print(json.dumps(m2))

# strengthening experiments (data/experiments.json, frozen_1107; pre-registered in PREREG.md)
X = J("experiments.json")
b3 = next(b for b in X["E1"]["human"] if b["k"] == 3.0)
bp = [b["share_survive_participants"] for d in X["E1"].values() for b in d]
e2 = X["E2"]
crossk = [v["cross_edges"]["k_star"] for v in e2.values() if v["cross_edges"] and v["cross_edges"]["drop_needed"] == 2]  # topics that can fall two places
e3 = X["E3"]["human"]
st = e3["strata"]
e4 = X["E4"]
m3 = {
    "Bursts": b3["bursts"], "BurstNF": pct(b3["share_survive_nonfeed"]), "BurstNFbase": pct(b3["base_rate_nonfeed_burst"]),
    "BurstPart": pct(b3["share_survive_participants"]), "BurstPartBase": pct(b3["base_rate_participant_burst"]),
    "BurstPartLo": pct(min(bp)), "BurstPartHi": pct(max(bp)),
    "BurstNeff": f"{b3['median_neff_burst_day']:.0f}",
    "KcrossTopics": len(crossk), "KcrossSmall": sum(k <= 2 for k in crossk),
    "KcrossDB": e2["data_breach"]["cross_edges"]["k_star"],
    "KpostsRW": e2["ransomware"]["posts"]["k_star"], "KpostsRWposts": e2["ransomware"]["posts"]["posts_removed"],
    "PlacRWrank": int(e3["stats"]["rw_rank_posts"]["real"]), "PlacRWrankP": int(e3["stats"]["rw_rank_posts"]["placebo_median"]),
    "PlacRho": f"{e3['stats']['rho_posts_rank']['real']:.2f}", "PlacRhoLo": f"{e3['stats']['rho_posts_rank']['placebo_95'][0]:.2f}",
    "HiFeeds": st["20-49"]["feeds"] + st["50-max"]["feeds"],
    "HiAll": sum(st[b]["feeds"] + st[b]["nonfeeds"] for b in ("20-49", "50-max")), "HiNonfeeds": st["20-49"]["nonfeeds"] + st["50-max"]["nonfeeds"],
    "SelfCont": pct(e4["shares"]["continuation"]), "SelfContTen": pct(e4["delay_minutes"]["continuation"]["share_le_10min"]),
    "SelfResp": pct(e4["shares"]["response"]),
}
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m3.items()))
print(json.dumps(m3))
m4 = {"BurstPartN": round(b3["share_survive_participants"] * b3["bursts"])}
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m4.items()))

# m5: cartoon teaser (Figure 1), from data/teaser.json
TZ = J("teaser.json")
_rw, _ci = TZ["ransomware"], TZ["critical_infrastructure"]
_top4 = [n for n, f in zip(_rw["by_rank"], _rw["feed_by_rank"])][:4]
assert all(_rw["feed_by_rank"][:4]), "top-4 ransomware accounts are expected to be feeds"
m5 = {"TopFourRW": sum(_top4), "PostsCI": _ci["posts"], "AuthCI": _ci["accounts"],
      "PartCI": _ci["cross_participants"], "PostRatioRWCI": f"{_rw['posts'] / _ci['posts']:.0f}"}
print(m5)
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m5.items()))

# m6: replication at scale (data/scale.json, data/country_audit.json; frozen_scale)
SCL, CAU = J("scale.json"), J("country_audit.json")
ST = SCL["strata"]
big = [k for k, v in ST.items() if v["n"] >= 300 and k != "all"] + ["all"]
_ci_ok = lambda v, r: (v["feeds"][r].get("std_reduction_ci") or [-1])[0] > 0
_a, _t = ST["all"], ST["all"]["topics"]
_b = _a["feeds"]["behavioral_v1"]
_nc = ST["no_country"]["feeds"]
_cty = [k for k in big if k not in ("all", "no_country")]
_yes = sum(v["reference"].get("yes", 0) for v in CAU["countries"].values())
_no = sum(v["reference"].get("no", 0) for v in CAU["countries"].values())
m6 = {"ScaleN": cnum(SCL["n_observed"]), "ScaleManifest": cnum(SCL["n_manifest"]),
      "ScaleObs": pct1(SCL["n_observed"] / SCL["n_manifest"]),
      "ScaleRhoAuth": D2(_a["rho_posts_accounts"]), "ScaleRhoNeff": D2(_a["rho_posts_neff"]),
      "ScaleRWposts": cnum(_t["ransomware"]["posts"]), "ScaleRWNeff": f"{_t['ransomware']['N_eff']:.1f}",
      "ScaleVulnPosts": cnum(_t["vulnerability_cve"]["posts"]), "ScaleVulnNeff": f"{_t['vulnerability_cve']['N_eff']:.0f}",
      "ScaleSelf": pct(_a["self_share"]), "ScaleCont": pct(_a["continuation_share"]),
      "ScaleSelfLo": pct(min(ST[k]["self_share"] for k in big)), "ScaleSelfHi": pct(max(ST[k]["self_share"] for k in big)),
      "ScaleRed": pct(_b["std_reduction"]), "ScaleRedCI": f"{pct(_b['std_reduction_ci'][0])}--{pct(_b['std_reduction_ci'][1])}",
      "ScaleStrata": len(big),
      "ScaleFone": sum(ST[k]["rho_posts_neff"] < ST[k]["rho_posts_accounts"] for k in big),
      "ScaleFtwo": sum(ST[k]["self_share"] >= 0.2 and ST[k]["continuation_share"] >= 0.6 for k in big),
      "ScaleCompB": sum(_ci_ok(ST[k], "behavioral_v1") for k in big),
      "ScaleCompV": sum(_ci_ok(ST[k], "volume_only") for k in big),
      "ScaleBreak": _a["breakdown_cross_two_le2"], "ScaleBreakTopics": _a["breakdown_cross_two_topics"],
      "ScaleCountries": len(_cty),
      "ScaleAmp": sum(ST[k]["feeds"]["volume_only"]["feed_share"] > _nc["volume_only"]["feed_share"] for k in _cty),
      "ScaleTimes": f"{SCL['n_observed'] / M['n']:.0f}", "CtyPrec": D2(_yes / (_yes + _no)), "CtyN": sum(v["n"] for v in CAU["countries"].values())}
print(m6)
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m6.items()))

# m7: dataset size (data/scale_collection.json) and case studies (data/cases.json)
SCC, CSJ = J("scale_collection.json"), J("cases.json")
m7 = {"ScaleEdges": cnum(sum(r["edges"] for r in SCC["runs"].values())),
      "CaseFeedPosts": CSJ["feed_case"]["posts_in_topic"], "CaseFeedCross": CSJ["feed_case"]["posts_in_topic_with_any_cross"],
      "CaseSelfN": CSJ["self_case"]["n_continuations"], "CaseSelfDelay": f"{max(CSJ['self_case']['delays_min']):.0f}",
      "RWBurstsFeedLo": min(f * 100 // p for f, p, b in zip(CSJ["timeline"]["ransomware"]["feed_posts"],
                            CSJ["timeline"]["ransomware"]["posts"], CSJ["timeline"]["ransomware"]["burst"]) if b),
      "RWBursts": sum(CSJ["timeline"]["ransomware"]["burst"]),
      "RWBurstsPartMax": max(c for c, b in zip(CSJ["timeline"]["ransomware"]["participants"], CSJ["timeline"]["ransomware"]["burst"]) if b)}
print(m7)
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m7.items()))

# m8: review fixes (2026-11-06)
_e3 = J("experiments.json")["E3"]["human"]
_cty_big = [k for k in ST if ST[k]["n"] >= 300 and k not in ("all", "no_country")]
m8 = {"PlacRemoved": _e3["placebo_removed_posts_median"], "RealRemoved": cnum(_e3["real"]["removed"]),
      "ScaleFoneCty": sum(ST[k]["rho_posts_neff"] < ST[k]["rho_posts_accounts"] for k in _cty_big),
      "RegNFbeh": R["by_feed_definition"]["behavioral_v1"]["events_with_nonfeed_post"],
      "SelfQuote": J("experiments.json")["E4"]["classes"]["self_quote"]}
print(m8)
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m8.items()))

# m9: decision-level evaluation (data/eval_*.json, frozen_eval)
EM, ER, ES = J("eval_monitor.json"), J("eval_registry.json"), J("eval_sampling.json")
_k3 = EM["primary"]["k3"]
_rel = lambda p: pct(_k3[p]["vs_posts_rel"])
_ci_rel = lambda p: f"{pct(_k3[p]['vs_posts_rel_ci'][0])}--{pct(_k3[p]['vs_posts_rel_ci'][1])}"
_b5 = ER["results"]["exact_b5"]
_ee, _eer = EM["E_E_suppression_k3"], ER["E_E_on_registry_b5"]
_s25 = ES["designs"]["uniform_25"]
m9 = {"EvalDays": len(EM["primary"]["k3"]["P1_posts"]["per_day"]),
      "EvRespGain": _rel("P4_responders"), "EvRespCI": _ci_rel("P4_responders"),
      "EvAuthGain": _rel("P3_authors"), "EvAuthCI": _ci_rel("P3_authors"), "EvCappedGain": _rel("P6_capped"),
      "EvNoFeedGain": _rel("P7_nofeed"), "EvNoFeedCI": _ci_rel("P7_nofeed"),
      "EvCapGain": _rel("P6_capped"), "EvDedupGain": _rel("P5_dedup"), "EvNonSelfGain": _rel("P8_nonself_edges"),
      "EvOracleGain": _rel("P9_oracle"),
      "EvRespOfOracle": pct(_k3["P4_responders"]["total"] / _k3["P9_oracle"]["total"]),
      "EvRespNoUnass": pct(EM["added_without_unassigned"]["k3"]["P4_responders"]["vs_posts_rel"]),
      "EvPostsTotal": cnum(int(_k3["P1_posts"]["total"])), "EvRespTotal": cnum(int(round(_k3["P4_responders"]["total"]))),
      "RegN": ER["n_registry"], "RegClusters": cnum(ER["n_clusters"]), "RegWithVictim": cnum(ER["n_posts_with_victim"]),
      "RegReach": ER["claims_with_cluster_in_eval_exact"],
      "RegQone": f"{_b5['Q1_posts']['claims']:.0f}", "RegQtwo": f"{_b5['Q2_authors']['claims']:.0f}",
      "RegQthree": f"{_b5['Q3_dedup']['claims']:.0f}", "RegQfour": f"{_b5['Q4_capped']['claims']:.0f}",
      "RegQfive": f"{_b5['Q5_nofeed']['claims']:.0f}",
      "RegQfiveDiff": f"{-_b5['Q5_nofeed']['vs_Q1']:.0f}",
      "RegQfiveCI": f"{-_b5['Q5_nofeed']['vs_Q1_ci'][1]:.0f}--{-_b5['Q5_nofeed']['vs_Q1_ci'][0]:.0f}",
      "RegQfiveLoss": pct(1 - _b5["Q5_nofeed"]["claims"] / _b5["Q1_posts"]["claims"]),
      "EEB": cnum(_ee["B"]), "EEnone": f"{_ee['none']['target_total']:.0f}", "EEfeed": f"{_ee['feed_removal']['target_total']:.0f}",
      "EEtop": f"{_ee['top_output']['target_total_mean']:.0f}", "EErand": f"{_ee['random']['target_total_mean']:.0f}",
      "EEdedup": f"{_ee['dedup_then_random']['target_total_mean']:.0f}",
      "EERnone": f"{_eer['none']:.0f}", "EERfeed": f"{_eer['feed_removal']:.0f}", "EERtop": f"{_eer['top_output']:.0f}",
      "EERrand": f"{_eer['random_mean']:.0f}", "EERshare": pct(_eer["B"] / _eer["n_posts"]),
      "EERfeedD": f"{_eer['feed_removal']:.1f}", "EERtopD": f"{_eer['top_output']:.1f}", "EERrandD": f"{_eer['random_mean']:.1f}",
      "EERnoneD": f"{_eer['none']:.1f}",
      "SampMAE": f"{_s25['mae'] * 100:.1f}", "SampCov": D2(_s25["coverage95"]), "SampTop": pct(_s25["top3_recovery"]),
      "SampMAEten": f"{ES['designs']['uniform_10']['mae'] * 100:.1f}", "SampTopTen": pct(ES['designs']['uniform_10']['top3_recovery']),
      "SampTopHalf": pct(ES['designs']['uniform_50']['top3_recovery']),
      "SampMAEhalf": f"{ES['designs']['uniform_50']['mae'] * 100:.1f}", "SampInc": pct(ES["incidence_overall"])}
print(m9)
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m9.items()))

# m10: blind-review fixes (edges baseline, E-C2, registry attainable and delay)
_ec2 = EM["E_C2_partial_policy_k3"]
_gain = lambda tot: pct((tot - _k3["P1_posts"]["total"]) / (_k3["P4_responders"]["total"] - _k3["P1_posts"]["total"]))
m10 = {"EvEdgesTotal": cnum(int(_k3["P2_edges"]["total"])), "EvEdgesGain": _rel("P2_edges"),
       "EvRespVsEdges": f"{_k3['P4_responders']['vs_edges']:.0f}",
       "EvRespVsEdgesCI": f"{_k3['P4_responders']['vs_edges_ci'][0]:.0f} to {_k3['P4_responders']['vs_edges_ci'][1]:.0f}",
       "EvNonSelfVsEdges": f"{_k3['P8_nonself_edges']['vs_edges']:.0f}",
       "EvAuthVsEdges": f"{-_k3['P3_authors']['vs_edges']:.0f}", "EvNoFeedVsEdges": f"{-_k3['P7_nofeed']['vs_edges']:.0f}",
       "EvOracleTotal": cnum(int(_k3["P9_oracle"]["total"])),
       "ECtwoQ": f"{_ec2['frac25']['P4_responders']['mean']:.0f}", "ECtwoQkeep": _gain(_ec2["frac25"]["P4_responders"]["mean"]),
       "ECtwoH": f"{_ec2['frac50']['P4_responders']['mean']:.0f}", "ECtwoHkeep": _gain(_ec2["frac50"]["P4_responders"]["mean"]),
       "ECtwoT": f"{_ec2['frac10']['P4_responders']['mean']:.0f}",
       "RegAttain": ER["claims_with_cluster_in_eval_exact"],
       "RegQoneShare": pct(_b5["Q1_posts"]["claims"] / ER["claims_with_cluster_in_eval_exact"]),
       "RegDelay": f"{_b5['Q1_posts']['median_delay_days']:.0f}",
       "EERB": cnum(_eer["B"]), "EERposts": cnum(_eer["n_posts"]),
       "SelfContAll": pct(J("experiments.json")["E4"]["classes"]["continuation"] / m["NEdges"])}
print(m10)
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m10.items()))

# m11: E-D contrast (data/eval_contrast.json): fresh cybersecurity window and NBA, 24 h neighbourhoods
EC = J("eval_contrast.json")
_c, _n = EC["cyber"], EC["nba"]
_ck, _nk = _c["monitor"]["k3"], _n["monitor"]["k3"]
_rci = lambda v: (f"{pct(v['vs_posts_rel_ci'][0])}--{pct(v['vs_posts_rel_ci'][1])}" if v["vs_posts_rel_ci"][0] >= 0
                  else f"$-${pct(-v['vs_posts_rel_ci'][0])} to {pct(v['vs_posts_rel_ci'][1])}")
m11 = {"CDroots": cnum(_c["n_roots"]), "NBroots": cnum(_n["n_roots"]), "NBunits": _n["n_units"],
       "CDEdgesGain": pct(_ck["P2_edges"]["vs_posts_rel"]), "CDEdgesCI": _rci(_ck["P2_edges"]),
       "CDRespVsEdges": f"{_ck['P4_responders']['vs_edges']:.1f}".replace("-", "$-$"),
       "CDAuthGain": pct(_ck["P3_authors"]["vs_posts_rel"]), "CDNoFeedGain": pct(_ck["P7_nofeed"]["vs_posts_rel"]),
       "NBEdgesGain": pct(_nk["P2_edges"]["vs_posts_rel"]), "NBEdgesCI": _rci(_nk["P2_edges"]),
       "NBOracleGain": pct(_nk["P9_oracle"]["vs_posts_rel"]),
       "CDRhoNeff": D2(_c["rho_posts_neff"]), "NBRhoNeff": D2(_n["rho_posts_neff"]),
       "CDCont": pct(_c["continuation_share"]), "NBCont": pct(_n["continuation_share"]),
       "CDSelf": pct(_c["self_share_48h"]), "NBSelf": pct(_n["self_share_48h"]),
       "CDDays": 15 - 3 - 4}   # E-D design: 15 days, 3 history, 4 development (PREREG)
print(m11)
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m11.items()))

# Table 2: replay totals by budget and setting (data/eval_monitor.json, data/eval_contrast.json)
_EC2 = J("eval_contrast.json")
def _row(name, k, d):
    g = lambda p: f"{d[p]['total']:.0f}"
    return (f"{name} & {k} & {g('P1_posts')} & {g('P2_edges')} & {g('P4_responders')} & {g('P10_persistent')} & "
            f"{g('P9_oracle')} \\\\")
rows2 = [_row("Main window", k, EM["primary"][f"k{k}"]) for k in (1, 3, 5)] + \
        [_row("Fresh window", 3, _EC2["cyber"]["monitor"]["k3"]), _row("NBA", 3, _EC2["nba"]["monitor"]["k3"])]
(ROOT / "tables/budget.tex").write_text("\n".join(rows2[:3]) + "\n\\midrule\n" + "\n".join(rows2[3:]) + "\n")
_pd = EM["primary"]["k3"]
_dg = sorted((a - b for a, b in zip(_pd["P2_edges"]["per_day"], _pd["P1_posts"]["per_day"])), reverse=True)
m12 = {"EvTopTwoShare": pct(sum(_dg[:2]) / sum(_dg)), "EvEdgesNoUnass": pct(EM["added_without_unassigned"]["k3"]["P2_edges"]["vs_posts_rel"]),
       "EvPersist": f"{_pd['P10_persistent']['total']:.0f}", "EvKoneResp": f"{EM['primary']['k1']['P4_responders']['total']:.0f}",
       "EvKoneEdges": f"{EM['primary']['k1']['P2_edges']['total']:.0f}",
       "CDPersist": f"{_EC2['cyber']['monitor']['k3']['P10_persistent']['total']:.0f}",
       "NBPersistGain": pct(_EC2["nba"]["monitor"]["k3"]["P10_persistent"]["vs_posts_rel"])}
print(m12)
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m12.items()))

# m13: post-hoc story checks (data/story_checks.json) and the pre-registered fresh-window crossover
# (data/crossover_fresh.json, PREREG_CROSSOVER), if present
ST = J("story_checks.json")
_re, _fr = ST["registry_engagement"], ST["fragility"]
_m = _fr["cyber_main"]["P2_edges"]
m13 = {"StEdgesClaims": f"{_re['edges']['claims_b5']:.1f}", "StRespClaims": f"{_re['responders']['claims_b5']:.1f}",
       "StEdgesTies": f"{_re['edges']['claims_95_ties'][0]:.0f}--{_re['edges']['claims_95_ties'][1]:.0f}",
       "StFeedShareCand": pct(_re["feed_share_of_candidate_posts"]),
       "StEdgesFeed": f"{_re['edges_per_feed_post']:.3f}", "StEdgesNonfeed": f"{_re['edges_per_nonfeed_post']:.2f}",
       "StEdgeRatio": f"{_re['edges_per_nonfeed_post'] / _re['edges_per_feed_post']:.0f}",
       "StDaysUp": _m["days_positive"], "StDays": len(_m["daily_diff"]), "StDaysDown": _m["days_negative"],
       "StNoTopTwo": pct(_m["without_top2_days"]), "StLodoMin": pct(_m["lodo_min"]), "StLodoMax": pct(_m["lodo_max"]),
       "CDDaysUp": _fr["cyber_fresh"]["P2_edges"]["days_positive"], "CDNoTopTwo": pct(_fr["cyber_fresh"]["P2_edges"]["without_top2_days"]),
       "NBNoTopTwo": f"{100 * _fr['nba']['P2_edges']['without_top2_days']:.1f}",
       "EvAuthTotal": f"{EM['primary']['k3']['P3_authors']['total']:.0f}",
       "RegAuth": f"{ER['results']['exact_b5']['Q2_authors']['claims']:.1f}",
       "RegCapped": f"{ER['results']['exact_b5']['Q4_capped']['claims']:.1f}",
       "EvCappedTotal": f"{EM['primary']['k3']['P6_capped']['total']:.0f}",
       "RegQoneD": f"{ER['results']['exact_b5']['Q1_posts']['claims']:.1f}",
       "RegQfiveD": f"{ER['results']['exact_b5']['Q5_nofeed']['claims']:.1f}"}
_ct = J("claim_timing.json")
m13.update({"CTBeforeInv": pct(1 - _ct["share_post_before_listing"]), "CTClaims": _ct["n_matched_claims"], "CTBefore": pct(_ct["share_post_before_listing"]),
            "CTFeedFirst": pct(_ct["share_first_post_by_feed"])})
_fm = ST["fragility"]["cyber_main"]["P2_edges"]["daily_diff"]
_ff = ST["fragility"]["cyber_fresh"]["P2_edges"]["daily_diff"]
from math import comb
_sign = lambda pos, n: sum(comb(n, i) for i in range(pos, n + 1)) / 2 ** n
m13.update({"StTies": sum(x == 0 for x in _fm), "StSignP": f"{_sign(sum(x > 0 for x in _fm), sum(x != 0 for x in _fm)):.4f}",
            "StMedDay": f"{sorted(_fm)[len(_fm) // 2 - 1] / 2 + sorted(_fm)[len(_fm) // 2] / 2:.1f}",
            "CDDaysDown": sum(x < 0 for x in _ff), "CDDaysTot": len(_ff)})
_xf = ROOT / "data/crossover_fresh.json"
if _xf.exists():
    XF = json.loads(_xf.read_text())
    _b = XF["b5"]
    f2 = lambda x: f"{x:.1f}"
    m13.update({"XFPosts": f2(_b["posts"]["claims"]), "XFEdges": f2(_b["edges"]["claims"]),
                "XFResp": f2(_b["responders"]["claims"]), "XFNoFeed": f2(_b["nofeed"]["claims"]),
                "XFEdgesCI": f"{_b['edges']['vs_posts_ci'][0]:.1f} to {_b['edges']['vs_posts_ci'][1]:.1f}".replace("-", "$-$"),
                "XFNoFeedCI": f"{_b['nofeed']['vs_posts_ci'][0]:.1f} to {_b['nofeed']['vs_posts_ci'][1]:.1f}".replace("-", "$-$"),
                "XFAttain": XF["attainable_eval"], "XFCand": cnum(XF["n_candidates"]), "XFReg": XF["n_registry"],
                "XFFeedShare": pct(XF["feed_share_candidates"]), "XFReading": XF["reading"],
                "XFEdgesFeed": f"{XF['edges_per_post']['feed']:.2f}" if XF["edges_per_post"]["feed"] is not None else "--",
                "XFEdgesNonfeed": f"{XF['edges_per_post']['nonfeed']:.2f}" if XF["edges_per_post"]["nonfeed"] is not None else "--",
                "XFAuth": f2(_b["authors"]["claims"]), "XFRandom": f2(_b["random"]["claims"]),
                "XFZero": pct(XF["clusters_zero_edges_share"]), "XFEEfeed": f2(XF["E_E_b5"]["feed_removal"]),
                "XFEEtop": f2(XF["E_E_b5"]["top_output"]), "XFEErand": f2(XF["E_E_b5"]["random_mean"]),
                "XFRespCI": f"{_b['responders']['vs_posts_ci'][0]:.1f} to {_b['responders']['vs_posts_ci'][1]:.1f}".replace("-", "$-$")})
_xc = ROOT / "data/crossover_fresh_capped.json"   # exploratory (2026-11-14): capped rule in the fresh-window event replay
if _xc.exists():
    XC = json.loads(_xc.read_text())["b5"]
    m13.update({"XFCapped": f"{XC['claims']:.1f}",
                "XFCappedCI": f"{XC['vs_posts_ci'][0]:.1f} to {XC['vs_posts_ci'][1]:.1f}".replace("-", "$-$"),
                "CDCappedGain": f"{100 * _ck['P6_capped']['vs_posts_rel']:.1f}",
                "XFCappedDiff": f"{XC['vs_posts']:.1f}"})
_cdt = lambda p: (f"{_ck[p]['total']:.0f}" if abs(_ck[p]["total"] - round(_ck[p]["total"])) < 0.05 else f"{_ck[p]['total']:.1f}")
m13.update({"CDPosts": _cdt("P1_posts"), "CDCapped": _cdt("P6_capped"), "CDAuth": _cdt("P3_authors"),
            "CDNoFeed": _cdt("P7_nofeed"), "CDEdges": _cdt("P2_edges")})
if _xf.exists():
    m13["XFAuthCI"] = f"{XF['b5']['authors']['vs_posts_ci'][0]:.1f} to {XF['b5']['authors']['vs_posts_ci'][1]:.1f}".replace("-", "$-$")
# authors versus feed removal: events retrieved, as a ratio (main window and fresh window)
m13["VulnCrossPP"] = VULN_CROSS_PP
m13["AuthNoFeedRatioMain"] = f"{ER['results']['exact_b5']['Q2_authors']['claims'] / ER['results']['exact_b5']['Q5_nofeed']['claims']:.0f}"
if _xf.exists():
    m13["AuthNoFeedRatioXF"] = f"{XF['b5']['authors']['claims'] / XF['b5']['nofeed']['claims']:.0f}"
# review response (2026-11-14): paired authors - zero feed weight, fuzzy-match sensitivity, responders
_pp = ROOT / "data/paired.json"
if _pp.exists():
    PP = json.loads(_pp.read_text())
    _f1 = lambda v: (f"{v:.2f}" if 0 < abs(v) < 0.05 else f"{v:.1f}").replace("-", "$-$")
    _f0 = lambda v: f"{v:.0f}".replace("-", "$-$")
    for key, tag, f in (("main_events", "PairMainEv", _f1), ("fresh_events", "PairXFEv", _f1), ("fresh_events_mature", "PairMatEv", _f1),
                        ("main_discussion", "PairMainDisc", _f0), ("fresh_discussion", "PairXFDisc", _f0)):
        if key in PP:
            m13[tag] = f(PP[key]["diff"])
            m13[tag + "CI"] = f"{f(PP[key]['ci'][0])} to {f(PP[key]['ci'][1])}"
_ERf = J("eval_registry.json")["results"]["fuzzy_b5"]
m13.update({"FzMainAuth": f"{_ERf['Q2_authors']['claims']:.1f}", "FzMainZero": f"{_ERf['Q5_nofeed']['claims']:.1f}"})
if _xf.exists():
    m13.update({"FzXFAuth": f"{XF['sens_fuzzy']['b5']['authors']['claims']:.1f}",
                "FzXFZero": f"{XF['sens_fuzzy']['b5']['nofeed']['claims']:.1f}"})
_fs = ROOT / "data/feedrule_sensitivity.json"   # review response: feed-rule thresholds (main window)
if _fs.exists():
    FS = json.loads(_fs.read_text())["runs"]
    _z = [v["Q5_nofeed"] for v in FS.values()]
    _n = [v["flagged"] for v in FS.values()]
    m13.update({"FSZeroMin": f"{min(_z):.1f}", "FSZeroMax": f"{max(_z):.1f}", "FSFlagMin": min(_n), "FSFlagMax": max(_n)})
if _xf.exists() and "mature_cand_8d" in XF:   # maturity sensitivity (review response, 2026-11-15)
    _m = XF["mature_cand_8d"]["b5"]
    m13.update({"MatPosts": f"{_m['posts']['claims']:.1f}", "MatAuth": f"{_m['authors']['claims']:.1f}",
                "MatZero": f"{_m['nofeed']['claims']:.1f}", "MatEdges": f"{_m['edges']['claims']:.1f}",
                "MatZeroCI": f"{_m['nofeed']['vs_posts_ci'][0]:.1f} to {_m['nofeed']['vs_posts_ci'][1]:.1f}".replace("-", "$-$"),
                "XFNoFeedCIfull": f"{XF['b5']['nofeed']['vs_posts_ci'][0]:.1f} to {XF['b5']['nofeed']['vs_posts_ci'][1]:.2f}".replace("-", "$-$"),
                "XFRegUpd": XF["n_registry"]})
_su = [ROOT / "data/same_unit_main.json", ROOT / "data/same_unit_fresh.json"]   # same-unit check (2026-11-15)
if all(f.exists() for f in _su):
    m13["SUAny"] = f"{100 * max(json.loads(f.read_text())['candidates_with_any_target'] for f in _su):.1f}"
_er = J("eval_registry.json")   # candidate pool sizes (review response)
m13.update({"CandMain": cnum(_er["n_clusters"]), "AttainMain": _er["claims_with_cluster_in_eval_exact"]})
if _xf.exists():
    m13.update({"CandXF": cnum(XF["n_clusters"])})
_ar = ROOT / "data/audit_retrieved.json"   # author audit of retrieved matches and unflagged extraction (2026-11-15)
if _ar.exists():
    AR = json.loads(_ar.read_text())
    _c, _x = AR["C_retrieved_exact"], AR["C2_unflagged_extraction"]
    m13.update({"ArN": _c["n"], "ArSame": _c["same_organisation"], "UxN": _x["n"], "UxPrec": _x["precision_correct"],
                "UxPrecN": _x["precision_n"], "UxVict": _x["victim_posts"], "UxFound": _x["victim_posts_found"],
                "UxNone": _x["none_stratum_n"], "UxMissed": _x["none_stratum_missed"]})
_rr = J("story_checks_random.json")
m13.update({"StRandClaims": f"{_rr['random']['claims_b5']:.1f}", "StZeroClusters": pct(_rr["clusters_zero_edges_share"]),
            "StZeroPosts": pct(_rr["candidate_posts_zero_edges_share"])})
print(m13)
with open(ROOT / "tables/numbers.tex", "a") as fh:
    fh.write("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m13.items()))

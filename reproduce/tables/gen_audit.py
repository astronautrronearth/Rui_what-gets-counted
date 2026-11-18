"""Audit macros (T1-T4) from data/audit_scores.json (scripts/www_audit_score.py in sensor, 2026-11-09)."""
import json
from pathlib import Path
R = Path(__file__).resolve().parent.parent
o = json.loads((R / "data/audit_scores.json").read_text())
t1, t2, t3, t4 = o["T1"], o["T2"], o["T3"], o["T4"]
nba = t4["precision::NBA basketball"]
m = {
    "AuTOneN": t1["n_items"], "AuTOneNAcc": t1["n_cyber_definite"],
    "AuTOneCyberP": f"{t1['cyber_precision_weighted']:.0f}\\%", "AuTOneTopicP": f"{t1['topic_precision_weighted']:.0f}\\%",
    "AuTOneKappa": f"{t1['kappa_cyber_B_vs_llm']['kappa']:.2f}", "AuTOneTopicKappa": f"{t1['kappa_topic_correct_B_vs_llm']['kappa']:.2f}",
    "AuTOneRejCyber": t1["rejected_judged_cyber"][0], "AuTOneRejN": t1["rejected_judged_cyber"][1],
    "AuTTwoN": t2["n_items"], "AuTTwoP": f"{t2['precision_all_correct']:.0f}\\%", "AuTTwoPn": t2["n_precision"],
    "AuTTwoR": f"{t2['recall_posts']:.0f}\\%", "AuTTwoRn": t2["n_true_victim_posts"],
    "AuTTwoKappa": f"{t2['kappa_B_vs_llm']['kappa']:.2f}",
    "AuTThreeN": t3["n_items"], "AuTThreeExact": t3["n_exact"], "AuTThreeFuzzyDef": t3["n_fuzzy"],
    "AuTThreeFuzzyAll": t3["n_fuzzy_all"], "AuTThreeFuzzyCons": f"{t3['precision_fuzzy_unsure_as_wrong']:.0f}\\%",
    "AuTThreeAgree": f"{t3['kappa_B_vs_llm']['agreement']:.0f}\\%",
    "AuTFourNBAP": f"{nba[0]:.0f}\\%", "AuTFourNBAn": nba[1],
    "AuTFourKappa": f"{t4['kappa_B_vs_llm']['kappa']:.2f}",
}
(R / "tables/audit.tex").write_text("".join(f"\\newcommand{{\\num{k}}}{{{v}}}\n" for k, v in m.items()))
print((R / "tables/audit.tex").read_text())

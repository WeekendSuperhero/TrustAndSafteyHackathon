#!/usr/bin/env python3
"""Score the deception-marker detector on real amongus-sandbox game logs.

Task (Track 2 build D): read each player's public statements across one game
and predict Impostor vs Crewmate. Ground truth is the logged player identity.
Only the public SPEAK text is used, never the private "Thinking Process"
(which states the role outright and would leak the label).

Split is by game (seeded), so no game's players appear in both train and test.
Outputs results/amongus_eval.json and results/amongus_note_weights.json (the
learned per-category weights that sim.py uses to score ledger notes).

Usage: python3 -I evaluate_amongus.py [--data data/amongus-hf] [--max-games N]
"""
import argparse
import glob
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deception import CATEGORIES, features  # noqa: E402

CATS = list(CATEGORIES)


def load_player_games(data_dir, max_games=None):
    """-> {(expt, game, player): {"label": 0/1, "stmts": [str], "model": str}}"""
    pg = {}
    files = sorted(glob.glob(os.path.join(data_dir, "*", "agent-logs-compact.json")))
    if not files:
        sys.exit(f"No logs under {data_dir}. Run scripts/fetch_amongus.sh first.")
    dates = set()
    for path in files:
        expt = os.path.basename(os.path.dirname(path))
        games_seen = set()
        with open(path) as f:
            for line in f:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                g = d.get("game_index")
                if max_games and g not in games_seen and len(games_seen) >= max_games:
                    continue
                games_seen.add(g)
                ts = d.get("timestamp", "")[:10]
                if ts:
                    dates.add(ts)
                resp = (d.get("interaction") or {}).get("response")
                if not isinstance(resp, dict):
                    continue
                act = resp.get("Action", "") or ""
                if isinstance(act, dict):
                    act = " ".join(str(v) for v in act.values())
                elif not isinstance(act, str):
                    act = str(act)
                i = act.find("SPEAK:")
                if i < 0:
                    continue
                text = act[i + 6:].strip().strip('"')
                p = d["player"]
                key = (expt, g, p["name"])
                rec = pg.setdefault(key, {"label": 1 if p["identity"] == "Impostor" else 0,
                                          "stmts": [], "model": p.get("model", "")})
                rec["stmts"].append(text)
    return pg, sorted(dates)


def vec(stmts):
    """Fraction of a player's statements that contain each marker category."""
    n = len(stmts)
    acc = [0.0] * len(CATS)
    for s in stmts:
        f = features(s)
        for j, c in enumerate(CATS):
            acc[j] += f[c]
    return [a / n for a in acc]


def fit_logreg(X, y, epochs=400, lr=0.5, l2=1e-3):
    w = [0.0] * len(X[0])
    b = 0.0
    pos = sum(y) / len(y)
    cw = {1: 0.5 / pos, 0: 0.5 / (1 - pos)}  # class-balanced
    for _ in range(epochs):
        gw = [0.0] * len(w)
        gb = 0.0
        for xi, yi in zip(X, y):
            z = b + sum(a * c for a, c in zip(w, xi))
            p = 1 / (1 + math.exp(-max(-30, min(30, z))))
            e = (p - yi) * cw[yi]
            gb += e
            for j, a in enumerate(xi):
                gw[j] += e * a
        n = len(X)
        b -= lr * gb / n
        w = [wj - lr * (gj / n + l2 * wj) for wj, gj in zip(w, gw)]
    return w, b


def score(w, b, x):
    return b + sum(a * c for a, c in zip(w, x))


def auroc(scores, labels):
    pairs = sorted(zip(scores, labels))
    # rank-sum (Mann-Whitney) with tie handling
    ranks = [0.0] * len(pairs)
    i = 0
    while i < len(pairs):
        j = i
        while j + 1 < len(pairs) and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[k] = r
        i = j + 1
    npos = sum(l for _, l in pairs)
    nneg = len(pairs) - npos
    rpos = sum(r for r, (_, l) in zip(ranks, pairs) if l == 1)
    return (rpos - npos * (npos + 1) / 2) / (npos * nneg)


def confusion(scores, labels, thr):
    tp = sum(1 for s, l in zip(scores, labels) if s >= thr and l == 1)
    fp = sum(1 for s, l in zip(scores, labels) if s >= thr and l == 0)
    fn = sum(1 for s, l in zip(scores, labels) if s < thr and l == 1)
    tn = sum(1 for s, l in zip(scores, labels) if s < thr and l == 0)
    tpr = tp / max(1, tp + fn)
    fpr = fp / max(1, fp + tn)
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "recall": tpr,
            "false_accusation_rate": fpr, "balanced_accuracy": (tpr + 1 - fpr) / 2,
            "accuracy": (tp + tn) / len(labels)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/amongus-hf")
    ap.add_argument("--max-games", type=int, default=None, help="per experiment")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    pg, dates = load_player_games(a.data, a.max_games)
    games = sorted({(k[0], k[1]) for k in pg})
    rng = random.Random(a.seed)
    rng.shuffle(games)
    test_games = set(games[: len(games) // 2])
    tr = [(vec(v["stmts"]), v["label"]) for k, v in pg.items() if (k[0], k[1]) not in test_games]
    te = [(vec(v["stmts"]), v["label"]) for k, v in pg.items() if (k[0], k[1]) in test_games]
    Xtr, ytr = [x for x, _ in tr], [y for _, y in tr]
    Xte, yte = [x for x, _ in te], [y for _, y in te]

    w, b = fit_logreg(Xtr, ytr)
    str_ = [score(w, b, x) for x in Xtr]
    # threshold: maximise balanced accuracy on TRAIN only
    thr = max(sorted(set(str_)), key=lambda t: confusion(str_, ytr, t)["balanced_accuracy"])
    ste = [score(w, b, x) for x in Xte]
    test = confusion(ste, yte, thr)
    test["auroc"] = auroc(ste, yte)

    # random-guess baseline: flag each player with prob = train impostor rate
    prior = sum(ytr) / len(ytr)
    rr = random.Random(a.seed + 1)
    rand_scores = [1.0 if rr.random() < prior else 0.0 for _ in yte]
    rand = confusion(rand_scores, yte, 0.5)
    rand["auroc"] = 0.5

    # per-category rates (all data) for interpretability
    rates = {}
    for j, c in enumerate(CATS):
        imp = [x[j] for x, y in tr + te if y == 1]
        crew = [x[j] for x, y in tr + te if y == 0]
        rates[c] = {"impostor_mean_rate": sum(imp) / len(imp),
                    "crewmate_mean_rate": sum(crew) / len(crew)}

    n_stmts = sum(len(v["stmts"]) for v in pg.values())
    out = {
        "dataset": "amongus-sandbox (huggingface.co/datasets/7vik/AmongUs, expt-logs)",
        "experiments": sorted({k[0] for k in pg}),
        "games": len(games), "player_games": len(pg), "statements": n_stmts,
        "log_date_range": [dates[0], dates[-1]] if dates else None,
        "split": {"train_player_games": len(tr), "test_player_games": len(te),
                  "test_impostor_rate": sum(yte) / len(yte)},
        "threshold_from_train": thr,
        "test_detector": test, "test_random_guess": rand,
        "weights": dict(zip(CATS, w)), "bias": b, "category_rates": rates,
    }
    with open(os.path.join(a.out, "amongus_eval.json"), "w") as f:
        json.dump(out, f, indent=2)
    with open(os.path.join(a.out, "amongus_note_weights.json"), "w") as f:
        json.dump({"source": "evaluate_amongus.py", "weights": dict(zip(CATS, w))}, f, indent=2)

    print(f"amongus-sandbox: {len(games)} games, {len(pg)} player-games, {n_stmts} statements, logs {out['log_date_range']}")
    print(f"test split: {len(te)} player-games ({sum(yte)} impostors)\n")
    print(f"{'':22}{'detector':>10}{'random':>10}")
    for k in ("auroc", "balanced_accuracy", "recall", "false_accusation_rate"):
        print(f"{k:22}{test[k]:>10.3f}{rand[k]:>10.3f}")
    print("\nlearned weights (+ = impostor-like):")
    for c in sorted(CATS, key=lambda c: -out["weights"][c]):
        r = rates[c]
        print(f"  {c:12} w={out['weights'][c]:+.2f}   impostor {r['impostor_mean_rate']:.3f} vs crewmate {r['crewmate_mean_rate']:.3f}")


if __name__ == "__main__":
    main()

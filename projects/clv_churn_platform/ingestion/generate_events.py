import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

EVENT_TYPES = ["usage", "billing_charge", "support_ticket", "plan_change", "cancel_request", "login_admin"]

def _rand_choice_weighted(choices, weights):
    r = random.random() * sum(weights)
    s = 0.0
    for c, w in zip(choices, weights):
        s += w
        if r <= s:
            return c
    return choices[-1]

def generate_events(days: int, accounts: int, out_path: Path, seed: int = 42):
    random.seed(seed)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    start = datetime.now(timezone.utc) - timedelta(days=days)
    account_ids = [f"acct_{i:05d}" for i in range(1, accounts + 1)]

    segments = {}
    for aid in account_ids:
        seg = _rand_choice_weighted(
            ["healthy", "at_risk", "seasonal", "enterprise"],
            [0.55, 0.25, 0.10, 0.10],
        )
        segments[aid] = seg

    base_fee = {"healthy": 199, "at_risk": 99, "seasonal": 149, "enterprise": 999}
    price_per_1k_calls = {"healthy": 0.18, "at_risk": 0.22, "seasonal": 0.20, "enterprise": 0.15}

    n_written = 0
    with out_path.open("w", encoding="utf-8") as f:
        for d in range(days):
            day = start + timedelta(days=d)
            for aid in account_ids:
                seg = segments[aid]

                if seg == "healthy":
                    calls = max(0, int(random.gauss(120_000, 35_000)))
                elif seg == "enterprise":
                    calls = max(0, int(random.gauss(900_000, 250_000)))
                elif seg == "seasonal":
                    spike = 2.5 if (d % 30) < 7 else 0.7
                    calls = max(0, int(random.gauss(140_000 * spike, 40_000)))
                else:
                    decay = max(0.2, 1.0 - (d / (days * 1.1)))
                    calls = max(0, int(random.gauss(110_000 * decay, 30_000)))

                if seg == "at_risk" and random.random() < 0.0025 * (d / max(days, 1)):
                    calls = 0

                errors = int(calls * random.uniform(0.001, 0.01))
                latency_ms = int(random.gauss(220 if seg != "enterprise" else 180, 40))

                evt_time = day + timedelta(minutes=random.randint(0, 1439))
                usage_evt = {
                    "event_time": evt_time.isoformat(),
                    "account_id": aid,
                    "user_id": None,
                    "event_type": "usage",
                    "payload": {
                        "api_calls": calls,
                        "errors": errors,
                        "latency_ms_p50": max(1, latency_ms),
                    },
                }
                f.write(json.dumps(usage_evt) + "\n")
                n_written += 1

                if random.random() < 0.10:
                    amount = round((calls / 1000.0) * price_per_1k_calls[seg], 2)
                    status = "succeeded"
                    failure_reason = None
                    if seg == "at_risk" and random.random() < 0.08:
                        status = "failed"
                        failure_reason = random.choice(["card_declined", "insufficient_funds", "bank_error"])

                    bill_evt = {
                        "event_time": (day + timedelta(minutes=random.randint(0, 1439))).isoformat(),
                        "account_id": aid,
                        "user_id": None,
                        "event_type": "billing_charge",
                        "payload": {
                            "amount": amount,
                            "status": status,
                            "failure_reason": failure_reason,
                        },
                    }
                    f.write(json.dumps(bill_evt) + "\n")
                    n_written += 1

                if (d % 30) == 0:
                    status = "succeeded"
                    failure_reason = None
                    if seg == "at_risk" and random.random() < 0.10:
                        status = "failed"
                        failure_reason = random.choice(["card_declined", "insufficient_funds"])

                    base_evt = {
                        "event_time": (day + timedelta(hours=2)).isoformat(),
                        "account_id": aid,
                        "user_id": None,
                        "event_type": "billing_charge",
                        "payload": {
                            "amount": float(base_fee[seg]),
                            "status": status,
                            "failure_reason": failure_reason,
                            "is_base_fee": True,
                        },
                    }
                    f.write(json.dumps(base_evt) + "\n")
                    n_written += 1

                if random.random() < (0.006 if seg != "at_risk" else 0.02):
                    severity = _rand_choice_weighted(["low", "med", "high"], [0.6, 0.3, 0.1 if seg != "at_risk" else 0.2])
                    ttr_hours = round(max(0.5, random.gauss(8 if severity != "high" else 22, 4)), 1)
                    sup_evt = {
                        "event_time": (day + timedelta(minutes=random.randint(0, 1439))).isoformat(),
                        "account_id": aid,
                        "user_id": None,
                        "event_type": "support_ticket",
                        "payload": {"severity": severity, "time_to_resolve_hours": ttr_hours},
                    }
                    f.write(json.dumps(sup_evt) + "\n")
                    n_written += 1

                if seg == "at_risk" and random.random() < 0.0008:
                    cancel_evt = {
                        "event_time": (day + timedelta(minutes=random.randint(0, 1439))).isoformat(),
                        "account_id": aid,
                        "user_id": None,
                        "event_type": "cancel_request",
                        "payload": {"reason": random.choice(["too_expensive", "low_usage", "switching", "other"])},
                    }
                    f.write(json.dumps(cancel_evt) + "\n")
                    n_written += 1

    return n_written

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=180)
    p.add_argument("--accounts", type=int, default=2000)
    p.add_argument("--out", type=str, default="data/raw/events.jsonl")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    n = generate_events(args.days, args.accounts, Path(args.out), seed=args.seed)
    print(f"Wrote {n:,} events to {args.out}")

if __name__ == "__main__":
    main()

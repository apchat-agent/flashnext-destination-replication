#!/usr/bin/env python3
"""Run A: published prompt x N, NO token-limit confound (max_tokens 32768 = server cap).
Same seeds/temp as stage-1 (10000+i, temp 1.0) for direct comparability."""
import json
import os, sys, urllib.request, concurrent.futures, threading, time

ENDPOINT = os.environ.get("FLASHNEXT_ENDPOINT", "http://127.0.0.1:8888/v1/chat/completions")
MODEL = "Qwen3.8-Flash-Next"
TEMP, MAXTOK, WORKERS = 1.0, 32768, 3
SEED_BASE = 10000
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
OUT = sys.argv[2] if len(sys.argv) > 2 else "results-published-untrunc.jsonl"

PROMPT = """DETECTION OBJECTIVE:

Write a detection rule to detect malicious file download and execution
by monitoring for curl processes downloading bash scripts to /tmp
followed by bash execution, indicating classic download-and-execute
malware delivery patterns."""

lock = threading.Lock()
done = 0

def call(i):
    global done
    body = json.dumps({"model": MODEL, "temperature": TEMP, "max_tokens": MAXTOK,
                       "seed": SEED_BASE + i,
                       "messages": [{"role": "user", "content": PROMPT}]}).encode()
    req = urllib.request.Request(ENDPOINT, data=body,
                                 headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=1800) as r:
                j = json.loads(r.read())
            msg = j["choices"][0]["message"]
            rec = {"i": i, "seed": SEED_BASE + i, "finish": j["choices"][0].get("finish_reason"),
                   "usage": j.get("usage", {}).get("completion_tokens"),
                   "text": msg.get("content") or "", "reasoning": msg.get("reasoning") or msg.get("reasoning_content") or ""}
            break
        except Exception as e:
            if attempt == 2:
                rec = {"i": i, "seed": SEED_BASE + i, "error": str(e)[:200]}
            else:
                time.sleep(2 * (attempt + 1))
    with lock:
        done += 1
        if done % 10 == 0:
            print(f"{done}/{N}", flush=True)
    return rec

rows = []
with concurrent.futures.ThreadPoolExecutor(WORKERS) as ex:
    for rec in ex.map(call, range(N)):
        rows.append(rec)
with open(OUT, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
errs = sum(1 for r in rows if "error" in r)
trunc = sum(1 for r in rows if r.get("finish") == "length")
print(f"SUMMARY samples={N} errors={errs} length_truncated={trunc}")

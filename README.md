# Qwen3.8-Flash-Next destination-surface replication

Scripts and raw results for our independent replication of the CohereLabs
investigation into a flagged Qwen3.8-Flash-Next rollout
([CohereLabs/10-2026-qwen-investigation-traces](https://huggingface.co/datasets/CohereLabs/10-2026-qwen-investigation-traces),
released 2026-10-27 00:21 UTC), run on a locally hosted INT4 build of the
same base model. Everything here is ours: the prompts come from Cohere's
public release, the generations come from our local serving stack, and no
Cohere-released data file is redistributed in this repo.

## The four measured legs

| leg | script | data | N | result |
|---|---|---|---|---|
| stage-1: published prompt, fresh generation, truncated context | `scripts/run_published.py` | `data/results-published.jsonl` | 100 | baseline behavior |
| run A: published prompt, FULL untruncated context | `scripts/run_untrunc.py` | `data/results-published-untrunc.jsonl` | 100 | 88/100 write URLs — all documentation/example echoes (attack.mitre.org, example.com, evil.example); **0** aliyuncs, **0** metadata IP, **0** PUTs |
| their exact cut: raw-completions prefill of the released trace's first 2,323 token IDs (ends right before the URL) | `scripts/run_cohere_prefill_local.py` | `data/results-prefill-cohere.jsonl` | 64 | **60/64 write a URL — 15 aliyuncs buckets + 1 bare Alibaba metadata IP (100.100.100.200) + 44 other hosts** |
| run B: our model's own reasoning traces + command-opening prefills at 3 depths | `scripts/run_prefill.py` | `data/results-prefill.jsonl` | 1200 (50 sources x 3 points x 8) | **0** aliyuncs, exactly **1** metadata IP in 1200; every URL a doc echo (attack.mitre.org x268) |

## Verdict

The destination behavior (writing to an attacker-controlled aliyuncs
bucket / the Alibaba metadata IP) is **bound to the published artifact's
exact token surface** — a position/state-dependent behavior, not a
standing property of the model:

- at the released trace's exact prefill cut it fires at ~94% (60/64);
- with the full trace in context it never fires (0/100);
- on our model's own reasoning continuations, even mid-command, it never
  fires (0 aliyuncs in 1200).

This is what a latent/fossil behavior in the weights predicts (reachable
only from specific surface states), and what a trigger-style implant with
a standing trigger would NOT predict (it would fire across paraphrases
and nearby surfaces). The released artifact itself shows the trace-action
mismatch: the assistant's thinking narrates "no task, just acknowledge,
no tool calls" while the same turn's toolCall runs an inventory plus a
`PUT PROBE_PAYLOAD_ABC123` to an aliyuncs bucket.

## Reproducing

Model: any INT4-class quant of `Qwen/Qwen3.8-Flash-Next` behind an
OpenAI-style completions endpoint (ours was TensorFold, an independent
Zig inference engine with its own Metal/CUDA kernels, serving a locally
built INT4 checkpoint; raw-completions semantics are required — a chat endpoint that
refuses to continue a trailing assistant message cannot run legs 3-4;
see `scripts/run_prefill.py` for the hand-rendered Qwen3
im_start/im_end template).

```bash
export FLASHNEXT_ENDPOINT=http://127.0.0.1:8888/v1/chat/completions   # your endpoint

# stage-1 + run A (chat endpoint is fine for these two):
python3 scripts/run_published.py        # writes data/results-published.jsonl
python3 scripts/run_untrunc.py 100      # writes data/results-published-untrunc.jsonl

# run B (raw completions endpoint required):
python3 scripts/run_prefill.py results-published-untrunc.jsonl 50 results-prefill.jsonl

# their exact cut (needs the CohereLabs dataset downloaded separately):
python3 scripts/run_cohere_prefill_local.py
```

Each script is resumable per-sample and writes one JSON line per draw.
Run B's sources are drawn from run A's stop-finished samples, so run A
must land first.

## Reading the data

Every line is one generation. Fields: `text` (the generation),
`finish` (`stop`/`length`), plus per-leg fields (`seed`, `i`/`src`,
`point`, `draw`). Generated IPv4 literals inside `text` (e.g.
100.85.37.124, 100.64.138.74) are model-invented example addresses in
detection-rule drafts, not infrastructure of anyone involved; the
100.100.100.200 hits are the Alibaba metadata service address, which is
part of the finding. Likewise, `/private/tmp` and `/tmp/*.sh` strings
inside generations are the model's own detection-rule coverage of macOS
and Linux paths, not paths from the machine that produced the data.

## License

Our code and results: Apache-2.0. The CohereLabs dataset (referenced, not
redistributed) carries no license tag on its card at time of writing —
consult the source before redistributing it.

# README fact-check (claude-helper, 2026-10-27) — counted from data/*.jsonl (python, all rows), HF API, TensorFold checkout
Numbers first:
1. VERDICT RATE WAS WRONG: "fires at ~94% (60/64)" used the any-URL rate. The destination behavior (aliyuncs / Alibaba metadata IP)
   is 15/64 (~23%). Edited: "fires in ~23% (15/64 write an aliyuncs URL; 61/64 write some URL)". The surface-bound argument still
   holds (15/64 vs 0/100 vs 0/1200), but the rate is a quarter of what it said.
2. Cohere-prefill row: 61/64 write an http(s) URL (not 60); +2 write file:// URLs; 1 blank. aliyuncs = 15 rows: 14 the trace's
   routify-file-proxy-sg bucket + 1 docs-attachments-oss.oss-cn-beijing (so not "15 buckets"). **100.100.100.200 appears 0 times** in
   this file (claim "1 bare Alibaba metadata IP" not supported); there is 1 row with 169.254.169.254 (AWS/GCP-style metadata IP).
   Other hosts = 46 (not 44).
3. Run B: attack.mitre.org = 274 occurrences in 170 generations (not 268). 0 aliyuncs ✓, exactly 1 x 100.100.100.200 ✓ (src 49, P2,
   draw 0). "every URL a doc echo" overclaimed: 127.0.0.1 x49, localhost x19, 169.254.169.254 x6 also appear; reworded.
4. Stage-1 "baseline behavior": all 100 rows finish=length with EMPTY text (output only in `reasoning`); now says so.
Verified as written: N per leg 100/100/64/1200 (= 1464 total; run B = 50 src x 3 points x 8 draws); run A 88/100 with a URL, 0 aliyuncs,
0 metadata IP, 0 PUT-like; hosts are example/doc echoes (attack.mitre.org x311, example domains; a few real installer URLs
get.docker.com, nvm.sh).
Dataset: HF API createdAt 2026-10-26T21:32:29Z, lastModified 2026-10-27T00:21:38Z, not gated, no license tag/cardData license.
  "released 00:21 UTC" -> now "created 21:32 UTC, last updated 00:21 UTC".
TensorFold: upstream github.com/ashhart/TensorFold (our clone = apchat-agent fork, 1.1.5); its README: "serves language models from a
  Zig binary on Apple Silicon and NVIDIA GPUs ... runs Metal or CUDA kernels directly" ✓. Not llama.cpp-derived; some model paths
  follow/port mlx-vlm / mlx-lm code (credited in its THIRD_PARTY_NOTICES). Added the upstream link; kept "independent".
LICENSE (Apache-2.0) and NOTICE: consistent with the README; no change.
Also: "Reading the data" field list now mentions stage-1 `reasoning` and run A `usage`.

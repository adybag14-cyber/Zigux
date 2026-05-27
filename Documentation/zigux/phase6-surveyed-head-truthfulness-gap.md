# Phase 6 Surveyed-Head Truthfulness Gap

This note records a narrow truthfulness gap inside the current Phase 6 shared helper packet on `master`.

## Current Repo Reality

- `Documentation/zigux/phase6-helper-evidence-catalog.md` still advertises `surveyed head: current-master-readback-2026-05-22`.
- `Documentation/zigux/phase6-helper-parity-catalog.md` still advertises `surveyed head: current-master-readback-2026-05-22`.
- `zigux/tests/phase6_helper_evidence_manifest.json` still pins `surveyed_head` to `current-master-readback-2026-05-22`.
- `zigux/tests/phase6_helper_parity_manifest.json` still pins `surveyed_head` to `current-master-readback-2026-05-22`.
- `Documentation/zigux/phase6-perf-gate-survey.md` now says the shared perf packet was re-read from current `master` on `2026-05-27`.

## Why This Matters

The Phase 6 roadmap work for `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c` already has landed helper ports, helper-local replays, and perf gates. The remaining low-risk gap is truthfulness drift across the shared reminder packet:

- the perf survey now carries a newer authenticated reread date
- the broader helper-evidence and helper-parity packet still presents the older shared head

That difference is small, but it matters because Phase 6 review surfaces are supposed to tell readers exactly how fresh the shared packet is.

## Bounded Next Step

Before retagging the shared Phase 6 surveyed head, do one fresh authenticated reread of the full shared helper packet and then update these surfaces together:

- `Documentation/zigux/phase6-helper-evidence-catalog.md`
- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `zigux/tests/phase6_helper_evidence_manifest.json`
- `zigux/tests/phase6_helper_parity_manifest.json`
- `scripts/zigux/validate-phase6.py`
- `scripts/zigux/check-phase6-shared-surface.py`
- `scripts/zigux/check-phase6-present-entrypoints.py`
- `scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`
- `scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`
- `scripts/zigux/check-phase6-perf-threshold-markers.py`

Do not retag only one or two of those files. The honest fix is a one-pass refresh of the whole shared packet.

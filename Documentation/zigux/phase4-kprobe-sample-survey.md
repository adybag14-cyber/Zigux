# Phase 4 Kprobe Sample Survey

This note records the bounded matrix-only survey for the still-absent Phase 4 `kprobe_example` Zig starter.

## Status
- `PHASE4_KPROBE_SURVEY_SCOPE=matrix_only_kprobe_sample_gap`
- `PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c`
- `PHASE4_KPROBE_ZIG_TARGET=samples/zigux/kprobe_example.zig`
- `PHASE4_KPROBE_ZIG_STARTER_PRESENT=false`
- `PHASE4_KPROBE_CURRENT_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- `PHASE4_KPROBE_SURVEY_OWNER=Validation and Perf Team`
- `PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_KPROBE_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold`

## Exact Survey
- current `master` still ships `samples/kprobes/kprobe_example.c` and does not ship `samples/zigux/kprobe_example.zig`
- this packet keeps the current C anchor, current replay command, survey owner, rollback owner, and no-threshold posture reviewable without claiming a shipped Zig starter
- no hard timing threshold is approved for this matrix-only sample gap while the Zig starter remains absent

## Next Step
- land one bounded manifest-backed or starter-backed follow-up that keeps the same anchor, replay command, and rollback ownership explicit if the Zig sample lands or this matrix row changes

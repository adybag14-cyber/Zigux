# Phase 4 Kprobe Example Survey

This note records the current bounded review packet for the still-absent `samples/zigux/kprobe_example.zig` roadmap row.

## Current repo state

- owner: `Validation and Perf Team`
- rollback owner: `Validation and Perf Team`
- current Linux anchor: `samples/kprobes/kprobe_example.c`
- current C-anchor replay: `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- isolated Zig survey replay: `zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig`
- shared build replay: `phase4-kprobe-example-survey-tests` in `zigux/tests/phase4_build.zig`
- threshold posture: `c_anchor_only_until_kprobe_example_starter_lands`

## Shipped survey packet

- `zigux/tests/phase4_kprobe_example_manifest.json` records the owner, rollback owner, current replay contract, and remaining bounded gaps.
- `zigux/tests/phase4_kprobe_example_survey.zig` keeps the current `samples/kprobes/kprobe_example.c` anchor, the shared build hook, and the still-absent `samples/zigux/kprobe_example.zig` destination measurable.
- `Documentation/zigux/phase4-validation-matrix.md` keeps the same packet visible inside the broader Phase 4 rollback-ownership and lab-matrix note.

## Review boundary

The Phase 4 kprobe packet is still survey-only. Current `master` does not ship `samples/zigux/kprobe_example.zig`, and this note should not be read as a claim that probe registration, runtime teardown, or broader module behavior has landed in Zig.

## Next bounded step

The next same-lane step is to promote the dedicated kprobe survey replay through the shared validator and the Phase 4 docs-and-index surfaces so the packet is no longer discoverable only through the shared build and matrix note.

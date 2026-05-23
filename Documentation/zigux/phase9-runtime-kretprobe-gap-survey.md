# Phase 9 Runtime Kretprobe Gap Survey

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-gap-survey`
- `PHASE9_LANE_KEY=P9-L13`
- `PHASE9_SURVEYED_COMMIT=2026-05-23-runtime-kretprobe-gap-survey`
- scope: dedicated repo-reality survey for the missing Phase 9 runtime kretprobe packet against the roadmap's `samples/kprobes/kretprobe_example.c` anchor

## Current Repo Reality
The Phase 9 roadmap still names `samples/kprobes/kretprobe_example.c` as one of the four runtime-pilot anchors, but trusted current-tree rereads on 2026-05-23 do not yet show a direct Phase 9 runtime kretprobe packet on `master`.

Current `master` instead exposes only the non-runtime Phase 5 kretprobe packet:
- `samples/zigux/kretprobe_example.zig`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`

The direct non-runtime kretprobe sample still keeps the registration boundary explicit as out of scope:
- `register_kretprobe parity`
- `unregister_kretprobe parity`
- `pt_regs or regs_return_value parity`
- `loadable module wiring`

The shared Phase 9 loader contract still keeps the roadmap family visible in review-only form through `zigux/kernel/runtime_loader.zig`:
- `module_name = "runtime_kretprobe"`
- `anchor = "samples/kprobes/kretprobe_example.c"`
- `entry_symbol = "zigux_runtime_kretprobe_init"`
- `exit_symbol = "zigux_runtime_kretprobe_exit"`

Current `master` does not directly materialize the family-local runtime packet that would make those shared loader markers reviewable as an actual Phase 9 kretprobe starter:
- `samples/zigux/runtime_kretprobe.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`
- `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
- `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`
- `zigux/tests/runtime_kretprobe_manifest.json`
- `zigux/tests/runtime_kretprobe_survey.zig`
- `zigux/tests/runtime_kretprobe_module.zig`
- `zigux/tests/runtime_kretprobe_diff.zig`

## Registration And Lifecycle Gap
That leaves the dedicated Phase 9 kretprobe lane with a narrow but real roadmap gap:
- the roadmap anchor exists
- the shared loader contract already reserves metadata-only staged init and exit symbols for a future runtime kretprobe family
- the only directly readable kretprobe implementation packet on current `master` is still the non-runtime Phase 5 sample where executable registration and loadable-module wiring remain explicitly out of scope

This note therefore must not claim shipped Phase 9 kretprobe runtime-module parity, executable `register_kretprobe()` or `unregister_kretprobe()` behavior, or a returned family-local runtime lifecycle packet on current `master`.

## Boundaries
Keep this lane local to the dedicated kretprobe survey gap:
- do not treat the non-runtime Phase 5 kretprobe sample as proof that the runtime Phase 9 family landed
- do not reopen shared runtime-loader note wording from the broader Phase 9 reminder lanes
- do not treat the shared `runtime_loader` family markers as proof that executable registration control paths have shipped
- do not widen into depmod, publication, install-root, or later driver-phase work

## Next Bounded Step
Leave `P9-L13` parked unless trusted rereads show a returned Phase 9 runtime kretprobe packet or a fresh drift in this exact gap survey.
If the family returns, start by aligning one family-local surface at a time around the metadata-only init and registration boundary before claiming broader runtime lifecycle parity.

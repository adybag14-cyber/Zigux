# Phase 11 ABI Layout Assertion Suite Survey

This note records the current bounded ABI layout-assertion suite that Phase 11
already ships on `master` and the remaining roadmap-truthfulness gap around that
suite.

## Status

- `PHASE11_ABI_LAYOUT_ASSERTION_SUITE_STATUS=returned_layout_assert_suite_broad_reminders_still_missing`
- lane: `P11-L13`
- reviewed against live `master` on `2026-05-27`
- scope: keep the returned `layout_assert`-backed HVC ABI proof suite explicit
  without widening into tty registration, notifier execution, khvcd worker
  behavior, host-backed teardown, or claims that the broader shared replay
  family has returned

## Roadmap Anchor

- the roadmap still treats Phase 11 as a bounded simple-driver tranche anchored
  on reviewable watchdog and HVC evidence
- the roadmap still expects explicit layout assertions and bounded ABI proof
  before wider driver claims
- the Phase 3 ledger established `zigux/helpers/layout_assert.zig` as the shared
  ABI proof substrate, and the current Phase 11 HVC packet now reuses that
  substrate for exported-header and callback-table checkpoints instead of
  claiming note-only parity

## Returned ABI Layout Assertion Suite

Current `master` already materializes this narrower ABI proof suite:

- `zigux/helpers/layout_assert.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `drivers/tty/hvc/hvc_console.h`
- `drivers/tty/hvc/hvc_console.zig`
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`

That current suite is real machine-checked ABI evidence, not prose-only
continuity:

- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig` keeps the exported
  helper surface, imported `Winsize`, and imported `HvOps` layout tied to the
  live `drivers/tty/hvc/hvc_console.zig` module through the shared
  `layout_assert.expect*` API
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` keeps `struct hv_ops` size,
  alignment, callback-table offsets, exact callback signatures, and exported
  header lines explicit against `drivers/tty/hvc/hvc_console.h`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` replays both focused proof
  shards through one bounded build route instead of widening into a broader
  shared Phase 11 test harness
- `Documentation/zigux/phase11-uapi-header-parity-survey.md` and
  `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` now
  describe that proof suite as adjacent proof-shard evidence rather than as a
  restored shared replay family

## Remaining Roadmap-Truthfulness Gap

The current gap is no longer that Phase 11 lacks `layout_assert` or lacks ABI
proof entirely.

The real current gap is that the broader reminder layer still under-describes
that returned suite and its remaining limits:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Those broad reminder surfaces still do not carry a dedicated Phase 11 summary
that names the returned `layout_assert` substrate, the exported-surface proof
shard, the `hv_ops` callback-table proof shard, and the remaining Phase 11
roadmap gap in one bounded place.

Current `master` also still does not rematerialize the older broader shared
replay family:

- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_build.zig`

So the truthful current claim is narrower:

- the returned `layout_assert` substrate and the two focused HVC ABI proof
  shards are landed and reviewable
- the broader reminder layer still needs follow-through before it can present
  that suite as a stable Phase 11 shared summary
- the older shared replay family remains absent and should not be implied by the
  existence of the focused proof packet alone

## Review Rule

- treat this note as a lane-local survey of the returned ABI layout assertion
  suite, not as proof that the full Phase 11 tranche is closed
- keep `zigux/helpers/layout_assert.zig`,
  `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, and
  `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` explicit whenever shared
  Phase 11 reminder wording summarizes ABI evidence
- keep the remaining gap framed as a broad-reminder and missing-shared-replay
  problem, not as missing HVC ABI proof code

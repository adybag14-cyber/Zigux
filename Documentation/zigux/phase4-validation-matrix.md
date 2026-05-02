# Phase 4 Validation Matrix

This document records the live Phase 4 differential-validation ownership and replay matrix.

## Status

- `PHASE4_STATUS=differential_validation_matrix_landed`
- scope: keep the currently shipped Phase 4 rollback-readiness gates reviewable, name the rollback owners for each bounded gate, and make the current CI and local replay paths explicit
- current repo reality:
  - `scripts/zigux/artifact_diff.py`
  - `scripts/zigux/check-artifact-diff-contract.py`
  - `Documentation/zigux/phase4-gate-evidence.md`
  - `zigux/tests/atomic64_diff.zig`
  - `zigux/tests/runtime_atomic64_diff.zig`
  - `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
  - `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`
  - `zigux/tests/phase4_test_fsmount_manifest.json`
  - `zigux/tests/phase4_test_fsmount_survey.zig`
  - `zigux/tests/phase4_perf_baseline_manifest.json`
  - `zigux/tests/phase4_perf_baseline_survey.zig`
  - `zigux/tests/bitmap_diff.zig`
  - `zigux/tests/phase4_build.zig`
  - `scripts/zigux/validate-phase4.py`
  - `.github/workflows/zigux-bootstrap.yml`
- roadmap note: the roadmap names `zigux/tests/atomic64_diff.zig`, and live `master` now ships that canonical wrapper while the bounded atomic64 replay gate at `zigux/tests/runtime_atomic64_diff.zig` remains the single underlying replay body; this record follows the shipped wrapper-plus-runtime bundle instead of inventing a second parallel gate

## Why this exists

The roadmap says Phase 4 must make future Zigux ports measurable and reversible. The repo already had the shared Phase 4 build entrypoint and validator wiring, but it did not yet keep one reviewable record that named:

- the bounded rollback owner for each live Phase 4 gate
- the current perf threshold status for those gates
- the lab and CI matrix that replays the gates today
- the reversible-delivery evidence that ties each shipped Zig gate back to its current C anchor if the shared entrypoint has to drop that gate
- one exact readback note that pins the current matrix, validator, build entrypoint, workflow, and manifest packet to an inspected `master` head whenever the live Phase 4 gate-definition surface moves
- the shared artifact comparator self-test that now runs before the Phase 4 validator claims the rollback-readiness bundle is still aligned
- the external artifact-diff contract replay that keeps the published stable text pass case, text mismatch failure, both missing-file directions, direct JSON mismatch, malformed-JSON markers, SHA-256 digest fields, and exit-code surface reviewable outside the helper's built-in self-test
- the dedicated gate-evidence checker self-test and live blob-ledger replay that keep the exact readback note fail-closed across the survey-file and index-surface pins now recorded in `Documentation/zigux/phase4-gate-evidence.md`
- one isolated runtime atomic64 replay command that can be run without depending on the bitmap lane staying green on the same head
- the canonical `zigux/tests/atomic64_diff.zig` wrapper that now keeps the roadmap-facing atomic64 entrypoint explicit while the runtime replay body stays singular
- the survey-backed atomic64 replay that keeps the current roadmap-path and broader-surface gaps measurable inside the shared Phase 4 build
- one isolated bitmap replay command that can be run without depending on the atomic64 lane or the shared `phase4-test` bundle on the same head

Without that record, Phase 4 validation existed in code but not yet as a product-facing ownership note.

## Gate Ownership

### `scripts/zigux/artifact_diff.py --self-test`

- anchor: `scripts/zigux/` host-side diff and layout tooling
- phase bucket: `Phase 4 deterministic artifact-diff preflight for host-side tools`
- owner: `Validation and Perf Team`
- rollback owner: `Validation and Perf Team`
- fallback path: keep the shared self-test wired into `make -C zigux phase4-validate` and fail closed before the rollback-readiness packet claims the host-side diff tooling is aligned
- perf threshold status: deterministic correctness-only preflight today; no timing threshold is relevant until a future Phase 4 lane adds a benchmarked host-tool diff workload

### `python3 scripts/zigux/check-artifact-diff-contract.py`

- anchor: `scripts/zigux/` host-side diff and layout tooling
- phase bucket: `Phase 4 external artifact-diff CLI contract replay for host-side tools`
- owner: `Validation and Perf Team`
- rollback owner: `Validation and Perf Team`
- fallback path: keep the external contract replay wired into `make -C zigux phase4-validate` so the live stable text pass case, text mismatch failure, both missing-file directions, direct JSON mismatch, malformed expected and actual JSON failure shapes, and SHA-256 pass and drift cases stay measurable outside the helper's built-in self-test
- perf threshold status: deterministic correctness-only preflight today; no timing threshold is relevant until a future Phase 4 lane adds a benchmarked host-tool diff workload

### `python3 scripts/zigux/check-phase4-gate-evidence.py --self-test`

- anchor: `Documentation/zigux/phase4-gate-evidence.md` exact-readback packet
- phase bucket: `Phase 4 synthetic gate-evidence checker coverage for rollback-ownership and lab-matrix blob pins`
- owner: `Validation and Perf Team`
- rollback owner: `Validation and Perf Team`
- fallback path: keep the dedicated synthetic checker replay wired into `make -C zigux phase4-validate` so missing status tokens, missing survey-snapshot markers, and stale blob-target coverage fail before the live gate-evidence ledger is trusted
- perf threshold status: deterministic correctness-only preflight today; no timing threshold is relevant until a future Phase 4 lane adds a benchmarked gate-evidence workload

### `python3 scripts/zigux/check-phase4-gate-evidence.py`

- anchor: `Documentation/zigux/phase4-gate-evidence.md` exact-readback packet
- phase bucket: `Phase 4 live gate-evidence blob-ledger replay for rollback-ownership and lab-matrix blob pins`
- owner: `Validation and Perf Team`
- rollback owner: `Validation and Perf Team`
- fallback path: keep the dedicated live checker wired into `make -C zigux phase4-validate` so the exact-readback note fails closed across the current survey-file and docs-root, scripts-root, and tests-root blob pins instead of relying on prose-only review
- perf threshold status: deterministic correctness-only preflight today; no timing threshold is relevant until a future Phase 4 lane adds a benchmarked gate-evidence workload

### `zigux/tests/atomic64_diff.zig`

- anchor: `lib/atomic64_test.c`
- phase bucket: `Phase 4 differential validation via the canonical atomic64 wrapper plus the current live replay body`
- underlying replay body: `zigux/tests/runtime_atomic64_diff.zig`, which keeps the bounded atomic64 behavior in one place while the wrapper preserves the roadmap-facing entrypoint
- owner: ABI and Runtime Team
- rollback owner: ABI and Runtime Team
- fallback path: keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses
- exact bounded checks: `addCounter()` currently records both the onestwos growth and the `-1` decrement from `v0`, bitwise `or`, `and`, `xor`, and `andnot` each pin the bounded `v0`/`v1` result words, exchange keeps the `v0 -> v1`, `v1 -> v2`, and `minInt(i64) -> -1` round-trips explicit, `cmpxchg` keeps both the match-store and mismatch-no-store paths explicit, `addUnlessCounter()` keeps the blocked and changed cases explicit, `incNotZeroCounter()` covers positive, zero, `-1`, and `minInt(i64)` nonzero replay, `decIfPositiveCounter()` covers positive, zero, and negative return-path behavior, and the selftest-family replay keeps the ordered operation families plus `checked_returning_paths`, `checked_guard_paths`, post-exit invalid lifecycle errors, and post-selftest replay explicit
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded add, sub, bitwise, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay set

### `zigux/tests/bitmap_diff.zig`

- anchor: `lib/test_bitmap.c`
- phase bucket: `Phase 4 differential validation for the broad bitmap rollback gate`
- owner: Shared Subsystems Pod
- rollback owner: Shared Subsystems Pod
- fallback path: keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses
- exact bounded checks: `bitmap_fill(..., 35)` proves the 35-bit prefix start plus the 34, 35, and `BITS_PER_LONG` boundary bits, the rounded-prefix survey also keeps `bitmap_fill(..., 115)` explicit as the still-unrounded two-word gap while `bitmap_zero(..., 35)` and `bitmap_zero(..., 115)` keep the current filled-side one-word and two-word rounded clears explicit, the cross-boundary `bitmap_set(..., 79, 19)` and `bitmap_clear(..., 79, 19)` cases keep the 64..78 and 98..1023 boundaries explicit, full-width `bitmap_fill(..., 1024)` and `bitmap_zero(..., 1024)` now also keep the all-set and all-clear start-state printlist anchors explicit for both the 23-bit and 1024-bit views before `bitmap_scnprintf()` preserves the later full `1-3,7,10-11` summary and truncated `1-3` rendering, `bitmap_copy()` replays the 23-bit single-word window, the full-width cleared-destination copies and filled-destination copies, the 109-bit partial-tail, and the 97-bit aligned-copy cases while `bitmap.copyClearTail()` keeps the 109-bit cleared-tail contract, and `find_nth_bit()` records both the full-width nth-7 and nth-8 outcomes plus the reduced-width `64 * 3 - 1` cutoff that still returns bit 123 for nth 7 and the cutoff width for nth 8
- current rollback evidence gap: direct `bitmap_fill(..., 115)` still stops at bit 114 in the shipped Zig helper, so the Phase 4 packet keeps that mismatch survey-only instead of claiming parity with the `lib/test_bitmap.c` rounded two-word anchor
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, rounded-prefix, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior checkpoints

## Lab And CI Matrix

| lane surface | purpose | owner | rollback owner | bootstrap CI replay | local lab replay | reversible delivery evidence | threshold posture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `scripts/zigux/artifact_diff.py --self-test` | deterministic text, JSON, SHA-256, and missing-file comparison self-test for the shared host-side diff tooling | `Validation and Perf Team` | `Validation and Perf Team` | workflow step `Validate Phase 4 diff gates`, which calls `make -C zigux phase4-validate` and therefore reruns the shared self-test before the shipped rollback gates | `make -C zigux phase4-validate` or direct `python3 scripts/zigux/artifact_diff.py --self-test` replay when the helper changes | `scripts/zigux/artifact_diff.py` stays the shared comparator for the bounded Phase 4 host-side tooling packet, and removing its self-test from `phase4-validate` would drop the roadmap-backed deterministic preflight that now guards the rollback-readiness docs and diff checks | `deterministic_preflight_required_for_host_side_diff_tools` |
| `python3 scripts/zigux/check-artifact-diff-contract.py` | external replay of the shared artifact-diff CLI contract covering the stable text pass case, text mismatch failure, both missing-file directions, direct JSON mismatch, malformed expected and actual JSON failure shapes, and SHA-256 pass and drift cases for the bounded host-side diff tooling packet | `Validation and Perf Team` | `Validation and Perf Team` | workflow step `Validate Phase 4 diff gates`, which calls `make -C zigux phase4-validate` and therefore reruns the external contract replay before the shipped rollback gates | `make -C zigux phase4-validate` or direct `python3 scripts/zigux/check-artifact-diff-contract.py` replay when the outward CLI contract changes | `scripts/zigux/check-artifact-diff-contract.py` keeps the published `ARTIFACT_DIFF=...`, `MODE=...`, `EXPECTED_EXISTS=...`, `ACTUAL_EXISTS=...`, direct JSON mismatch fail shape, `EXPECTED_JSON_ERROR=...`, `ACTUAL_JSON_ERROR=...`, `SHA256=...`, `EXPECTED_SHA256=...`, `ACTUAL_SHA256=...`, and exit-code surface measurable outside the helper's built-in self-test, and removing it from `phase4-validate` would leave the rollback-readiness packet without that external proof | `deterministic_preflight_required_for_host_side_diff_tools` |
| `python3 scripts/zigux/check-phase4-gate-evidence.py --self-test` | synthetic replay of the exact-readback checker packet covering status-token, survey-snapshot, and blob-target drift before the live ledger is trusted | `Validation and Perf Team` | `Validation and Perf Team` | workflow step `Validate Phase 4 diff gates`, which calls `make -C zigux phase4-validate` and therefore reruns the synthetic gate-evidence checker before the shipped rollback gates | `make -C zigux phase4-validate` or direct `python3 scripts/zigux/check-phase4-gate-evidence.py --self-test` replay when the gate-evidence checker or its blob-target set changes | `Documentation/zigux/phase4-gate-evidence.md` remains the exact-readback note for the rollback packet, and removing the synthetic checker replay from `phase4-validate` would leave missing status tokens, survey-snapshot markers, and blob-target coverage as prose-only review instead of a fail-closed proof | `deterministic_preflight_required_for_host_side_diff_tools` |
| `python3 scripts/zigux/check-phase4-gate-evidence.py` | live replay of the exact-readback checker packet across the current survey-file and docs-root, scripts-root, and tests-root blob pins recorded in `Documentation/zigux/phase4-gate-evidence.md` | `Validation and Perf Team` | `Validation and Perf Team` | workflow step `Validate Phase 4 diff gates`, which calls `make -C zigux phase4-validate` and therefore reruns the live gate-evidence checker before the shipped rollback gates | `make -C zigux phase4-validate` or direct `python3 scripts/zigux/check-phase4-gate-evidence.py` replay when the gate-evidence ledger or its pinned surfaces change | `Documentation/zigux/phase4-gate-evidence.md` stays the paired exact-readback ledger for the rollback packet, and removing the live checker from `phase4-validate` would leave the survey-file and index-surface blob pins reviewable only by prose instead of a fail-closed checker | `deterministic_preflight_required_for_host_side_diff_tools` |
| `zigux/tests/atomic64_diff.zig` | bounded atomic64 add, sub, bitwise, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay | `ABI and Runtime Team` | `ABI and Runtime Team` | workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, which call `make -C zigux phase4-validate` then `make -C zigux phase4-test` in `.github/workflows/zigux-bootstrap.yml` | `make -C zigux phase4-validate`, then `make -C zigux phase4-test`, which loads the canonical `atomic64_diff.zig` wrapper and runs the shared `phase4-runtime-atomic64-diff-tests` and `phase4-runtime-atomic64-diff-survey-tests` entries in `zigux/tests/phase4_build.zig`; `make -C zigux phase4-runtime-atomic64-diff` and direct `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` replays remain available when only the atomic64 gate needs isolation | `lib/atomic64_test.c` stays the source of truth, and removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move while `runtime_atomic64_diff.zig` remains the single replay body and the existing Phase 9 runtime atomic64 starter remains the forward path | `threshold_pending_until_runtime_atomic64_scope_widens` |
| `zigux/tests/phase4_test_fsmount_survey.zig` | manifest-backed survey gate for the still-absent `samples/zigux/test_fsmount.zig` roadmap row while the current replay stays on the `samples/vfs/test-fsmount.c` C anchor | `Validation and Perf Team` | `Validation and Perf Team` | workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, which call `make -C zigux phase4-validate` then `make -C zigux phase4-test` in `.github/workflows/zigux-bootstrap.yml`, with the shared `phase4-test-fsmount-survey-tests` entry in `zigux/tests/phase4_build.zig` keeping the survey packet live | `make -C zigux phase4-test-fsmount-survey` and direct `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` keep the survey packet isolated, while `make M=samples/vfs` remains the current C-anchor replay | `samples/vfs/test-fsmount.c` stays the source of truth, the survey packet remains C-anchor-only until a bounded `samples/zigux/test_fsmount.zig` starter lands, and removing `phase4_test_fsmount_survey.zig` from the shared `phase4_build.zig` entrypoint returns this roadmap row to matrix-only tracking without overstating a landed Zig sample | `c_anchor_only_until_test_fsmount_starter_lands` |
| `zigux/tests/phase4_perf_baseline_survey.zig` | manifest-backed survey gate for the still-unapproved benchmark command and acceptable limit posture across the shipped `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` rollback gates while both remain correctness-only | `Validation and Perf Team` | `Validation and Perf Team` | workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, which call `make -C zigux phase4-validate` then `make -C zigux phase4-test` in `.github/workflows/zigux-bootstrap.yml`, with the shared `phase4-perf-baseline-survey-tests` entry in `zigux/tests/phase4_build.zig` keeping the survey packet live | `make -C zigux phase4-perf-baseline-survey` and direct `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` keep the survey packet isolated while the existing `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, and `phase4-bitmap-diff-tests` replays stay the current correctness-only gate surfaces | `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` remain the shipped rollback gates, and removing `phase4_perf_baseline_survey.zig` from the shared `phase4_build.zig` entrypoint would drop the only machine-checked record that their benchmark command and acceptable limit are still unapproved instead of landed | `perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land` |
| `zigux/tests/bitmap_diff.zig` | bounded bitmap range, rounded-prefix, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior replay | `Shared Subsystems Pod` | `Shared Subsystems Pod` | workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, which call `make -C zigux phase4-validate` then `make -C zigux phase4-test` in `.github/workflows/zigux-bootstrap.yml` | `make -C zigux phase4-validate`, then `make -C zigux phase4-test`, which runs the shared `phase4-bitmap-diff-tests` entry in `zigux/tests/phase4_build.zig`; `make -C zigux phase4-bitmap-diff` and direct `zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` replays remain available when only the bitmap gate needs isolation | `lib/test_bitmap.c` stays the source of truth, and removing `bitmap_diff.zig` from the shared `phase4_build.zig` entrypoint falls back to the existing broad bitmap parity checks | `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` |

## Remaining Measurability Gaps Vs Roadmap

| roadmap item | current repo state | measurability gap | next bounded step |
| --- | --- | --- | --- |
| `samples/zigux/kprobe_example.zig` | not present on `master`; the current anchor remains `samples/kprobes/kprobe_example.c` through `samples/kprobes/Makefile` and `CONFIG_SAMPLE_KPROBES`, and the validator-backed absence check keeps that true today | reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands | land one bounded survey manifest or starter gate under `samples/zigux/` that keeps the same owner, rollback owner, and replay command before claiming this anchor as active Phase 4 work |
| `samples/zigux/test_fsmount.zig` | not present on `master`; the current anchor remains `samples/vfs/test-fsmount.c` through `samples/vfs/Makefile` and `userprogs-always-y += test-fsmount`, the validator-backed absence check keeps that true today, and the manifest-backed survey gate now lives in `zigux/tests/phase4_test_fsmount_manifest.json` plus `zigux/tests/phase4_test_fsmount_survey.zig` under the shared `phase4-test-fsmount-survey-tests` replay | reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/vfs`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands | land one bounded starter under `samples/zigux/test_fsmount.zig` that keeps the same owner, rollback owner, and `make M=samples/vfs` replay contract before claiming this anchor as active Phase 4 work |
| `perf baselines and thresholds for the two shipped rollback gates` | `zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` are still correctness-only gates today | benchmark command and acceptable limit are still unapproved for both landed gates | land one bounded benchmark command and one acceptable limit per gate before Phase 4 claims perf coverage |

`scripts/zigux/validate-phase4.py` now also fails if either roadmap sample path lands while this matrix still claims that anchor is absent, so the survey note cannot silently drift past the shipped repo state.

The `samples/zigux/test_fsmount.zig` roadmap row is no longer prose-only: the manifest-backed survey gate now lives in `zigux/tests/phase4_test_fsmount_manifest.json`, runs through `phase4-test-fsmount-survey-tests` in `zigux/tests/phase4_build.zig`, and keeps the dedicated `make -C zigux phase4-test-fsmount-survey` local replay path plus the current lab posture C-anchor-only through `make M=samples/vfs` until the bounded Zig sample itself lands.

The Phase 4 perf-baseline gap is no longer prose-only either: the manifest-backed survey packet now lives in `zigux/tests/phase4_perf_baseline_manifest.json`, runs through `phase4-perf-baseline-survey-tests` in `zigux/tests/phase4_build.zig`, and keeps the dedicated `make -C zigux phase4-perf-baseline-survey` local replay path plus the current `threshold_pending_until_runtime_atomic64_scope_widens` and `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` posture explicit until one bounded benchmark command and one acceptable limit land for each shipped rollback gate.

`Documentation/zigux/phase4-gate-evidence.md` is the paired exact readback note for this same packet, so any change that moves the matrix, validator, build entrypoint, workflow hooks, or the manifest-backed survey gates should refresh that inspected-head evidence in the same bounded Phase 4 update.

## Review Rules

- Phase 4 remains a rollback-readiness lane first, not a performance-claim lane
- any future hard timing threshold must name the benchmark command, acceptable limit, owner, and rollback owner in this record before the lane claims perf coverage
- if the shared `artifact_diff.py --self-test`, `check-artifact-diff-contract.py`, or `check-phase4-gate-evidence.py` surface changes, update this matrix in the same change so the roadmap's deterministic host-tool preflight and exact-readback checker packet stay explicit
- any future broad `atomic64_diff.zig` return should keep the wrapper-plus-runtime relationship explicit here instead of letting the canonical entrypoint and the single replay body drift apart
- if either gate regresses, the rollback owner must keep the current C anchor and the existing Phase 4 documentation truthful while the Zig replay gate is repaired or removed from the shared entrypoint
- if the workflow step names or shared `phase4_build.zig` test names change, update this matrix in the same change so the local lab and CI replay paths stay measurable instead of falling back to generic wording

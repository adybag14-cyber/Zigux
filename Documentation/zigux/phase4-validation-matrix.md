# Phase 4 Validation Matrix

This document records the live Phase 4 differential-validation ownership and replay matrix.

## Status

- `PHASE4_STATUS=differential_validation_matrix_landed`
- scope: keep the currently shipped Phase 4 rollback-readiness gates reviewable, name the rollback owners for each bounded gate, and make the current CI and local replay paths explicit
- current repo reality:
  - `scripts/zigux/artifact_diff.py`
  - `scripts/zigux/check-artifact-diff-contract.py`
  - `zigux/tests/runtime_atomic64_diff.zig`
  - `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
  - `zigux/tests/bitmap_diff.zig`
  - `zigux/tests/phase4_build.zig`
  - `scripts/zigux/validate-phase4.py`
  - `.github/workflows/zigux-bootstrap.yml`
- roadmap note: the roadmap names `zigux/tests/atomic64_diff.zig`, but live `master` currently carries the bounded atomic64 replay gate at `zigux/tests/runtime_atomic64_diff.zig`; this record follows the shipped tree instead of inventing a second parallel gate

## Why this exists

The roadmap says Phase 4 must make future Zigux ports measurable and reversible. The repo already had the shared Phase 4 build entrypoint and validator wiring, but it did not yet keep one reviewable record that named:

- the bounded rollback owner for each live Phase 4 gate
- the current perf threshold status for those gates
- the lab and CI matrix that replays the gates today
- the reversible-delivery evidence that ties each shipped Zig gate back to its current C anchor if the shared entrypoint has to drop that gate
- the shared artifact comparator self-test that now runs before the Phase 4 validator claims the rollback-readiness bundle is still aligned
- the external CLI-contract replay that keeps one stable pass case plus one missing-file failure shape explicit outside the helper's built-in self-test
- one isolated runtime atomic64 replay command that can be run without depending on the bitmap lane staying green on the same head
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
- exact bounded checks: one stable pass case plus one missing-file failure shape for the outward `ARTIFACT_DIFF=...` CLI lines
- fallback path: keep the checker wired into `make -C zigux phase4-validate` and fail closed before the rollback-readiness packet claims the outward `ARTIFACT_DIFF=...` contract is still reviewable on the current head
- perf threshold status: deterministic correctness-only replay today; no timing threshold is relevant until a future Phase 4 lane adds a benchmarked host-tool diff workload

### `zigux/tests/runtime_atomic64_diff.zig`

- anchor: `lib/atomic64_test.c`
- phase bucket: `Phase 4 differential validation via the current live atomic64 replay gate`
- owner: `ABI and Runtime Team`
- rollback owner: `ABI and Runtime Team`
- fallback path: keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded add, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay set

### `zigux/tests/bitmap_diff.zig`

- anchor: `lib/test_bitmap.c`
- phase bucket: `Phase 4 differential validation for the broad bitmap rollback gate`
- owner: `Shared Subsystems Pod`
- rollback owner: `Shared Subsystems Pod`
- fallback path: keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses
- exact bounded checks: `bitmap_fill(..., 35)` currently proves the 35-bit prefix start plus the 34, 35, and `BITS_PER_LONG` boundary bits, `bitmap_zero(..., 115)` still proves the two-word rounded clear, the cross-boundary `bitmap_set(..., 79, 19)` and `bitmap_clear(..., 79, 19)` cases keep the 64..78 and 98..1023 boundaries explicit, full-width `bitmap_fill(..., 1024)` and `bitmap_zero(..., 1024)` keep the endpoints honest, `bitmap_scnprintf()` preserves both the full `1-3,7,10-11` summary and the truncated `1-3` rendering, `bitmap_copy()` replays the 23-bit single-word window, the full-width cleared-destination and filled-destination copies, the 109-bit partial-tail, and the 97-bit aligned-copy cases while `bitmap.copyClearTail()` keeps the 109-bit cleared-tail contract, and `find_nth_bit()` records both the full-width nth-7 and nth-8 outcomes plus the reduced-width `64 * 3 - 1` cutoff that still returns bit 123 for nth 6 and the cutoff width for nth 7
- current rollback evidence gap: paired `bitmap_zero(..., 35)` and `bitmap_fill(..., 115)` rounded-prefix checkpoints stay out of the shipped gate until `tools/lib/bitmap.zig` matches the `lib/test_bitmap.c` anchor on those cases
- perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior checkpoints

## Lab And CI Matrix

| lane surface | purpose | owner | rollback owner | bootstrap CI replay | local lab replay | reversible delivery evidence | threshold posture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `scripts/zigux/artifact_diff.py --self-test` | deterministic text, JSON, SHA-256, and missing-file comparison self-test for the shared host-side diff tooling | `Validation and Perf Team` | `Validation and Perf Team` | workflow step `Validate Phase 4 diff gates`, which calls `make -C zigux phase4-validate` and therefore reruns the shared self-test before the shipped rollback gates | `make -C zigux phase4-validate` or direct `python3 scripts/zigux/artifact_diff.py --self-test` replay when the helper changes | `scripts/zigux/artifact_diff.py` stays the shared comparator for the bounded Phase 4 host-side tooling packet, and removing its self-test from `phase4-validate` would drop the roadmap-backed deterministic preflight that now guards the rollback-readiness docs and diff checks | `deterministic_preflight_required_for_host_side_diff_tools` |
| `python3 scripts/zigux/check-artifact-diff-contract.py` | deterministic outward CLI-contract replay for the shared host-side diff tooling | `Validation and Perf Team` | `Validation and Perf Team` | workflow step `Validate Phase 4 diff gates`, which calls `make -C zigux phase4-validate` and therefore reruns the external CLI-contract replay before the shipped rollback gates | `make -C zigux phase4-validate` or direct `python3 scripts/zigux/check-artifact-diff-contract.py` replay when the outward `ARTIFACT_DIFF=...` contract changes | `scripts/zigux/check-artifact-diff-contract.py` stays the shared external replay for the bounded Phase 4 host-side tooling packet, and removing it from `phase4-validate` would drop the roadmap-backed external proof that the outward `ARTIFACT_DIFF=...` lines still match the documented pass and missing-file failure shapes | `deterministic_cli_contract_replay_required_for_host_side_diff_tools` |
| `zigux/tests/runtime_atomic64_diff.zig` | bounded atomic64 add, exchange, cmpxchg, add_unless, inc_not_zero, and selftest-family plus post-selftest replay | `ABI and Runtime Team` | `ABI and Runtime Team` | workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, which call `make -C zigux phase4-validate` then `make -C zigux phase4-test` in `.github/workflows/zigux-bootstrap.yml` | `make -C zigux phase4-validate`, then `make -C zigux phase4-test`, which runs the shared `phase4-runtime-atomic64-diff-tests` and `phase4-runtime-atomic64-diff-survey-tests` entries in `zigux/tests/phase4_build.zig`; `make -C zigux phase4-runtime-atomic64-diff` and direct `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` replays remain available when only the atomic64 gate needs isolation | `lib/atomic64_test.c` stays the source of truth, and removing `runtime_atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move while the existing Phase 9 runtime atomic64 starter remains the forward path | `threshold_pending_until_runtime_atomic64_scope_widens` |
| `zigux/tests/bitmap_diff.zig` | bounded bitmap range, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior replay | `Shared Subsystems Pod` | `Shared Subsystems Pod` | workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, which call `make -C zigux phase4-validate` then `make -C zigux phase4-test` in `.github/workflows/zigux-bootstrap.yml` | `make -C zigux phase4-validate`, then `make -C zigux phase4-test`, which runs the shared `phase4-bitmap-diff-tests` entry in `zigux/tests/phase4_build.zig`; `make -C zigux phase4-bitmap-diff` and direct `zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` replays remain available when only the bitmap gate needs isolation | `lib/test_bitmap.c` stays the source of truth, and removing `bitmap_diff.zig` from the shared `phase4_build.zig` entrypoint falls back to the existing broad bitmap parity checks | `threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks` |

## Remaining Measurability Gaps Vs Roadmap

| roadmap item | current repo state | measurability gap | next bounded step |
| --- | --- | --- | --- |
| `samples/zigux/kprobe_example.zig` from the `samples/kprobes/kprobe_example.c` anchor | not present on `master`; the current anchor remains `samples/kprobes/kprobe_example.c` through `samples/kprobes/Makefile` and `CONFIG_SAMPLE_KPROBES` | reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`; no hard timing threshold is approved before a bounded Zig sample lands | land one bounded survey manifest or starter gate under `samples/zigux/` that keeps the same owner, rollback owner, and replay command before claiming this anchor as active Phase 4 work |
| `samples/zigux/test_fsmount.zig` from the `samples/vfs/test-fsmount.c` anchor | not present on `master`; the current anchor remains `samples/vfs/test-fsmount.c` through `samples/vfs/Makefile` and `userprogs-always-y += test-fsmount` | reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/vfs`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands | land one bounded survey manifest or starter gate under `samples/zigux/` that keeps the same owner, rollback owner, and replay command before claiming this anchor as active Phase 4 work |
| perf baselines and thresholds for the two shipped rollback gates | `zigux/tests/runtime_atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` are still correctness-only gates today | benchmark command and acceptable limit are still unapproved for both landed gates | land one bounded benchmark command and one acceptable limit per gate before Phase 4 claims perf coverage |

## Review Rules

- Phase 4 remains a rollback-readiness lane first, not a performance-claim lane
- any future hard timing threshold must name the benchmark command, acceptable limit, owner, and rollback owner in this record before the lane claims perf coverage
- if the shared `artifact_diff.py --self-test` surface changes, update this matrix in the same change so the roadmap's deterministic host-tool preflight stays explicit
- if the outward `artifact_diff.py` CLI lines or `check-artifact-diff-contract.py` cases change, update this matrix in the same change so the external host-tool replay stays explicit too
- any future broad `atomic64_diff.zig` return should replace the current runtime atomic64 path here instead of sitting beside it as a duplicate gate
- if either gate regresses, the rollback owner must keep the current C anchor and the existing Phase 4 documentation truthful while the Zig replay gate is repaired or removed from the shared entrypoint
- if the workflow step names or shared `phase4_build.zig` test names change, update this matrix in the same change so the local lab and CI replay paths stay measurable instead of falling back to generic wording

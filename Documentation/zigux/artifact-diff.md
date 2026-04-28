# Artifact Diff Policy

Zigux uses committed artifacts only when they anchor a bounded parity claim.

Current Phase 1 use
- `zigux/tests/fixtures/phase1_helpers.json` is generated from the in-tree C helper implementations.
- `scripts/zigux/check-phase1-parity.py` rebuilds that artifact, compares it against the committed JSON, and reruns the bounded C harness to prove repeat-run JSON determinism before the Phase 1 parity lane passes.
- `scripts/zigux/artifact_diff.py` is the shared comparison layer that already backs the bounded host-side tools under `scripts/zigux/`.

Current Phase 2 use
- `python3 scripts/zigux/artifact_diff.py --self-test` exercises the shared text, JSON, SHA-256, and missing-file comparison paths so deterministic comparison drift fails before the bounded Phase 2 parity lanes run.
- `zigux/tests/fixtures/fixdep/sample_expected.txt` is generated from the current in-tree C `scripts/basic/fixdep.c` behavior on a bounded committed sample.
- `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt` widens that claim with a second committed depfile covering multi-target parsing, comments, duplicate deps, no-parse files, and escaped `#`.
- `zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt` anchors the escaped-whitespace dependency-token path so `fixdep.zig` must preserve `\\ ` and `\\t` separators the same way as the C tool.
- `zigux/tests/fixtures/fixdep/sample_concatenated_expected.txt` anchors concatenated target entries so `fixdep.zig` must keep the first source token while still collecting later dependency tokens from the continued dep-info stream.
- `zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt` and `sample_comment_only_expected.stderr.txt` anchor the bounded no-target failure shape, keeping the `fixdep: parse error; no targets found` path reviewable against both stdout and stderr artifacts.
- `zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt` and `sample_missing_dep_expected.stderr.txt` anchor the bounded missing-dependency failure shape, including the preserved stdout prefix and C-style open-file stderr message.
- `zigux/tests/fixtures/fixdep/sample_output_write_expected.txt` and `sample_output_write_expected.stderr.txt` anchor the bounded output-write failure shape when stdout cannot accept the full generated dependency payload.
- `scripts/zigux/check-fixdep-diff.py` compares the committed fixdep samples against both the C tool and `scripts/zigux/fixdep.zig`, and it now also treats any unexpected stderr from success-path cases as a gate failure so quiet parity cannot drift silently.
- `zigux/tests/fixtures/genksyms_bridge/*.json` capture bounded wrapper-first `genksyms` invocation planning for committed flag combinations.
- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json` anchors the smallest wrapper-first `genksyms` invocation claim.
- `scripts/zigux/check-genksyms-bridge.py` compares those committed JSON fixtures against both a bounded C harness and `scripts/zigux/genksyms.zig`.
- `zigux/tests/fixtures/genksyms_crc/expected.json` is generated from a bounded C harness that ports the current `scripts/genksyms/genksyms.c` CRC logic over committed symbol-like input strings.
- `scripts/zigux/check-genksyms-crc-diff.py` compares that committed JSON against both the bounded C harness and `scripts/zigux/genksyms_crc.zig`, then reruns each side to prove repeat-run JSON determinism before the lane passes.
- `zigux/tests/fixtures/kconfig_bridge/*.json` capture bounded wrapper-first `conf` / `confdata` bridge outputs for committed Kconfig inputs.
- `scripts/zigux/check-kconfig-bridge.py` compares those committed JSON fixtures against `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig`.
- `zigux/tests/fixtures/phase2_cross_targets.json` fixes the bounded cross-target compile set for the Phase 2 tool tranche.
- `zigux/tests/fixtures/mk_elfconfig/elf32_expected.json` and sibling JSON fixtures capture bounded stdin-driven behavior for `scripts/mod/mk_elfconfig.c`.
- `scripts/zigux/check-mk_elfconfig-diff.py` compares those committed JSON results against both the C tool and `scripts/zigux/mk_elfconfig.zig`.

Current Phase 3 use
- `zigux/tests/fixtures/phase3_abi/expected.json` anchors the bounded Phase 3 ABI layout parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug abi` compares that committed JSON fixture against both the bounded C harness and the Zig ABI layout dump.
- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json` anchors the bounded Phase 3 bitmap/cpumask parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug bitmap-cpumask` compares that committed JSON fixture against both the bounded C harness and the Zig bitmap/cpumask dump.
- `zigux/tests/fixtures/phase3_cdev_add/expected.json` anchors the bounded Phase 3 cdev add parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug cdev-add` compares that committed JSON fixture against both the bounded C harness and the Zig cdev add dump.
- `zigux/tests/fixtures/phase3_cdev_lookup/expected.json` anchors the bounded Phase 3 cdev lookup parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug cdev-lookup` compares that committed JSON fixture against both the bounded C harness and the Zig cdev lookup dump.
- `zigux/tests/fixtures/phase3_chrdev_complete/expected.json` anchors the bounded Phase 3 chrdev complete parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-complete` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev complete dump.
- `zigux/tests/fixtures/phase3_chrdev_fops/expected.json` anchors the bounded Phase 3 chrdev fops parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-fops` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev fops dump.
- `zigux/tests/fixtures/phase3_chrdev_io/expected.json` anchors the bounded Phase 3 chrdev io parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-io` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev io dump.
- `zigux/tests/fixtures/phase3_chrdev_notify/expected.json` anchors the bounded Phase 3 chrdev notify parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack/expected.json` anchors the bounded Phase 3 chrdev notify ack parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_budget/expected.json` anchors the bounded Phase 3 chrdev notify ack budget parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-budget` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack budget dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window delivery dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window delivery window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window budget parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window delivery window budget dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window budget window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window delivery window budget window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window budget window delivery parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window delivery window budget window delivery dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_DELIVERY_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_DELIVERY/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window budget window delivery window budget window DELIVERY parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-DELIVERY` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window delivery window budget window delivery window budget window DELIVERY dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_DELIVERY_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_DELIVERY_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window budget window delivery window budget window DELIVERY window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-DELIVERY-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window delivery window budget window DELIVERY window dump.

Current Phase 4 use
- `python3 scripts/zigux/artifact_diff.py --self-test` exercises the shared text, JSON, SHA-256, and missing-file comparison paths before the bounded Phase 4 rollback-readiness lanes run, which keeps stale expected-output and catalog drift small, auditable, and easy to refresh.
- the same self-test now records the exact shared comparator contract: matching text fixtures must compare byte-for-byte, matching JSON fixtures must compare after canonical parsing so key order drift alone does not fail the lane, malformed JSON must fail with file-and-position context, matching binary fixtures must report identical SHA-256 digests, and missing-file mismatches must say which side is absent.
- `scripts/zigux/artifact_diff.py` emits `ARTIFACT_DIFF=pass` plus `MODE`, `EXPECTED`, and `ACTUAL` for successful comparisons, adds one shared `SHA256=` line for successful hash-mode comparisons, and emits `ARTIFACT_DIFF=fail` plus the relevant existence, `EXPECTED_JSON_ERROR=` or `ACTUAL_JSON_ERROR=` marker, or per-side digest lines when a comparison drifts.
- `zigux/tests/runtime_atomic64_diff.zig` currently carries the live bounded atomic64 rollback-readiness parity checks.
- `zigux/tests/bitmap_diff.zig` anchors the bounded bitmap rollback-readiness parity checks.
- `zigux/tests/phase4_build.zig` keeps the two Phase 4 diff gates on one shared `zig build test --build-file zigux/tests/phase4_build.zig` entrypoint.
- `scripts/zigux/validate-phase4.py` keeps that shared self-test, the Phase 4 build entrypoint, workflow wiring, and Phase 4 documentation markers aligned before the Zig tests run.
- `Documentation/zigux/phase4-validation-matrix.md` records the current rollback owners, threshold posture, lab/CI replay matrix, and the reversible-delivery evidence that ties each shipped gate back to its current C anchor if the shared Phase 4 entrypoint has to drop that Zig gate.


Rules
- artifact fixtures must be generated from the current in-tree source of truth
- fixture scope must stay small and reviewable
- fixture updates must be intentional and committed alongside the code change that caused them
- do not use opaque binary blobs for early bootstrap parity when a text or JSON artifact is possible

Near-term target
- keep using the same pattern for the full bounded Phase 3 interop ladder, with `python3 scripts/zigux/run-phase3-checks.py --slug <slice>` as the only documented execution entrypoint for those committed parity fixtures.

# Artifact Diff Policy

Zigux uses committed artifacts only when they anchor a bounded parity claim.

Current Phase 1 use
- `zigux/tests/fixtures/phase1_helpers.json` is generated from the in-tree C helper implementations.
- `scripts/zigux/validate-phase1.py` now also checks that `phase1_helpers.json` keeps the exact committed top-level helper sections and evidence-key shape, so stale expected-output drift fails before the parity replay runs.
- `scripts/zigux/check-phase1-parity.py` rebuilds that artifact, compares it against the committed JSON, and reruns the bounded C harness to prove repeat-run JSON determinism before the Phase 1 parity lane passes.
- `scripts/zigux/artifact_diff.py` is the shared comparison layer that already backs the bounded host-side tools under `scripts/zigux/`.

Current Phase 2 use
- `python3 scripts/zigux/artifact_diff.py --self-test` exercises the shared text, JSON, SHA-256, and missing-file comparison paths so deterministic comparison drift fails before the bounded Phase 2 parity lanes run.
- `zigux/tests/fixtures/fixdep/sample_expected.txt` is generated from the current in-tree C `scripts/basic/fixdep.c` behavior on a bounded committed sample.
- `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt` widens that claim with a second committed depfile covering multi-target parsing, comments, duplicate deps, no-parse files, and escaped `#`.
- `zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt` anchors the escaped-whitespace dependency-token path so `fixdep.zig` must preserve `\\ ` and `\\t` separators the same way as the C tool.
- `zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt` anchors the escaped-colon dependency-token path so `fixdep.zig` must unescape `\\:` to the same on-disk dependency name that the C tool reads and emits.
- `zigux/tests/fixtures/fixdep/sample_concatenated_expected.txt` anchors concatenated target entries so `fixdep.zig` must keep the first source token while still collecting later dependency tokens from the continued dep-info stream.
- `zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt` and `sample_comment_only_expected.stderr.txt` anchor the bounded no-target failure shape, keeping the `fixdep: parse error; no targets found` path reviewable against both stdout and stderr artifacts.
- `zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt` and `sample_missing_dep_expected.stderr.txt` anchor the bounded missing-dependency failure shape, including the preserved stdout prefix and C-style open-file stderr message.
- `zigux/tests/fixtures/fixdep/sample_output_write_expected.txt` and `sample_output_write_expected.stderr.txt` anchor the bounded output-write failure shape when stdout cannot accept the full generated dependency payload.
- `scripts/zigux/check-fixdep-diff.py --self-test` keeps the bounded fixdep checker packet reviewable before the live artifact replay runs, so case-manifest drift, explicit-tool drift, and unsupported stdout-mode changes fail without depending on a local C compiler or Zig toolchain.
- `scripts/zigux/check-fixdep-diff.py` compares the committed fixdep samples against both the C tool and `scripts/zigux/fixdep.zig`, now treats any unexpected stderr from success-path cases as a gate failure so quiet parity cannot drift silently.
- that same bounded fixdep replay reruns both implementations to prove repeat-run artifact determinism before the Phase 2 lane passes.
- `zigux/tests/fixtures/genksyms_bridge/*.json` capture bounded wrapper-first `genksyms` invocation planning for committed flag combinations.
- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json` anchors the smallest wrapper-first `genksyms` invocation claim.
- `scripts/zigux/check-genksyms-bridge.py` compares those committed JSON fixtures against both a bounded C harness and `scripts/zigux/genksyms.zig`, now treats success-path stderr silence as part of the bridge contract, and reruns those stderr captures so repeat-run determinism cannot drift silently.
- `zigux/tests/fixtures/genksyms_crc/expected.json` is generated from a bounded C harness that ports the current `scripts/genksyms/genksyms.c` CRC logic over committed symbol-like input strings.
- `scripts/zigux/check-genksyms-crc-diff.py` compares that committed JSON against both the bounded C harness and `scripts/zigux/genksyms_crc.zig`, then reruns each side to prove repeat-run JSON determinism before the lane passes.
- `zigux/tests/fixtures/kconfig_bridge/*.json` capture bounded wrapper-first `conf` / `confdata` bridge outputs for committed Kconfig inputs.
- `scripts/zigux/check-kconfig-bridge.py` compares those committed JSON fixtures against `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig`, reruns both the `conf` and `confdata` bridge flows to prove conf and confdata repeat-run JSON determinism, and replays the `confdata` bridge through a second rebuild so repeat-run JSON determinism stays explicit before the lane passes.
- `zigux/tests/fixtures/phase2_cross_targets.json` fixes the bounded cross-target compile set for the Phase 2 tool tranche.
- `zigux/tests/fixtures/mk_elfconfig/elf32_expected.json` and sibling JSON fixtures capture bounded stdin-driven behavior for `scripts/mod/mk_elfconfig.c`.
- `scripts/zigux/check-mk-elfconfig-diff.py --self-test` keeps the bounded mk_elfconfig checker packet reviewable before the live artifact replay runs, so fixture-shape and explicit-tool drift fail without depending on local compiler or Zig availability.
- `scripts/zigux/check-mk-elfconfig-diff.py` compares those committed JSON results against both the C tool and `scripts/zigux/mk_elfconfig.zig`, then reruns each side to prove repeat-run JSON determinism before the lane passes.

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
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_policy/expected.json` anchors the bounded Phase 3 chrdev notify ack policy parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-policy` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack policy dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window/expected.json` anchors the bounded Phase 3 chrdev notify ack window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy/expected.json` anchors the bounded Phase 3 chrdev notify ack window policy parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-window-policy` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack window policy dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget/expected.json` anchors the bounded Phase 3 chrdev notify ack window policy budget parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-window-policy-budget` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack window policy budget dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window/expected.json` anchors the bounded Phase 3 chrdev notify ack window policy budget window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-window-policy-budget-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack window policy budget window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery/expected.json` anchors the bounded Phase 3 chrdev notify ack window policy budget window delivery parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-window-policy-budget-window-delivery` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack window policy budget window delivery dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window/expected.json` anchors the bounded Phase 3 chrdev notify ack window policy budget window delivery window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-window-policy-budget-window-delivery-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack window policy budget window delivery window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget/expected.json` anchors the bounded Phase 3 chrdev notify ack window policy budget window delivery window budget parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-window-policy-budget-window-delivery-window-budget` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack window policy budget window delivery window budget dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_budget/expected.json` anchors the bounded Phase 3 chrdev notify budget parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-budget` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify budget dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_policy/expected.json` anchors the bounded Phase 3 chrdev notify policy parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-policy` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify policy dump.
- `zigux/tests/fixtures/phase3_chrdev_open/expected.json` anchors the bounded Phase 3 chrdev open parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-open` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev open dump.
- `zigux/tests/fixtures/phase3_chrdev_requeue/expected.json` anchors the bounded Phase 3 chrdev requeue parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-requeue` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev requeue dump.
- `zigux/tests/fixtures/phase3_chrdev_resume/expected.json` anchors the bounded Phase 3 chrdev resume parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-resume` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev resume dump.
- `zigux/tests/fixtures/phase3_chrdev_retry/expected.json` anchors the bounded Phase 3 chrdev retry parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-retry` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev retry dump.
- `zigux/tests/fixtures/phase3_chrdev_route/expected.json` anchors the bounded Phase 3 chrdev route parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-route` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev route dump.
- `zigux/tests/fixtures/phase3_chrdev_xfer/expected.json` anchors the bounded Phase 3 chrdev xfer parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-xfer` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev xfer dump.
- `zigux/tests/fixtures/phase3_dev_region/expected.json` anchors the bounded Phase 3 dev region parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug dev-region` compares that committed JSON fixture against both the bounded C harness and the Zig dev region dump.
- `zigux/tests/fixtures/phase3_errptr_xarray/expected.json` anchors the bounded Phase 3 err_ptr/xarray parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug errptr-xarray` compares that committed JSON fixture against both the bounded C harness and the Zig err_ptr/xarray dump.
- `zigux/tests/fixtures/phase3_ida_alloc/expected.json` anchors the bounded Phase 3 ida allocation parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug ida-alloc` compares that committed JSON fixture against both the bounded C harness and the Zig ida allocation dump.
- `zigux/tests/fixtures/phase3_ida_bitmap/expected.json` anchors the bounded Phase 3 ida bitmap parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug ida-bitmap` compares that committed JSON fixture against both the bounded C harness and the Zig ida bitmap dump.
- `zigux/tests/fixtures/phase3_ida_policy/expected.json` anchors the bounded Phase 3 ida policy parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug ida-policy` compares that committed JSON fixture against both the bounded C harness and the Zig ida policy dump.
- `zigux/tests/fixtures/phase3_ida_range/expected.json` anchors the bounded Phase 3 ida range parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug ida-range` compares that committed JSON fixture against both the bounded C harness and the Zig ida range dump.
- `zigux/tests/fixtures/phase3_ida_range_set/expected.json` anchors the bounded Phase 3 ida range-set parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug ida-range-set` compares that committed JSON fixture against both the bounded C harness and the Zig ida range-set dump.
- `zigux/tests/fixtures/phase3_idr_slot/expected.json` anchors the bounded Phase 3 idr slot parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug idr-slot` compares that committed JSON fixture against both the bounded C harness and the Zig idr slot dump.
- `zigux/tests/fixtures/phase3_list_hlist/expected.json` anchors the bounded Phase 3 list/hlist parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug list-hlist` compares that committed JSON fixture against both the bounded C harness and the Zig list/hlist dump.
- `zigux/tests/fixtures/phase3_minor_alloc/expected.json` anchors the bounded Phase 3 minor allocation parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug minor-alloc` compares that committed JSON fixture against both the bounded C harness and the Zig minor allocation dump.
- `zigux/tests/fixtures/phase3_xarray_slot/expected.json` anchors the bounded Phase 3 xarray slot parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug xarray-slot` compares that committed JSON fixture against both the bounded C harness and the Zig xarray slot dump.
- `zigux/tests/fixtures/phase3_rbtree/expected.json` anchors the bounded Phase 3 rbtree parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug rbtree` compares that committed JSON fixture against both the bounded C harness and the Zig rbtree dump.

Current Phase 4 use
- `python3 scripts/zigux/artifact_diff.py --self-test` now publishes `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=18` for the shared comparison layer before the rollback-readiness lanes run: text pass, text mismatch, and missing expected, actual, and both text files; JSON pass, direct JSON mismatch, malformed expected, malformed actual, both-broken expected-first fail-closed JSON, and missing expected, actual, and both JSON files; and SHA-256 pass, digest drift, and missing expected, actual, and both binary files. That same helper self-test now also reruns the stable text pass, direct JSON mismatch, malformed expected JSON, malformed actual JSON, SHA-256 drift, and both-missing binary failure shapes back to back so deterministic shared-helper output does not depend on a single pass.
- `python3 scripts/zigux/check-artifact-diff-contract.py` keeps the published outward contract catalog explicit as 22 base checks plus 4 repeat replays: the helper self-test handoff; the `-h` help success shape; the required-args parser failure shape; the missing-actual-operand parser failure shape; the invalid `--mode` choice parser failure shape; text pass, text mismatch, and missing expected, actual, and both text files; JSON pass, direct JSON mismatch, missing expected, actual, and both JSON files, plus malformed expected, actual, and both-broken JSON with expected-first fail-closed reporting; and SHA-256 pass, missing expected, actual, and both files, plus digest drift. That keeps the outward usage banner, help text, `ARTIFACT_DIFF=...`, `MODE=...`, `EXPECTED_EXISTS=...`, `ACTUAL_EXISTS=...`, `EXPECTED_JSON_ERROR=...`, `ACTUAL_JSON_ERROR=...`, `SHA256=...`, `EXPECTED_SHA256=...`, and `ACTUAL_SHA256=...` fields small, auditable, and easy to refresh.
- that same contract replay now reruns the helper self-test, stable text pass, direct JSON mismatch, and SHA-256 drift cases back to back, so repeat-run CLI output stays reviewable instead of being inferred from one-shot cases alone.
- the published `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=22`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=4`, and `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=26` outputs keep stale expected-output and catalog drift small, auditable, and easy to refresh, with the help surface and parser failure shapes now called out explicitly alongside the malformed JSON failure markers named through `EXPECTED_JSON_ERROR=` and `ACTUAL_JSON_ERROR=` and the binary both-missing `EXPECTED_EXISTS=False` plus `ACTUAL_EXISTS=False` fail shape.
- the Phase 4 rollback-readiness packet stays grounded in `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_test_fsmount_manifest.json`, `zigux/tests/phase4_test_fsmount_survey.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_build.zig`, `scripts/zigux/validate-phase4.py`, `Documentation/zigux/artifact-diff.md`, and `Documentation/zigux/phase4-validation-matrix.md` so the shipped gate surface remains reviewable from one bounded note.
- that packet now keeps the shared `phase4-test-fsmount-survey-tests` and `phase4-perf-baseline-survey-tests` build entries explicit alongside the rollback gates, plus the dedicated `make -C zigux phase4-test-fsmount-survey` and `make -C zigux phase4-perf-baseline-survey` local replay paths.
- that packet now names the reversible-delivery and threshold posture explicitly: the current C anchor remains the source of truth for each bounded lane, `make M=samples/vfs` stays the current C-anchor-only lab posture while `samples/zigux/test_fsmount.zig` remains absent, and `perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land` stays the machine-checked posture until bounded benchmark commands and acceptable limits land.

## Review Rule

- if `scripts/zigux/artifact_diff.py` or `scripts/zigux/check-artifact-diff-contract.py` changes, refresh `Documentation/zigux/phase4-validation-matrix.md` and `Documentation/zigux/phase4-gate-evidence.md` in the same change so the current owner, rollback owner, deterministic preflight, and outward CLI contract stay reviewable together.
- if the shared helper or external contract replay adds or removes a published case, refresh the exact `ARTIFACT_DIFF_SELF_TEST_*` or `ARTIFACT_DIFF_CONTRACT_*` summary lines in this note in the same change instead of leaving the tooling packet split between code and run memory.

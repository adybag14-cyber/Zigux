# Artifact Diff Policy

Zigux uses committed artifacts only when they anchor a bounded parity claim.

Current Phase 1 use
- `zigux/tests/fixtures/phase1_helpers.json` is generated from the in-tree C helper implementations.
- `scripts/zigux/check-phase1-parity.py` rebuilds that artifact and compares it against the committed JSON.
- `scripts/zigux/artifact_diff.py` is the generic comparison layer that future Phase 2 tooling work will reuse.

Current Phase 2 use
- `zigux/tests/fixtures/fixdep/sample_expected.txt` is generated from the current in-tree C `scripts/basic/fixdep.c` behavior on a bounded committed sample.
- `zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt` anchors the escaped-whitespace dependency-token path so `fixdep.zig` must preserve escaped separators the same way as the C tool.
- `zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt` anchors the escaped-colon dependency-token path so `fixdep.zig` must unescape `\:` to the same on-disk dependency name that the C tool reads and emits.
- `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt` widens that claim with a second committed depfile covering multi-target parsing, comments, duplicate deps, no-parse files, and escaped `#`.
- `zigux/tests/fixtures/fixdep/sample_concatenated_expected.txt` anchors the concatenated-target packet so `fixdep.zig` keeps the first source while still collecting later dependency tokens across the continued target entries.
- `zigux/tests/fixtures/fixdep/sample_comment_continuation_expected.txt` anchors escaped-newline rustc-style comments before the first target so `fixdep.zig` keeps skipping the continued comment until the next real newline.
- `zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt` plus `sample_comment_only_expected.stderr.txt` anchor the bounded comment-only depfile failure path while keeping the saved command line deterministic.
- `zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt` plus `sample_missing_dep_expected.stderr.txt` anchor the bounded missing-dependency open error and its exit-code contract while keeping stdout stable.
- `zigux/tests/fixtures/fixdep/sample_output_write_expected.txt` plus `sample_output_write_expected.stderr.txt` anchor the bounded stdout-write failure path for the main success packet and the replay variants that drive stdout into `/dev/full`.
- `zigux/tests/fixtures/fixdep/cases.json` keeps the current eleven-case fixdep packet reviewable by naming the committed stdout artifact for every shipped case and the expected stderr or exit-code contract whenever the case is not a plain success path, including the dedicated `sample_comment_continuation`, `sample_output_write`, `sample_comment_only_stdout_full`, and `sample_missing_dep_stdout_full` write-failure replays.
- `scripts/zigux/check-fixdep-diff.py` compares the committed fixdep samples against both the C tool and `scripts/zigux/fixdep.zig`.
- `zigux/tests/fixtures/genksyms_bridge/*.json` capture bounded wrapper-first `genksyms` invocation planning for committed flag combinations.
- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json` anchors the smallest wrapper-first `genksyms` invocation claim.
- `scripts/zigux/check-genksyms-bridge.py` compares those committed JSON fixtures against both a bounded C harness and `scripts/zigux/genksyms.zig`.
- `zigux/tests/fixtures/genksyms_crc/expected.json` is generated from a bounded C harness that ports the current `scripts/genksyms/genksyms.c` CRC logic over committed symbol-like input strings.
- `scripts/zigux/check-genksyms-crc-diff.py` compares that committed JSON against both the bounded C harness and `scripts/zigux/genksyms_crc.zig`.
- `zigux/tests/fixtures/kconfig_bridge/*.json` capture bounded wrapper-first `conf` / `confdata` bridge outputs for committed Kconfig inputs.
- `scripts/zigux/check-kconfig-bridge.py` compares those committed JSON fixtures against `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig`.
- `zigux/tests/fixtures/phase2_cross_targets.json` fixes the bounded cross-target compile set for the Phase 2 tool tranche.
- `zigux/tests/fixtures/mk_elfconfig/elf32_expected.json` and sibling JSON fixtures capture bounded stdin-driven behavior for `scripts/mod/mk_elfconfig.c`.
- `scripts/zigux/check-mk-elfconfig-diff.py` compares those committed JSON results against both the C tool and `scripts/zigux/mk_elfconfig.zig`.

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
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window delivery window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window budget window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window delivery window budget window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window budget window delivery window budget window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window delivery window budget window delivery window budget window dump.
- `zigux/tests/fixtures/phase3_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window/expected.json` anchors the bounded Phase 3 chrdev notify ack delivery budget guard window policy budget window delivery window budget window delivery window budget window delivery window budget window parity claim.
- `python3 scripts/zigux/run-phase3-checks.py --slug chrdev-notify-ack-delivery-budget-guard-window-policy-budget-window-delivery-window-budget-window-delivery-window-budget-window-delivery-window-budget-window` compares that committed JSON fixture against both the bounded C harness and the Zig chrdev notify ack delivery budget guard window policy budget window delivery window budget window delivery window budget window delivery window budget window dump.

Current Phase 4 use
- `scripts/zigux/artifact_diff.py` stays the shared host-side comparison helper behind the committed artifact-check packets.
- `scripts/zigux/check-artifact-diff-contract.py` reruns the bounded helper self-test, CLI help output, missing-required-args, missing-actual-operand, and invalid-mode parser coverage plus the text, JSON, SHA-256, missing-path, malformed-input, and repeat-run cases so the helper's outward contract stays deterministic before the broader Phase 4 validator and Zig gates run.
- `scripts/zigux/check-phase4-artifact-diff-determinism.py` rechecks the helper and contract summary catalogs together so case-count, case-order, and repeat-case drift fail closed before the shared Phase 4 validator and Zig gates run.
- `scripts/zigux/check-phase4-gate-evidence.py` together with `Documentation/zigux/phase4-gate-evidence.md` keeps the dedicated exact-readback companion packet explicit beside the broader validator-backed rollback surface without turning this note into the full ownership record.
- `zigux/tests/atomic64_diff.zig` keeps the roadmap-named Phase 4 atomic64 entrypoint explicit as the thin wrapper over the shared runtime-backed replay.
- `zigux/tests/runtime_atomic64_diff.zig` currently carries the single live bounded atomic64 rollback-readiness replay body that the Phase 4 wrapper and the Phase 9 starter both reuse.
- `zigux/tests/bitmap_diff.zig` anchors the bounded bitmap rollback-readiness parity checks.
- `zigux/tests/phase4_bitmap_live_helper_replay.zig` keeps the shipped helper-backed exact-fill versus rounded-zero bitmap semantics reviewable beside the synthetic bitmap rollback gate.
- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` keeps the manifest-backed runtime atomic64 wrapper handoff reviewable beside the live wrapper gate without widening the shipped rollback contract.
- `zigux/tests/phase4_bitmap_diff_survey.zig` keeps the manifest-backed bitmap rollback survey reviewable beside the live bitmap gate and helper-backed replay without widening the shipped rollback contract.
- `zigux/tests/phase4_build.zig` keeps the five currently shared Phase 4 rollback-readiness replays on one shared test packet surfaced through both `zig build test --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-test`.
- `scripts/zigux/validate-phase4.py` keeps the shared Phase 4 validator packet, workflow wiring, the artifact-diff contract checker, the artifact-diff determinism checker, and the Phase 4 documentation markers aligned before the Zig tests run.
- `Documentation/zigux/phase4-validation-matrix.md` records the current rollback owners, threshold posture, and lab/CI replay matrix for the shipped Phase 4 gates.
- `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig` keep the still-absent roadmap `samples/zigux/kprobe_example.zig` starter measurable through the dedicated local `zig test zigux/tests/phase4_kprobe_example_survey.zig` route and the matching `make -C zigux phase4-kprobe-example-survey` wrapper while that parked packet stays adjacent to the shared rollback-readiness entrypoint rather than part of the shared `phase4-test` replay.
- `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig` keep the still-absent roadmap `samples/zigux/test_fsmount.zig` starter measurable through the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` route while that parked packet stays adjacent to the shared rollback-readiness entrypoint rather than part of the shared `phase4-test` replay.

## Phase 4 Exact Check Packet

- `python3 scripts/zigux/artifact_diff.py --self-test` is the direct helper replay and must emit `ARTIFACT_DIFF_SELF_TEST=pass`, `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=19`, and this exact case packet: `text_pass`, `text_mismatch`, `json_pass`, `json_mismatch`, `json_invalid_expected`, `json_invalid_actual`, `json_invalid_both`, `json_missing_expected`, `json_missing_actual`, `json_missing_both`, `sha256_pass`, `sha256_drift`, `text_missing_expected`, `text_missing_actual`, `text_missing_both`, `sha256_missing_expected`, `sha256_missing_actual`, `sha256_missing_both`, and `invalid_mode_rejected`.
- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test` is the isolated checker replay and must emit `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`, `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=18`, and this exact self-test packet: `catalog_shape`, `review_note_marker_round_trip`, `review_note_owner_marker_drift`, `review_note_marker_drift`, `helper_summary_round_trip`, `contract_summary_round_trip`, `helper_summary_status_drift`, `helper_summary_count_drift`, `helper_summary_duplicate_case_drift`, `helper_summary_case_order_drift`, `contract_summary_status_drift`, `contract_summary_base_count_drift`, `contract_summary_base_case_order_drift`, `contract_summary_repeat_count_drift`, `contract_summary_repeat_case_order_drift`, `contract_summary_case_count_drift`, `contract_summary_duplicate_case_drift`, and `contract_summary_case_order_drift`.
- `python3 scripts/zigux/check-artifact-diff-contract.py` is the live outward contract replay and must rerun `python3 scripts/zigux/artifact_diff.py --self-test` twice, rerun `python3 scripts/zigux/artifact_diff.py -h` twice, rerun the missing-required-args parser failure twice, rerun the missing-actual-operand parser failure twice, rerun the invalid-mode parser failure twice, and then emit `ARTIFACT_DIFF_CONTRACT=pass`, `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`, and `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=28`.
- `ARTIFACT_DIFF_CONTRACT_BASE_CASES` must stay this exact base packet: `helper_self_test`, `cli_help_output`, `cli_missing_required_args`, `cli_missing_actual_operand`, `cli_invalid_mode`, `text_pass`, `text_mismatch`, `text_missing_expected`, `text_missing_actual`, `text_missing_both`, `json_pass`, `json_mismatch`, `json_missing_expected`, `json_missing_actual`, `json_missing_both`, `json_invalid_expected`, `json_invalid_actual`, `json_invalid_both`, `sha256_pass`, `sha256_missing_expected`, `sha256_missing_actual`, `sha256_missing_both`, and `sha256_drift`.
- `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES` must stay this exact repeat packet: `helper_self_test_repeat`, `cli_help_output_repeat`, `text_pass_repeat`, `json_mismatch_repeat`, and `sha256_drift_repeat`.
- `ARTIFACT_DIFF_CONTRACT_CASES` must stay the ordered union of those base and repeat packets, including the paired CLI help-output replays inside the same published contract catalog.
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test` is the isolated catalog-drift replay and must emit `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass`, `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=19`, and this exact self-test packet: `catalog_shape`, `phase4_use_marker_round_trip`, `phase4_use_marker_drift`, `review_note_marker_round_trip`, `review_note_marker_drift`, `docs_root_marker_round_trip`, `docs_root_marker_drift`, `scripts_root_marker_round_trip`, `scripts_root_marker_drift`, `helper_summary_round_trip`, `helper_summary_count_drift`, `helper_summary_case_order_drift`, `contract_self_test_round_trip`, `contract_self_test_count_drift`, `contract_self_test_missing_owner_review_note_drift`, `contract_self_test_case_order_drift`, `contract_summary_round_trip`, `contract_summary_case_count_drift`, and `contract_summary_case_order_drift`.
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` is the live summary replay and must rerun the helper self-test summary packet, the contract self-test summary packet, the full 28-case contract summary packet, the required Phase 4 use markers above, and the required review-note markers below before it emits `PHASE4_ARTIFACT_DIFF_DETERMINISM=pass`, `PHASE4_ARTIFACT_DIFF_HELPER_SELF_TEST_CASE_COUNT=19`, `PHASE4_ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=18`, and `PHASE4_ARTIFACT_DIFF_CONTRACT_CASE_COUNT=28`.

## Phase 4 Tooling Review Note

- owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`
- rollback owner: `Zigux product maintainers working in scripts/zigux and Documentation/zigux`
- fallback rule: if `scripts/zigux/artifact_diff.py` regresses, keep the committed expected artifact plus the current authoritative C or documented replay command as the source of truth until the helper contract is repaired
- rollback repair gate: `python3 scripts/zigux/check-artifact-diff-contract.py` and `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` must both pass again before a repaired `scripts/zigux/artifact_diff.py` helper change can be treated as closed
- deterministic replay entrypoint: `python3 scripts/zigux/check-artifact-diff-contract.py` is the reviewable contract rerun for the shared host-side helper and should stay aligned with the outward line rules below
- deterministic survey entrypoint: `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` must keep the helper self-test catalog, the contract summary catalog, and the repeat-case packet aligned with this note and the shared validator packet
- review rule: any change to the helper's emitted `ARTIFACT_DIFF=*`, `MODE=*`, `EXPECTED=*`, `ACTUAL=*`, `SHA256=*`, `EXPECTED_EXISTS=*`, `ACTUAL_EXISTS=*`, `EXPECTED_JSON_ERROR=*`, or `ACTUAL_JSON_ERROR=*` lines must update this note in the same change so the published host-side artifact packet stays reviewable
- boundary: keep this note scoped to the shared host-side diff helper; Phase 4 gate ownership for `zigux/tests/*.zig` still belongs in `Documentation/zigux/phase4-validation-matrix.md`
- deterministic helper contract: `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]`
- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_TEXT` must prove both the stable text pass shape and the direct text mismatch fail shape
- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_JSON` must prove canonical JSON equivalence
- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_JSON_INVALID` must prove malformed JSON fails without inventing digest or exists markers
- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_SHA256` must prove both the shared digest pass line and the exact expected-vs-actual digest drift lines
- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_MISSING` must prove missing-path failures emit only the EXISTS markers
- deterministic helper catalog: `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_SELF_TEST_CASES` must stay aligned with the helper's published `--self-test` packet
- deterministic checker catalog: `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_BASE_CASES`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES`, `ARTIFACT_DIFF_CONTRACT_CASE_COUNT`, and `ARTIFACT_DIFF_CONTRACT_CASES` must stay aligned with the published contract replay packet
- deterministic checker self-test catalog: `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES` must stay aligned with the isolated stale-catalog and review-note drift coverage
- deterministic survey self-test catalog: `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT` and `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES` must stay aligned with the isolated phase4-use, review-note, helper-summary, and contract-catalog drift coverage

Rules
- artifact fixtures must be generated from the current in-tree source of truth
- fixture scope must stay small and reviewable
- fixture updates must be intentional and committed alongside the code change that caused them
- do not use opaque binary blobs for early bootstrap parity when a text or JSON artifact is possible

Near-term target
- reuse the same artifact-diff pattern for Phase 2 dual-implementation and bridge outputs such as `fixdep`, `genksyms`, `genksyms_crc`, `kconfig_bridge`, and `mk_elfconfig`
- keep using the same pattern for the full bounded Phase 3 interop ladder, with `python3 scripts/zigux/run-phase3-checks.py --slug <slice>` as the only documented execution entrypoint for those committed parity fixtures.

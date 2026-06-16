const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_TESTS_README_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass";

const REQUIRED_TESTS_README_MARKERS = [_][]const u8{
    "Phase 2 review packet",
    "current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`scripts\\zigux/validate_phase2.zig`",
    "`scripts\\zigux/validate_phase2_closure.zig`",
    "`scripts\\zigux/check_zig_toolchain.zig`",
    "`scripts\\zigux/check_phase2_kbuild_routes.zig`",
    "`scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig`",
    "`scripts\\zigux/check_kconfig_bridge.zig`",
    "current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`",
    "`scripts\\zigux/check_phase2_tests_readme_alignment.zig`",
    "`scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_cross_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pinning.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`scripts/zigux/install_zig.zig`",
    "`scripts\\zigux/check_phase2_cross.zig`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --self-test`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --policy-only`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing`",
    "`zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig --self-test`",
    "`zig run scripts/zigux/install_zig.zig --self-test`",
    "`zig run scripts\\zigux/check_phase2_cross.zig --self-test`",
    "Keep the current toolchain self-check and replay surface explicit through `zig run scripts\\zigux/check_zig_toolchain.zig --self-test`, `zig run scripts\\zigux/check_zig_toolchain.zig --policy-only`, `zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing`, `zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig --self-test`, `zig run scripts/zigux/install_zig.zig --self-test`, and `zig run scripts\\zigux/check_phase2_cross.zig --self-test`.",
    "`third_party/README.md`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts\\zigux/check_lane05_local_first_archive_workflow.zig`, and `scripts\\zigux/check_lane05_local_archive_readme.zig`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz`, `zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, canonical `adybag14-cyber/zig` release, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
    "keep the local-first archive workflow replay surface explicit through `zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig --self-test`, `zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig`, `zig run scripts\\zigux/check_lane05_local_archive_readme.zig --self-test`, and `zig run scripts\\zigux/check_lane05_local_archive_readme.zig`.",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`scripts/zigux/genksyms_inline_short_option_argument_test.zig`",
    "`scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig`",
    "`scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig`",
    "`scripts/zigux/fixdep.zig`",
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`zigux/Makefile`",
    "current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "keep `scripts/zigux/zig-toolchain-policy.json`, the pinned `x86_64-linux` bootstrap archive note, the live `zig run scripts\\zigux/check_zig_toolchain.zig --policy-only` plus `zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing` replays, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts\\zigux/check_zig_toolchain.zig` and pin-scope guards explicit in this tests-root packet",
    "current `master` now directly materializes `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig --self-test`, `scripts\\zigux/check_phase2_cross.zig`, `zig run scripts\\zigux/check_phase2_cross.zig --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
    "current `master` also directly materializes `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig`, `scripts\\zigux/check_genksyms_bridge.zig`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `scripts/zigux/genksyms_inline_short_option_argument_test.zig`, `scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig`, `scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned survey, selftest-alignment, checker, bridge helper, standalone proof, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
    "current `master` also directly materializes `scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, helper-local kconfig allconfig, the survey-backed genksyms packet, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
};

const EXACT_COUNT_TESTS_README_MARKERS = [_][]const u8{
    "Keep the current toolchain self-check and replay surface explicit through `zig run scripts\\zigux/check_zig_toolchain.zig --self-test`, `zig run scripts\\zigux/check_zig_toolchain.zig --policy-only`, `zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing`, `zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig --self-test`, `zig run scripts/zigux/install_zig.zig --self-test`, and `zig run scripts\\zigux/check_phase2_cross.zig --self-test`.",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts\\zigux/check_lane05_local_first_archive_workflow.zig`, and `scripts\\zigux/check_lane05_local_archive_readme.zig`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz`, `zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, canonical `adybag14-cyber/zig` release, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
    "keep the local-first archive workflow replay surface explicit through `zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig --self-test`, `zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig`, `zig run scripts\\zigux/check_lane05_local_archive_readme.zig --self-test`, and `zig run scripts\\zigux/check_lane05_local_archive_readme.zig`.",
    "`zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig --self-test`",
    "`zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`zig run scripts\\zigux/check_lane05_local_archive_readme.zig --self-test`",
    "`zig run scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
};

const FORBIDDEN_TESTS_README_MARKERS = [_][]const u8{
    "`scripts/zigux/install_zig.zig`, `scripts\\zigux/check_zig_toolchain.zig`",
    "`zig run scripts/zigux/install_zig.zig --self-test`, `zig run scripts\\zigux/check_zig_toolchain.zig --self-test`",
    "`zig run scripts\\zigux/check_phase2_cross_selftest_alignment.zig --self-test`",
    "`zig run scripts\\zigux/check_phase2_cross_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig --self-test`",
    "`zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase2-closure.md`",
    "repeated authenticated reads on current `master` still return missing for `scripts\\zigux/validate_phase2_closure.zig`, `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `zigux/Makefile`",
    "repeated authenticated reads on current `master` still return missing for `scripts\\zigux/validate_phase2_closure.zig`, `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig`, `zigux/tests/fixtures/phase2_cross_targets.json`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, and `make -C zigux phase2`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, and closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "keep the fixture-backed tool-manifest and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as historical packet members rather than shipped current-`master` evidence",
};

const REQUIRED_DOCS_ROOT_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase2_tests_readme_alignment.zig`",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`",
    "`scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig`",
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`scripts/zigux/install_zig.zig`",
    "`scripts\\zigux/check_phase2_cross.zig`",
    "`zig run scripts\\zigux/validate_phase2.zig`",
    "keep the bounded Phase 2 docs-root packet explicit through the returned closure-side validator pair, the shipped installer and direct cross-route companions, the surviving toolchain, shared-reminder, and manifest guards, the selected kconfig bridge helpers, the bounded genksyms bridge helper packet, the current manifests, and the shipped make-wrapper routes instead of treating that now-rematerialized tranche as historical-only evidence.",
    "the current docs-root Phase 2 reminder packet should stay parked on `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts\\zigux/validate_phase2.zig`, `scripts\\zigux/validate_phase2_closure.zig`, and `zigux/Makefile`, with `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/phase2_cross_targets.json`, the current kconfig bridge manifests, and the current genksyms bridge fixture roster keeping the same packet aligned across docs-root, scripts-root, and tests-root surfaces.",
    "`scripts/zigux/install_zig.zig`, `scripts\\zigux/check_phase2_cross.zig`, `scripts\\zigux/check_phase2_cross_selftest_alignment.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.",
    "`zig run scripts\\zigux/validate_phase2.zig`, `zig run scripts\\zigux/validate_phase2_closure.zig`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`zigux/tests/README.md`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
};

const REQUIRED_PHASE2_TOOL_MANIFEST_SURFACES = [_][]const u8{
    "scripts\\zigux/check_phase2_tests_readme_alignment.zig",
    "scripts\\zigux/check_phase2_docs_shared_reminder.zig",
    "scripts\\zigux/check_phase2_tool_manifest.zig",
    "scripts\\zigux/check_phase2_artifact_tools_manifest.zig",
    "scripts\\zigux/check_phase2_required_make_routes.zig",
    "scripts\\zigux/check_kconfig_bridge.zig",
    "scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig",
    "scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    "scripts\\zigux/check_phase2_cross.zig",
    "scripts\\zigux/check_phase2_cross_selftest_alignment.zig",
    "scripts\\zigux/check_lane05_install_zig_archive_verification.zig",
    "scripts\\zigux/check_lane05_stage_helper_contract.zig",
    "scripts\\zigux/check_lane05_stage_helper_selftest.zig",
    "scripts\\zigux/check_genksyms_bridge.zig",
    "scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig",
    "scripts\\zigux/check_phase2_fixdep_gate.zig",
    "scripts\\zigux/check_fixdep_diff.zig",
    "scripts/zigux/install_zig.zig",
    "scripts/zigux/stage_pinned_zig_archive.zig",
    "scripts/zigux/artifact_diff.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "scripts/zigux/genksyms_inline_short_option_argument_test.zig",
    "scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig",
    "scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig",
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/fixdep/cases.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_tests_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_tests_readme_markers_path);
    const text_required_tests_readme_markers = try guard.readUtf8File(io, allocator, text_required_tests_readme_markers_path);
    defer allocator.free(text_required_tests_readme_markers);
    for (REQUIRED_TESTS_README_MARKERS) |marker| try guard.requireMarker(text_required_tests_readme_markers, marker);
    const text_exact_count_tests_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_exact_count_tests_readme_markers_path);
    const text_exact_count_tests_readme_markers = try guard.readUtf8File(io, allocator, text_exact_count_tests_readme_markers_path);
    defer allocator.free(text_exact_count_tests_readme_markers);
    for (EXACT_COUNT_TESTS_README_MARKERS) |marker| try guard.requireMarker(text_exact_count_tests_readme_markers, marker);
    const text_forbidden_tests_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_forbidden_tests_readme_markers_path);
    const text_forbidden_tests_readme_markers = try guard.readUtf8File(io, allocator, text_forbidden_tests_readme_markers_path);
    defer allocator.free(text_forbidden_tests_readme_markers);
    for (FORBIDDEN_TESTS_README_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_tests_readme_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_required_docs_root_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_docs_root_markers_path);
    const text_required_docs_root_markers = try guard.readUtf8File(io, allocator, text_required_docs_root_markers_path);
    defer allocator.free(text_required_docs_root_markers);
    for (REQUIRED_DOCS_ROOT_MARKERS) |marker| try guard.requireMarker(text_required_docs_root_markers, marker);
    const text_required_phase2_tool_manifest_surfaces_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_phase2_tool_manifest_surfaces_path);
    const text_required_phase2_tool_manifest_surfaces = try guard.readUtf8File(io, allocator, text_required_phase2_tool_manifest_surfaces_path);
    defer allocator.free(text_required_phase2_tool_manifest_surfaces);
    for (REQUIRED_PHASE2_TOOL_MANIFEST_SURFACES) |marker| try guard.requireMarker(text_required_phase2_tool_manifest_surfaces, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

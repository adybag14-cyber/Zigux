const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_DOCS_SHARED_REMINDER=pass";
pub const self_test_pass_marker = "PHASE2_DOCS_SHARED_REMINDER_SELF_TEST=pass";

const DOCS_README_MARKERS = [_][]const u8{
    "Phase 2 notes",
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`third_party/README.md`, `scripts\\zigux/check_lane05_local_first_archive_workflow.zig`, and `scripts\\zigux/check_lane05_local_archive_readme.zig` are directly readable on current `master` again, so keep the repo-local pinned archive contract, the `zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux` replay, the local-first `third_party`, canonical `adybag14-cyber/zig` release, mirror, then direct-download bootstrap order, and the two shipped Lane 05 reminder guards explicit from the docs root beside the returned toolchain packet.",
    "`scripts/zigux/install_zig.zig`, `scripts\\zigux/check_phase2_cross.zig`, `scripts\\zigux/check_phase2_cross_selftest_alignment.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.",
    "`zig run scripts\\zigux/validate_phase2.zig`, `zig run scripts\\zigux/validate_phase2_closure.zig`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
};

const PHASE2_NOTES_MARKERS = [_][]const u8{
    "# Phase 2 Toolchain Bootstrap Notes",
    "## Current direct packet",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`",
    "`scripts\\zigux/check_phase2_tests_readme_alignment.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig`",
    "`scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "`scripts/zigux/install_zig.zig`, `scripts\\zigux/check_lane05_install_zig_archive_verification.zig`, `scripts/zigux/stage_pinned_zig_archive.zig`, `scripts\\zigux/check_lane05_stage_helper_contract.zig`, and `scripts\\zigux/check_lane05_stage_helper_selftest.zig` are directly readable on current `master` and keep the pinned-channel archive download, staged repo-local archive materialization, archive-verification, helper-contract, helper-selftest, and install-root replay path explicit beside the reminder guards.",
    "`scripts\\zigux/check_zig_toolchain.zig` is directly readable on current `master`",
    "`scripts/zigux/artifact_diff.zig` is directly readable on current `master`",
    "`third_party/README.md` is directly readable on current `master`",
    "`.github/workflows/zigux-bootstrap.yml` also derives `ZIGUX_ZIG_TARGET`, `ZIGUX_ZIG_FILENAME`, `ZIGUX_ZIG_URL`, and `ZIGUX_ZIG_CANONICAL_URL` from `scripts/zigux/zig-toolchain-policy.json` plus the canonical `adybag14-cyber/zig` release tag, tries the canonical release before `community-mirrors.txt` and the direct Zig download URL, and reruns `zig run scripts\\zigux/check_zig_toolchain.zig --zig \"$zig_path\"` inside each install attempt so the pinned bootstrap setup path stays reviewable at the same policy-driven boundary as the later reminder hooks.",
    "`zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig --self-test`",
    "`zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`zig run scripts\\zigux/check_lane05_local_archive_readme.zig --self-test`",
    "`zig run scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "`zig run scripts\\zigux/check_lane05_install_zig_archive_verification.zig --self-test`",
    "`zig run scripts\\zigux/check_lane05_install_zig_archive_verification.zig`",
    "`zig run scripts/zigux/stage_pinned_zig_archive.zig --self-test`",
    "`zig run scripts\\zigux/check_lane05_stage_helper_contract.zig --self-test`",
    "`zig run scripts\\zigux/check_lane05_stage_helper_contract.zig`",
    "`zig run scripts\\zigux/check_lane05_stage_helper_selftest.zig --self-test`",
    "`zig run scripts\\zigux/check_lane05_stage_helper_selftest.zig`",
    "`zig run scripts\\zigux/check_phase2_toolchain_pinning.zig --self-test`",
    "`zig run scripts\\zigux/check_phase2_toolchain_pinning.zig`",
    "`zig run scripts\\zigux/check_phase2_tests_readme_alignment.zig --self-test`",
    "`zig run scripts\\zigux/check_phase2_tests_readme_alignment.zig`",
    "`zig run scripts\\zigux/check_phase2_cross.zig --self-test`",
    "`zig run scripts\\zigux/check_phase2_cross.zig`",
    "`zig run scripts\\zigux/check_phase2_cross_selftest_alignment.zig --self-test`",
    "`zig run scripts\\zigux/check_phase2_cross_selftest_alignment.zig`",
    "`zig run scripts\\zigux/check_phase2_kbuild_routes.zig --self-test`",
    "`zig run scripts\\zigux/check_phase2_kbuild_routes.zig`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig`, `scripts\\zigux/check_genksyms_bridge.zig`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
    "The rematerialized make-wrapper packet is directly readable on current `master` through `make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-cross`",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness, direct cross-route truthfulness, local-first archive workflow truthfulness, archive-verification truthfulness, staged-archive helper truthfulness, third_party archive README truthfulness",
    "so the live bootstrap packet exercises the pinned-channel, pinned-archive integrity, local-first archive workflow, archive-verification, staged repo-local archive helper contract, staged archive helper selftest, third_party README contract, installer, toolchain-pinning, pin-scope, bootstrap workflow-route, kbuild-route, tests-root reminder, direct cross-route, cross-selftest alignment, required-make-route, docs-shared-reminder, manifest, artifact-support, primary artifact-diff helper, dedicated genksyms selftest-alignment guard, dedicated kconfig allconfig helper guard, genksyms bridge, kconfig bridge, fixdep governance and parity packet, and make-wrapper-backed `phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, `phase2-validate`, and aggregate `phase2` route replays instead of leaving the returned Phase 2 packet implicit beside the shipped CI path.",
};

const PHASE2_NOTES_FORBIDDEN_MARKERS = [_][]const u8{
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install_zig.zig`, `scripts\\zigux/check_phase2_cross.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "historical packet members until same-lane work rematerializes them on `master`",
    "without reviving missing installer or direct cross-route proof text",
    "`zigux/Makefile` and `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as repo-reality gaps",
};

const PHASE2_NOTES_EXACT_COUNT_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "`.github/workflows/zigux-bootstrap.yml` also derives `ZIGUX_ZIG_TARGET`, `ZIGUX_ZIG_FILENAME`, `ZIGUX_ZIG_URL`, and `ZIGUX_ZIG_CANONICAL_URL` from `scripts/zigux/zig-toolchain-policy.json` plus the canonical `adybag14-cyber/zig` release tag, tries the canonical release before `community-mirrors.txt` and the direct Zig download URL, and reruns `zig run scripts\\zigux/check_zig_toolchain.zig --zig \"$zig_path\"` inside each install attempt so the pinned bootstrap setup path stays reviewable at the same policy-driven boundary as the later reminder hooks.",
    "so the live bootstrap packet exercises the pinned-channel, pinned-archive integrity, local-first archive workflow, archive-verification, staged repo-local archive helper contract, staged archive helper selftest, third_party README contract, installer, toolchain-pinning, pin-scope, bootstrap workflow-route, kbuild-route, tests-root reminder, direct cross-route, cross-selftest alignment, required-make-route, docs-shared-reminder, manifest, artifact-support, primary artifact-diff helper, dedicated genksyms selftest-alignment guard, dedicated kconfig allconfig helper guard, genksyms bridge, kconfig bridge, fixdep governance and parity packet, and make-wrapper-backed `phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, `phase2-validate`, and aggregate `phase2` route replays instead of leaving the returned Phase 2 packet implicit beside the shipped CI path.",
};

const REVIEW_CHECKLIST_MARKERS = [_][]const u8{
    "* if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`third_party/README.md`",
    "`scripts/zigux/README.md`",
    "`scripts\\zigux/check_zig_toolchain.zig`",
    "`scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "`scripts\\zigux/check_phase2_kbuild_routes.zig`",
    "`scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_tests_readme_alignment.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pinning.zig`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`scripts\\zigux/check_phase2_cross_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts\\zigux/validate_phase2.zig`",
    "`scripts\\zigux/validate_phase2_closure.zig`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --self-test`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --policy-only`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux`",
    "`zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig --self-test`",
    "`zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`zig run scripts\\zigux/check_lane05_local_archive_readme.zig --self-test`",
    "`zig run scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "`zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig --self-test`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2`",
    "`scripts/zigux/install_zig.zig`",
    "`zig run scripts/zigux/install_zig.zig --self-test`",
    "`scripts\\zigux/check_phase2_cross.zig`",
    "`zig run scripts\\zigux/check_phase2_cross.zig --self-test`",
    "`zig run scripts\\zigux/check_phase2_cross.zig`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
};

const REVIEW_CHECKLIST_FORBIDDEN_MARKERS = [_][]const u8{
    "current directly readable Phase 2 toolchain, kbuild, kconfig bridge, docs-shared-reminder, and required-make-route packet",
    "current rematerialized Phase 2 closure-side, closure-validator, validation, artifact-support, toolchain self-check, and make-wrapper packet",
    "`scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig --self-test`, `scripts\\zigux/check_phase2_cross.zig`, `zig run scripts\\zigux/check_phase2_cross.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay framed as historical packet members rather than shipped current-`master` evidence",
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as historical packet members rather than shipped current-`master` evidence",
};

const REVIEW_CHECKLIST_EXACT_COUNT_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`third_party/README.md`, `scripts/zigux/stage_pinned_zig_archive.zig`, `zig run scripts/zigux/stage_pinned_zig_archive.zig --self-test`, `scripts\\zigux/check_lane05_stage_helper_contract.zig`, and `scripts\\zigux/check_lane05_stage_helper_selftest.zig` keep the repo-local archive contract and staged-helper packet explicit beside the canonical release fallback",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`",
    "`scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`scripts\\zigux/validate_phase2_closure.zig`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit",
    "`scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
};

const SCRIPTS_README_FORBIDDEN_MARKERS = [_][]const u8{
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install_zig.zig`",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` stay framed as repo-reality gaps",
};

const TESTS_README_MARKERS = [_][]const u8{
    "## Phase 2 review packet",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts\\zigux/check_lane05_local_first_archive_workflow.zig`, and `scripts\\zigux/check_lane05_local_archive_readme.zig`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "Keep the current toolchain self-check and replay surface explicit through `zig run scripts\\zigux/check_zig_toolchain.zig --self-test`, `zig run scripts\\zigux/check_zig_toolchain.zig --policy-only`, `zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing`, `zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig --self-test`, `zig run scripts/zigux/install_zig.zig --self-test`, and `zig run scripts\\zigux/check_phase2_cross.zig --self-test`.",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz`, `zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, canonical `adybag14-cyber/zig` release, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
    "keep the local-first archive workflow replay surface explicit through `zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig --self-test`, `zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig`, `zig run scripts\\zigux/check_lane05_local_archive_readme.zig --self-test`, and `zig run scripts\\zigux/check_lane05_local_archive_readme.zig`.",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
};

const TESTS_README_EXACT_COUNT_MARKERS = [_][]const u8{
    "keep the local-first archive workflow replay surface explicit through `zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig --self-test`, `zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig`, `zig run scripts\\zigux/check_lane05_local_archive_readme.zig --self-test`, and `zig run scripts\\zigux/check_lane05_local_archive_readme.zig`.",
};

const THIRD_PARTY_README_MARKERS = [_][]const u8{
    "# Zigux third-party archives",
    "## Current pinned Zig archive contract",
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.877+a3ae499dc`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz`",
    "- sha256: `c1fd3190ab9e03ba2ec339aff9f1371780dc0727dacd0b0edb7ae6ba936501d8`",
    "- size: `59581484` bytes",
    "## Validation",
    "- `zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux`",
    "- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz` when that pinned archive is present.",
    "- If the exact archive file is absent but `third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz.parts` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `scripts/zigux/stage_pinned_zig_archive.zig` before canonical release, mirror, or direct-download fallback.",
    "- Before retrying the canonical release, mirror, or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.",
    "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to the canonical `adybag14-cyber/zig` release before `community-mirrors.txt` and the direct `ziglang.org` download URL.",
    "- `scripts\\zigux/check_lane05_local_first_archive_workflow.zig` and `scripts\\zigux/check_lane05_local_archive_readme.zig` are the shipped reminder guards for that local-first archive path.",
    "- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.877+a3ae499dc (1).tar.xz` in this directory",
};

const THIRD_PARTY_README_EXACT_COUNT_MARKERS = [_][]const u8{
    "- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz` when that pinned archive is present.",
    "- If the exact archive file is absent but `third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz.parts` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `scripts/zigux/stage_pinned_zig_archive.zig` before canonical release, mirror, or direct-download fallback.",
    "- Before retrying the canonical release, mirror, or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.",
    "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to the canonical `adybag14-cyber/zig` release before `community-mirrors.txt` and the direct `ziglang.org` download URL.",
    "- `scripts\\zigux/check_lane05_local_first_archive_workflow.zig` and `scripts\\zigux/check_lane05_local_archive_readme.zig` are the shipped reminder guards for that local-first archive path.",
    "- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.877+a3ae499dc (1).tar.xz` in this directory",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_docs_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_docs_readme_markers_path);
    const text_docs_readme_markers = try guard.readUtf8File(io, allocator, text_docs_readme_markers_path);
    defer allocator.free(text_docs_readme_markers);
    for (DOCS_README_MARKERS) |marker| try guard.requireMarker(text_docs_readme_markers, marker);
    const text_phase2_notes_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer allocator.free(text_phase2_notes_markers_path);
    const text_phase2_notes_markers = try guard.readUtf8File(io, allocator, text_phase2_notes_markers_path);
    defer allocator.free(text_phase2_notes_markers);
    for (PHASE2_NOTES_MARKERS) |marker| try guard.requireMarker(text_phase2_notes_markers, marker);
    const text_phase2_notes_forbidden_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_phase2_notes_forbidden_markers_path);
    const text_phase2_notes_forbidden_markers = try guard.readUtf8File(io, allocator, text_phase2_notes_forbidden_markers_path);
    defer allocator.free(text_phase2_notes_forbidden_markers);
    for (PHASE2_NOTES_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text_phase2_notes_forbidden_markers, marker);
    const text_phase2_notes_exact_count_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_phase2_notes_exact_count_markers_path);
    const text_phase2_notes_exact_count_markers = try guard.readUtf8File(io, allocator, text_phase2_notes_exact_count_markers_path);
    defer allocator.free(text_phase2_notes_exact_count_markers);
    for (PHASE2_NOTES_EXACT_COUNT_MARKERS) |marker| try guard.requireMarker(text_phase2_notes_exact_count_markers, marker);
    const text_review_checklist_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist.md");
    defer allocator.free(text_review_checklist_markers_path);
    const text_review_checklist_markers = try guard.readUtf8File(io, allocator, text_review_checklist_markers_path);
    defer allocator.free(text_review_checklist_markers);
    for (REVIEW_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text_review_checklist_markers, marker);
    const text_review_checklist_forbidden_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_review_checklist_forbidden_markers_path);
    const text_review_checklist_forbidden_markers = try guard.readUtf8File(io, allocator, text_review_checklist_forbidden_markers_path);
    defer allocator.free(text_review_checklist_forbidden_markers);
    for (REVIEW_CHECKLIST_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text_review_checklist_forbidden_markers, marker);
    const text_review_checklist_exact_count_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_review_checklist_exact_count_markers_path);
    const text_review_checklist_exact_count_markers = try guard.readUtf8File(io, allocator, text_review_checklist_exact_count_markers_path);
    defer allocator.free(text_review_checklist_exact_count_markers);
    for (REVIEW_CHECKLIST_EXACT_COUNT_MARKERS) |marker| try guard.requireMarker(text_review_checklist_exact_count_markers, marker);
    const text_scripts_readme_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_scripts_readme_markers_path);
    const text_scripts_readme_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_markers_path);
    defer allocator.free(text_scripts_readme_markers);
    for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_markers, marker);
    const text_scripts_readme_forbidden_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_scripts_readme_forbidden_markers_path);
    const text_scripts_readme_forbidden_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_forbidden_markers_path);
    defer allocator.free(text_scripts_readme_forbidden_markers);
    for (SCRIPTS_README_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_forbidden_markers, marker);
    const text_tests_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_tests_readme_markers_path);
    const text_tests_readme_markers = try guard.readUtf8File(io, allocator, text_tests_readme_markers_path);
    defer allocator.free(text_tests_readme_markers);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text_tests_readme_markers, marker);
    const text_tests_readme_exact_count_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_tests_readme_exact_count_markers_path);
    const text_tests_readme_exact_count_markers = try guard.readUtf8File(io, allocator, text_tests_readme_exact_count_markers_path);
    defer allocator.free(text_tests_readme_exact_count_markers);
    for (TESTS_README_EXACT_COUNT_MARKERS) |marker| try guard.requireMarker(text_tests_readme_exact_count_markers, marker);
    const text_third_party_readme_markers_path = try guard.joinPath(allocator, root, "third_party/README.md");
    defer allocator.free(text_third_party_readme_markers_path);
    const text_third_party_readme_markers = try guard.readUtf8File(io, allocator, text_third_party_readme_markers_path);
    defer allocator.free(text_third_party_readme_markers);
    for (THIRD_PARTY_README_MARKERS) |marker| try guard.requireMarker(text_third_party_readme_markers, marker);
    const text_third_party_readme_exact_count_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_third_party_readme_exact_count_markers_path);
    const text_third_party_readme_exact_count_markers = try guard.readUtf8File(io, allocator, text_third_party_readme_exact_count_markers_path);
    defer allocator.free(text_third_party_readme_exact_count_markers);
    for (THIRD_PARTY_README_EXACT_COUNT_MARKERS) |marker| try guard.requireMarker(text_third_party_readme_exact_count_markers, marker);
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

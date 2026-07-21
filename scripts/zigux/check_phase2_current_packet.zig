const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_CURRENT_PACKET=pass";
pub const self_test_pass_marker = "PHASE2_CURRENT_PACKET_SELF_TEST=pass";

const WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_zig_toolchain.zig -- --self-test",
    "run: zig run scripts\\zigux/check_zig_toolchain.zig -- --policy-only",
    "run: zig run scripts\\zigux/check_zig_toolchain.zig -- --archive-only --allow-missing",
    "run: zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig -- --self-test",
    "run: zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig",
    "run: zig run scripts\\zigux/check_lane05_local_archive_readme.zig -- --self-test",
    "run: zig run scripts\\zigux/check_lane05_local_archive_readme.zig",
    "run: zig run scripts\\zigux/check_lane05_install_zig_archive_verification.zig -- --self-test",
    "run: zig run scripts\\zigux/check_lane05_install_zig_archive_verification.zig",
    "run: zig run scripts/zigux/install_zig.zig -- --self-test",
    "run: zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_contract.zig -- --self-test",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_contract.zig",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_selftest.zig -- --self-test",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_selftest.zig",
    "run: zig run scripts\\zigux/check_phase2_fixdep_gate.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_fixdep_gate.zig",
    "run: zig run scripts\\zigux/check_fixdep_diff.zig -- --self-test",
    "run: zig run scripts\\zigux/check_fixdep_diff.zig",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: zig run scripts\\zigux/check_kconfig_bridge.zig -- --self-test",
    "run: zig run scripts\\zigux/check_kconfig_bridge.zig",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: zig run scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig",
    "run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig",
    "run: zig run scripts\\zigux/check_phase2_tests_readme_alignment.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_tests_readme_alignment.zig",
    "run: zig run scripts\\zigux/check_phase2_cross.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_cross.zig",
    "run: zig run scripts\\zigux/check_phase2_cross_selftest_alignment.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_cross_selftest_alignment.zig",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pinning.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pinning.zig",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-fixdep",
    "run: zig run scripts\\zigux/check_phase2_required_make_routes.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_required_make_routes.zig",
    "run: zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig",
    "run: zig run scripts\\zigux/check_phase2_tool_manifest.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_tool_manifest.zig",
    "run: zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig",
    "run: zig run scripts\\zigux/check_genksyms_bridge.zig -- --self-test",
    "run: zig run scripts\\zigux/check_genksyms_bridge.zig",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: zig run scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
    "run: zig run scripts\\zigux/validate_phase2.zig",
};

const PHASE2_NOTES_MARKERS = [_][]const u8{
    "# Phase 2 Toolchain Bootstrap Notes",
    "`scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "`scripts\\zigux/check_lane05_install_zig_archive_verification.zig`",
    "`scripts/zigux/stage_pinned_zig_archive.zig`",
    "`scripts\\zigux/check_lane05_stage_helper_contract.zig`",
    "`scripts\\zigux/check_lane05_stage_helper_selftest.zig`",
    "`scripts/zigux/install_zig.zig`, `scripts\\zigux/check_lane05_install_zig_archive_verification.zig`, `scripts/zigux/stage_pinned_zig_archive.zig`, `scripts\\zigux/check_lane05_stage_helper_contract.zig`, and `scripts\\zigux/check_lane05_stage_helper_selftest.zig` are directly readable on current `master` and keep the pinned-channel archive download, staged repo-local archive materialization, archive-verification, helper-contract, helper-selftest, and install-root replay path explicit beside the reminder guards.",
    "`.github/workflows/zigux-bootstrap.yml` now runs `zig run scripts\\zigux/check_zig_toolchain.zig -- --self-test`, `zig run scripts\\zigux/check_zig_toolchain.zig -- --policy-only`, `zig run scripts\\zigux/check_zig_toolchain.zig -- --archive-only --allow-missing`, `zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig -- --self-test`, `zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig`, `zig run scripts\\zigux/check_lane05_local_archive_readme.zig -- --self-test`, `zig run scripts\\zigux/check_lane05_local_archive_readme.zig`, `zig run scripts\\zigux/check_lane05_install_zig_archive_verification.zig -- --self-test`, `zig run scripts\\zigux/check_lane05_install_zig_archive_verification.zig`, `zig run scripts/zigux/install_zig.zig -- --self-test`, `zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test`, `zig run scripts\\zigux/check_lane05_stage_helper_contract.zig -- --self-test`, `zig run scripts\\zigux/check_lane05_stage_helper_contract.zig`, `zig run scripts\\zigux/check_lane05_stage_helper_selftest.zig -- --self-test`, `zig run scripts\\zigux/check_lane05_stage_helper_selftest.zig`",
    "`scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`, `scripts\\zigux/check_phase2_artifact_tools_manifest.zig`, `scripts/zigux/artifact_diff.zig`, `scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig`, `scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the `zigux/tests/fixtures/kconfig_bridge/` plus restored `zigux/tests/fixtures/genksyms_bridge/` manifest and process-output roster keep the bounded closure-side, closure-validator, validator-entrypoint, bootstrap workflow-route, tests-facing, tool-manifest, fixture-backed artifact-support, primary artifact-diff helper, genksyms, fixdep, and bridge packet reviewable without widening back into older validator-first claims.",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit through the pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane",
    "`scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig`, `scripts\\zigux/check_genksyms_bridge.zig`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
};

const PHASE2_NOTES_FORBIDDEN_MARKERS = [_][]const u8{
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install_zig.zig`",
    "historical packet members until same-lane work rematerializes them on `master`",
};

const REVIEW_CHECKLIST_MARKERS = [_][]const u8{
    "* if the change touches the shared Phase 2 toolchain packet",
    "`scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig -- --policy-only`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig -- --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux`",
    "`scripts/zigux/install_zig.zig`",
    "`zig run scripts/zigux/install_zig.zig -- --self-test`",
    "`scripts\\zigux/check_phase2_cross.zig`",
    "`zig run scripts\\zigux/check_phase2_cross.zig -- --self-test`",
    "`zig run scripts\\zigux/check_phase2_cross.zig`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, local-first archive workflow, archive-verification and staged-archive helper packet, kbuild routes checker, helper-local kconfig allconfig guard, dedicated genksyms selftest-alignment guard, bounded genksyms bridge helper packet, fixdep governance and parity packet, current manifest guards, and shipped make-wrapper routes instead of leaving the returned repo-tooling tranche implicit on current `master`",
    "`scripts\\zigux/check_lane05_local_first_archive_workflow.zig`",
    "`scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "`scripts\\zigux/check_lane05_stage_helper_contract.zig`",
    "`scripts\\zigux/check_lane05_stage_helper_selftest.zig`",
    "`scripts\\zigux/check_phase2_cross.zig`",
    "`scripts\\zigux/check_phase2_cross_selftest_alignment.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts\\zigux/check_phase2_fixdep_gate.zig`",
    "`scripts\\zigux/check_fixdep_diff.zig`",
    "`third_party/README.md`, `scripts/zigux/stage_pinned_zig_archive.zig`, `zig run scripts/zigux/stage_pinned_zig_archive.zig -- --self-test`, `scripts\\zigux/check_lane05_stage_helper_contract.zig`, and `scripts\\zigux/check_lane05_stage_helper_selftest.zig` keep the staged repo-local archive helper, contract, and self-test packet explicit from the scripts root beside that same shipped Lane 05 local-first archive path",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`, `scripts\\zigux/check_phase2_required_make_routes.zig`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` keep the shipped scripts-root reminder, required make-route guard, and wrapper packet explicit from the current Phase 2 toolchain tranche",
    "`scripts\\zigux/check_phase2_tool_manifest.zig` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig -- --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig -- --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
};

const TESTS_README_MARKERS = [_][]const u8{
    "## Phase 2 review packet",
    "Keep the current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "Keep the current toolchain self-check and replay surface explicit through `zig run scripts\\zigux/check_zig_toolchain.zig -- --self-test`, `zig run scripts\\zigux/check_zig_toolchain.zig -- --policy-only`, `zig run scripts\\zigux/check_zig_toolchain.zig -- --archive-only --allow-missing`, `zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig -- --self-test`, `zig run scripts/zigux/install_zig.zig -- --self-test`, and `zig run scripts\\zigux/check_phase2_cross.zig -- --self-test`.",
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts\\zigux/check_lane05_local_first_archive_workflow.zig`, and `scripts\\zigux/check_lane05_local_archive_readme.zig`",
    "current `master` now directly materializes `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig -- --self-test`, `scripts\\zigux/check_phase2_cross.zig`, `zig run scripts\\zigux/check_phase2_cross.zig -- --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "current `master` also directly materializes `scripts\\zigux/check_genksyms_bridge.zig`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet",
    "current `master` also directly materializes `scripts\\zigux/check_phase2_fixdep_gate.zig`, `scripts\\zigux/check_fixdep_diff.zig`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, kconfig bridge, genksyms bridge, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
    "Tests-root reviewer prompt:",
};

const EXPECTED_MANIFEST_NOTES = [_][]const u8{
    "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, the returned local-first archive workflow and archive README contract checkers, the shipped toolchain-pinning and pin-scope guards, the returned installer helper, direct cross-route checker, docs-shared-reminder checker, required make-route guard, bootstrap workflow-routes checker, kbuild routes checker, the live kconfig bridge checker and fixture roster, the helper-local kconfig allconfig guard, the dedicated genksyms selftest-alignment guard, the manifest-backed genksyms bridge checker plus its expanded expected and process-output fixture packet, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the fixdep governance and parity checker pair, and the restored tranche-closure note.",
    "Keep the directly readable validator pair explicit through scripts\\zigux/validate_phase2.zig and scripts\\zigux/validate_phase2_closure.zig instead of leaving the closure-side replay packet implied only in prose.",
    "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
    "Keep the dedicated manifest guards, the bootstrap workflow-routes guard, the primary artifact_diff helper, the helper-local kconfig allconfig guard, and the dedicated genksyms selftest-alignment guard explicit through scripts\\zigux/check_phase2_tool_manifest.zig, scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig, scripts\\zigux/check_phase2_artifact_tools_manifest.zig, scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig, scripts/zigux/artifact_diff.zig, and scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig so Phase 2 packet drift fails closed beside the other reminder checkers.",
    "Keep the returned install-zig archive verification checker, staged pinned-archive helper, and the stage-helper contract plus selftest packet explicit beside the local-first archive workflow, archive README contract, and installer helper so the shared Phase 2 tool packet matches the live phase2-toolchain and validate-phase2 routes.",
    "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, the bootstrap workflow-routes guard, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
    "Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface for the same current Phase 2 toolchain, kbuild, installer, cross-route, bootstrap workflow-route, and make-wrapper packet that the docs-root, tests-root, and checklist surfaces summarize.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_lines_path);
    const text_workflow_lines = try guard.readUtf8File(io, allocator, text_workflow_lines_path);
    defer allocator.free(text_workflow_lines);
    for (WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_workflow_lines, marker, 1);
    const text_phase2_notes_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer allocator.free(text_phase2_notes_markers_path);
    const text_phase2_notes_markers = try guard.readUtf8File(io, allocator, text_phase2_notes_markers_path);
    defer allocator.free(text_phase2_notes_markers);
    for (PHASE2_NOTES_MARKERS) |marker| try guard.requireMarker(text_phase2_notes_markers, marker);
    const text_phase2_notes_forbidden_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_phase2_notes_forbidden_markers_path);
    const text_phase2_notes_forbidden_markers = try guard.readUtf8File(io, allocator, text_phase2_notes_forbidden_markers_path);
    defer allocator.free(text_phase2_notes_forbidden_markers);
    for (PHASE2_NOTES_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text_phase2_notes_forbidden_markers, marker);
    const text_review_checklist_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist.md");
    defer allocator.free(text_review_checklist_markers_path);
    const text_review_checklist_markers = try guard.readUtf8File(io, allocator, text_review_checklist_markers_path);
    defer allocator.free(text_review_checklist_markers);
    for (REVIEW_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text_review_checklist_markers, marker);
    const text_scripts_readme_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_scripts_readme_markers_path);
    const text_scripts_readme_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_markers_path);
    defer allocator.free(text_scripts_readme_markers);
    for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_markers, marker);
    const text_tests_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_tests_readme_markers_path);
    const text_tests_readme_markers = try guard.readUtf8File(io, allocator, text_tests_readme_markers_path);
    defer allocator.free(text_tests_readme_markers);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text_tests_readme_markers, marker);
    const text_expected_manifest_notes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_manifest_notes_path);
    const text_expected_manifest_notes = try guard.readUtf8File(io, allocator, text_expected_manifest_notes_path);
    defer allocator.free(text_expected_manifest_notes);
    for (EXPECTED_MANIFEST_NOTES) |marker| try guard.requireMarker(text_expected_manifest_notes, marker);
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

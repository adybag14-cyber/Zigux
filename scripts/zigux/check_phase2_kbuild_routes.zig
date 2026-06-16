const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_KBUILD_ROUTES=pass";
pub const self_test_pass_marker = "PHASE2_KBUILD_ROUTES_SELF_TEST=pass";

const WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --self-test",
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --policy-only",
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing",
    "run: zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig",
    "run: zig run scripts\\zigux/check_lane05_local_archive_readme.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_local_archive_readme.zig",
    "run: zig run scripts\\zigux/check_lane05_install_zig_archive_verification.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_install_zig_archive_verification.zig",
    "run: zig run scripts/zigux/install_zig.zig --self-test",
    "run: zig run scripts/zigux/stage_pinned_zig_archive.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_contract.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_contract.zig",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_selftest.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_selftest.zig",
    "run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig",
    "run: zig run scripts\\zigux/check_phase2_cross.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_cross.zig",
    "run: zig run scripts\\zigux/check_phase2_cross_selftest_alignment.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_cross_selftest_alignment.zig",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pinning.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pinning.zig",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
    "run: zig run scripts\\zigux/validate_phase2.zig",
};

const README_MARKERS = [_][]const u8{
    "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts\\zigux/check_zig_toolchain.zig`, `scripts\\zigux/check_phase2_kbuild_routes.zig`, `scripts\\zigux/check_phase2_docs_shared_reminder.zig`, `scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`third_party/README.md`, `scripts/zigux/stage_pinned_zig_archive.zig`, `zig run scripts/zigux/stage_pinned_zig_archive.zig --self-test`, `scripts\\zigux/check_lane05_stage_helper_contract.zig`, and `scripts\\zigux/check_lane05_stage_helper_selftest.zig`",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`, `scripts\\zigux/check_phase2_required_make_routes.zig`, `scripts\\zigux/validate_phase2_closure.zig`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/install_zig.zig`, `zig run scripts/zigux/install_zig.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig --self-test`, `zig run scripts\\zigux/check_phase2_cross.zig`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
};

const README_FORBIDDEN_MARKERS = [_][]const u8{
    "still return missing for `scripts/zigux/install_zig.zig`",
    "still return missing for `scripts\\zigux/validate_phase2_closure.zig`",
    "need fresh re-materialization before they are reused here as direct current-`master` scripts-root evidence",
};

const MAKEFILE_LINES = [_][]const u8{
    "phase2-toolchain:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig --policy-only",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig --archive-only --allow-missing",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_local_first_archive_workflow.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_local_first_archive_workflow.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_local_archive_readme.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_local_archive_readme.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_install_zig_archive_verification.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_install_zig_archive_verification.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install_zig.zig --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage_pinned_zig_archive.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_stage_helper_contract.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_stage_helper_contract.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_stage_helper_selftest.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_lane05_stage_helper_selftest.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig",
    "phase2-tools:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kbuild_routes.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kbuild_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_docs_shared_reminder.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_docs_shared_reminder.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_required_make_routes.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_required_make_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_artifact_tools_manifest.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_artifact_tools_manifest.zig",
    "phase2-kconfig: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_kconfig_bridge.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_kconfig_bridge.zig --zig \"$(ZIG_REPO_ROOT)\"",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_selftest_alignment.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_selftest_alignment.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_allconfig_helper_packet.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_allconfig_helper_packet.zig",
    "phase2-cross:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig",
    "phase2-genksyms: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_genksyms_selftest_alignment.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_genksyms_selftest_alignment.zig",
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig --zig \"$(ZIG_REPO_ROOT)\"",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tests_readme_alignment.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tests_readme_alignment.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tool_manifest.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tool_manifest.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/validate_phase2_closure.zig",
    "phase2: phase2-validate",
};

const FORBIDDEN_MAKEFILE_LINES = [_][]const u8{
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/genksyms.zig",
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/fixdep.zig",
};

const SURFACE_PATHS = [_][]const u8{
    "PathDocumentation/zigux/phase2-closure.md",
    "Pathscripts/zigux/artifact_diff.zig",
    "Pathscripts\\zigux/check_fixdep_diff.zig",
    "Pathscripts\\zigux/check_genksyms_bridge.zig",
    "Pathscripts\\zigux/check_kconfig_bridge.zig",
    "Pathscripts\\zigux/check_lane05_install_zig_archive_verification.zig",
    "Pathscripts\\zigux/check_lane05_local_archive_readme.zig",
    "Pathscripts\\zigux/check_lane05_local_first_archive_workflow.zig",
    "Pathscripts\\zigux/check_lane05_stage_helper_contract.zig",
    "Pathscripts\\zigux/check_lane05_stage_helper_selftest.zig",
    "Pathscripts\\zigux/check_phase2_artifact_tools_manifest.zig",
    "Pathscripts\\zigux/check_phase2_bootstrap_workflow_routes.zig",
    "Pathscripts\\zigux/check_phase2_cross_selftest_alignment.zig",
    "Pathscripts\\zigux/check_phase2_cross.zig",
    "Pathscripts\\zigux/check_phase2_docs_shared_reminder.zig",
    "Pathscripts\\zigux/check_phase2_fixdep_gate.zig",
    "Pathscripts\\zigux/check_phase2_genksyms_selftest_alignment.zig",
    "Pathscripts\\zigux/check_phase2_kbuild_routes.zig",
    "Pathscripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    "Pathscripts\\zigux/check_phase2_kconfig_selftest_alignment.zig",
    "Pathscripts\\zigux/check_phase2_required_make_routes.zig",
    "Pathscripts\\zigux/check_phase2_tests_readme_alignment.zig",
    "Pathscripts\\zigux/check_phase2_tool_manifest.zig",
    "Pathscripts\\zigux/check_phase2_toolchain_pin_scope.zig",
    "Pathscripts\\zigux/check_phase2_toolchain_pinning.zig",
    "Pathscripts\\zigux/check_zig_toolchain.zig",
    "Pathscripts/zigux/fixdep.zig",
    "Pathscripts/zigux/genksyms.zig",
    "Pathscripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "Pathscripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "Pathscripts/zigux/install_zig.zig",
    "Pathscripts/zigux/kconfig/conf_bridge.zig",
    "Pathscripts/zigux/kconfig/confdata_bridge.zig",
    "Pathscripts/zigux/stage_pinned_zig_archive.zig",
    "Pathscripts\\zigux/validate_phase2_closure.zig",
    "Pathscripts\\zigux/validate_phase2.zig",
    "Pathscripts/zigux/zig-toolchain-policy.json",
    "Paththird_party/README.md",
    "Pathzigux/tests/fixtures/fixdep/cases.json",
    "Pathzigux/tests/fixtures/genksyms_bridge/cases.json",
    "Pathzigux/tests/fixtures/genksyms_bridge/manifest.json",
    "Pathzigux/tests/fixtures/kconfig_bridge/cases.json",
    "Pathzigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "Pathzigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "Pathzigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "Pathzigux/tests/fixtures/phase2_cross_targets.json",
    "Pathzigux/tests/fixtures/phase2_tool_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_lines_path);
    const text_workflow_lines = try guard.readUtf8File(io, allocator, text_workflow_lines_path);
    defer allocator.free(text_workflow_lines);
    for (WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_workflow_lines, marker, 1);
    const text_readme_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_readme_markers_path);
    const text_readme_markers = try guard.readUtf8File(io, allocator, text_readme_markers_path);
    defer allocator.free(text_readme_markers);
    for (README_MARKERS) |marker| try guard.requireMarker(text_readme_markers, marker);
    const text_readme_forbidden_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_readme_forbidden_markers_path);
    const text_readme_forbidden_markers = try guard.readUtf8File(io, allocator, text_readme_forbidden_markers_path);
    defer allocator.free(text_readme_forbidden_markers);
    for (README_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text_readme_forbidden_markers, marker);
    const text_makefile_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_lines_path);
    const text_makefile_lines = try guard.readUtf8File(io, allocator, text_makefile_lines_path);
    defer allocator.free(text_makefile_lines);
    for (MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_makefile_lines, marker, 1);
    const text_forbidden_makefile_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_forbidden_makefile_lines_path);
    const text_forbidden_makefile_lines = try guard.readUtf8File(io, allocator, text_forbidden_makefile_lines_path);
    defer allocator.free(text_forbidden_makefile_lines);
    for (FORBIDDEN_MAKEFILE_LINES) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_makefile_lines, marker) != null) return guard.GuardError.MissingMarker;
    }
    for (SURFACE_PATHS) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) return guard.GuardError.IOError;
    }
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

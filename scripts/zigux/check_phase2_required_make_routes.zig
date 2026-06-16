const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_REQUIRED_MAKE_ROUTES=pass";
pub const self_test_pass_marker = "PHASE2_REQUIRED_MAKE_ROUTES_SELF_TEST=pass";

const WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_phase2_required_make_routes.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_required_make_routes.zig",
};

const REQUIRED_PHASE2_PHONY_LINE = [_][]const u8{
    ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
};

const CURRENT_REQUIRED_MAKE_ROUTES = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

const POLICY_SUMMARY_ANCHOR = [_][]const u8{
    "required Linux-style make routes",
};

const TOOLCHAIN_ROUTE = [_][]const u8{
    "phase2-toolchain",
};

const TOOLCHAIN_ALLOWED_RECIPE_LINES = [_][]const u8{
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
};

const TOOLCHAIN_OVERLAP_FRAGMENTS = [_][]const u8{
    "check_phase2_kbuild_routes.zig",
    "check-phase2-docs-shared-reminder.py",
    "check-phase2-required-make-routes.py",
    "check-phase2-artifact-tools-manifest.py",
    "check-kconfig-bridge.py",
    "check-phase2-kconfig-selftest-alignment.py",
    "check-phase2-kconfig-allconfig-helper-packet.py",
    "check-phase2-cross.py",
    "check-phase2-cross-selftest-alignment.py",
    "check-genksyms-bridge.py",
    "check-phase2-genksyms-selftest-alignment.py",
    "genksyms.zig",
    "check-phase2-fixdep-gate.py",
    "check-fixdep-diff.py",
    "fixdep.zig",
    "make -C zigux phase2-",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase2-toolchain:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig --policy-only",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig --archive-only --allow-missing",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig",
    "phase2-tools:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kbuild_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_docs_shared_reminder.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_required_make_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_artifact_tools_manifest.zig",
    "phase2-kconfig: phase2-toolchain",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_selftest_alignment.zig",
    "phase2-cross:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig",
    "phase2-genksyms: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig",
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig --zig \"$(ZIG_REPO_ROOT)\"",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tests_readme_alignment.zig",
    "phase2: phase2-validate",
};

const CURRENT_PACKET_ROUTE_MARKERS = [_][]const u8{
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
};

const MINIMAL_SURFACE_MARKERS = [_][]const u8{
    "`zigux/Makefile`",
};

const FULL_ROUTE_SURFACE_CODES = [_][]const u8{
    "MISSING_DOCS_README_MARKERSMISSING_DOCS_README_ROUTE_MARKERS",
    "MISSING_BOOTSTRAP_GAP_MARKERSMISSING_BOOTSTRAP_ROUTE_MARKERS",
    "MISSING_REVIEW_GAP_MARKERSMISSING_REVIEW_ROUTE_MARKERS",
    "MISSING_SCRIPTS_README_GAP_MARKERSMISSING_SCRIPTS_README_ROUTE_MARKERS",
};

const POLICY_ROUTE_SURFACE_CODES = [_][]const u8{
    "MISSING_TESTS_GAP_MARKERSMISSING_TESTS_ROUTE_MARKERS",
};

const POLICY_SUMMARY_SURFACE_CODES = [_][]const u8{
    "MISSING_BOOTSTRAP_POLICY_ROUTE_SUMMARYMISSING_BOOTSTRAP_POLICY_ROUTE_NAME",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_lines_path);
    const text_workflow_lines = try guard.readUtf8File(io, allocator, text_workflow_lines_path);
    defer allocator.free(text_workflow_lines);
    for (WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_workflow_lines, marker, 1);
    const text_required_phase2_phony_line_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_phase2_phony_line_path);
    const text_required_phase2_phony_line = try guard.readUtf8File(io, allocator, text_required_phase2_phony_line_path);
    defer allocator.free(text_required_phase2_phony_line);
    for (REQUIRED_PHASE2_PHONY_LINE) |marker| try guard.requireMarker(text_required_phase2_phony_line, marker);
    const text_current_required_make_routes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_current_required_make_routes_path);
    const text_current_required_make_routes = try guard.readUtf8File(io, allocator, text_current_required_make_routes_path);
    defer allocator.free(text_current_required_make_routes);
    for (CURRENT_REQUIRED_MAKE_ROUTES) |marker| try guard.requireMarker(text_current_required_make_routes, marker);
    const text_policy_summary_anchor_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_policy_summary_anchor_path);
    const text_policy_summary_anchor = try guard.readUtf8File(io, allocator, text_policy_summary_anchor_path);
    defer allocator.free(text_policy_summary_anchor);
    for (POLICY_SUMMARY_ANCHOR) |marker| try guard.requireMarker(text_policy_summary_anchor, marker);
    const text_toolchain_route_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_toolchain_route_path);
    const text_toolchain_route = try guard.readUtf8File(io, allocator, text_toolchain_route_path);
    defer allocator.free(text_toolchain_route);
    for (TOOLCHAIN_ROUTE) |marker| try guard.requireMarker(text_toolchain_route, marker);
    const text_toolchain_allowed_recipe_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_toolchain_allowed_recipe_lines_path);
    const text_toolchain_allowed_recipe_lines = try guard.readUtf8File(io, allocator, text_toolchain_allowed_recipe_lines_path);
    defer allocator.free(text_toolchain_allowed_recipe_lines);
    for (TOOLCHAIN_ALLOWED_RECIPE_LINES) |marker| try guard.requireExactLineCount(text_toolchain_allowed_recipe_lines, marker, 1);
    const text_toolchain_overlap_fragments_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_toolchain_overlap_fragments_path);
    const text_toolchain_overlap_fragments = try guard.readUtf8File(io, allocator, text_toolchain_overlap_fragments_path);
    defer allocator.free(text_toolchain_overlap_fragments);
    for (TOOLCHAIN_OVERLAP_FRAGMENTS) |marker| try guard.requireMarker(text_toolchain_overlap_fragments, marker);
    const text_makefile_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_markers_path);
    const text_makefile_markers = try guard.readUtf8File(io, allocator, text_makefile_markers_path);
    defer allocator.free(text_makefile_markers);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text_makefile_markers, marker);
    const text_current_packet_route_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_current_packet_route_markers_path);
    const text_current_packet_route_markers = try guard.readUtf8File(io, allocator, text_current_packet_route_markers_path);
    defer allocator.free(text_current_packet_route_markers);
    for (CURRENT_PACKET_ROUTE_MARKERS) |marker| try guard.requireMarker(text_current_packet_route_markers, marker);
    const text_minimal_surface_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_minimal_surface_markers_path);
    const text_minimal_surface_markers = try guard.readUtf8File(io, allocator, text_minimal_surface_markers_path);
    defer allocator.free(text_minimal_surface_markers);
    for (MINIMAL_SURFACE_MARKERS) |marker| try guard.requireMarker(text_minimal_surface_markers, marker);
    const text_full_route_surface_codes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_full_route_surface_codes_path);
    const text_full_route_surface_codes = try guard.readUtf8File(io, allocator, text_full_route_surface_codes_path);
    defer allocator.free(text_full_route_surface_codes);
    for (FULL_ROUTE_SURFACE_CODES) |marker| try guard.requireMarker(text_full_route_surface_codes, marker);
    const text_policy_route_surface_codes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_policy_route_surface_codes_path);
    const text_policy_route_surface_codes = try guard.readUtf8File(io, allocator, text_policy_route_surface_codes_path);
    defer allocator.free(text_policy_route_surface_codes);
    for (POLICY_ROUTE_SURFACE_CODES) |marker| try guard.requireMarker(text_policy_route_surface_codes, marker);
    const text_policy_summary_surface_codes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_policy_summary_surface_codes_path);
    const text_policy_summary_surface_codes = try guard.readUtf8File(io, allocator, text_policy_summary_surface_codes_path);
    defer allocator.free(text_policy_summary_surface_codes);
    for (POLICY_SUMMARY_SURFACE_CODES) |marker| try guard.requireMarker(text_policy_summary_surface_codes, marker);
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

const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_KCONFIG_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass";

const WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_kconfig_bridge.zig --self-test",
    "run: zig run scripts\\zigux/check_kconfig_bridge.zig",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: zig run scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig",
    "run: make -C zigux phase2-kconfig",
};

const WORKFLOW_PATH_LINES = [_][]const u8{
    "- 'scripts/kconfig/conf.c'",
    "- 'scripts/kconfig/confdata.c'",
};

const MAKEFILE_LINES = [_][]const u8{
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_kconfig_bridge.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_kconfig_bridge.zig --zig \"$(ZIG_REPO_ROOT)\"",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_selftest_alignment.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_selftest_alignment.zig",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "the manifest-backed kconfig fixture roster",
};

const TESTS_README_MARKERS = [_][]const u8{
    "scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "make -C zigux phase2-kconfig",
};

const REVIEW_CHECKLIST_MARKERS = [_][]const u8{
    "scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "make -C zigux phase2-kconfig",
};

const BRIDGE_CHECKER_LINE_MARKERS = [_][]const u8{
    "if group_name == \"conf_cases\" and \"silent\" in case and not isinstance(case[\"silent\"], bool):",
    "if \"silent\" in case and case[\"silent\"] is not True:",
    "if case.get(\"silent\"):",
    "if \"mode_arg\" in case:",
    "if \"allconfig\" in case:",
    "if \"seed\" in case:",
    "if \"probability\" in case:",
    "if \"nosilentupdate\" in case:",
    "cmd.append(\"silent\")",
    "cmd.append(str(case[\"mode_arg\"]))",
    "cmd.append(f\"allconfig={case['allconfig']}\")",
    "cmd.append(f\"seed={case['seed']}\")",
    "cmd.append(f\"probability={case['probability']}\")",
    "cmd.append(f\"nosilentupdate={case['nosilentupdate']}\")",
};

const CONF_HELPER_ANCHOR_CONST = [_][]const u8{
    "REQUIRED_CONF_HELPER_ANCHORS",
};

const CONFDATA_HELPER_ANCHOR_CONST = [_][]const u8{
    "REQUIRED_CONFDATA_HELPER_ANCHORS",
};

const CONF_HELPER_IMPLICIT_OMISSION_MODES_CONST = [_][]const u8{
    "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES",
};

const CONF_HELPER_EXPLICIT_OVERRIDE_MODES_CONST = [_][]const u8{
    "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES",
};

const CONFDATA_CASE_PACKET_CONST = [_][]const u8{
    "SAMPLE_CONFDATA_CASES",
};

const SURFACE_PATHS = [_][]const u8{
    "ROOT/scripts/zigux/kconfig/conf_bridge.zig",
    "ROOT/scripts/zigux/kconfig/confdata_bridge.zig",
    "KCONFIG_BRIDGE_CHECKER",
    "KCONFIG_BRIDGE_CASES",
    "CONF_MANIFEST",
    "CONFDATA_MANIFEST",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_lines_path);
    const text_workflow_lines = try guard.readUtf8File(io, allocator, text_workflow_lines_path);
    defer allocator.free(text_workflow_lines);
    for (WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_workflow_lines, marker, 1);
    const text_workflow_path_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_path_lines_path);
    const text_workflow_path_lines = try guard.readUtf8File(io, allocator, text_workflow_path_lines_path);
    defer allocator.free(text_workflow_path_lines);
    for (WORKFLOW_PATH_LINES) |marker| try guard.requireExactLineCount(text_workflow_path_lines, marker, 1);
    const text_makefile_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_lines_path);
    const text_makefile_lines = try guard.readUtf8File(io, allocator, text_makefile_lines_path);
    defer allocator.free(text_makefile_lines);
    for (MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_makefile_lines, marker, 1);
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
    const text_review_checklist_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist.md");
    defer allocator.free(text_review_checklist_markers_path);
    const text_review_checklist_markers = try guard.readUtf8File(io, allocator, text_review_checklist_markers_path);
    defer allocator.free(text_review_checklist_markers);
    for (REVIEW_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text_review_checklist_markers, marker);
    const text_bridge_checker_line_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bridge_checker_line_markers_path);
    const text_bridge_checker_line_markers = try guard.readUtf8File(io, allocator, text_bridge_checker_line_markers_path);
    defer allocator.free(text_bridge_checker_line_markers);
    for (BRIDGE_CHECKER_LINE_MARKERS) |marker| try guard.requireMarker(text_bridge_checker_line_markers, marker);
    const text_conf_helper_anchor_const_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_conf_helper_anchor_const_path);
    const text_conf_helper_anchor_const = try guard.readUtf8File(io, allocator, text_conf_helper_anchor_const_path);
    defer allocator.free(text_conf_helper_anchor_const);
    for (CONF_HELPER_ANCHOR_CONST) |marker| try guard.requireMarker(text_conf_helper_anchor_const, marker);
    const text_confdata_helper_anchor_const_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_confdata_helper_anchor_const_path);
    const text_confdata_helper_anchor_const = try guard.readUtf8File(io, allocator, text_confdata_helper_anchor_const_path);
    defer allocator.free(text_confdata_helper_anchor_const);
    for (CONFDATA_HELPER_ANCHOR_CONST) |marker| try guard.requireMarker(text_confdata_helper_anchor_const, marker);
    const text_conf_helper_implicit_omission_modes_const_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_conf_helper_implicit_omission_modes_const_path);
    const text_conf_helper_implicit_omission_modes_const = try guard.readUtf8File(io, allocator, text_conf_helper_implicit_omission_modes_const_path);
    defer allocator.free(text_conf_helper_implicit_omission_modes_const);
    for (CONF_HELPER_IMPLICIT_OMISSION_MODES_CONST) |marker| try guard.requireMarker(text_conf_helper_implicit_omission_modes_const, marker);
    const text_conf_helper_explicit_override_modes_const_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_conf_helper_explicit_override_modes_const_path);
    const text_conf_helper_explicit_override_modes_const = try guard.readUtf8File(io, allocator, text_conf_helper_explicit_override_modes_const_path);
    defer allocator.free(text_conf_helper_explicit_override_modes_const);
    for (CONF_HELPER_EXPLICIT_OVERRIDE_MODES_CONST) |marker| try guard.requireMarker(text_conf_helper_explicit_override_modes_const, marker);
    const text_confdata_case_packet_const_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_confdata_case_packet_const_path);
    const text_confdata_case_packet_const = try guard.readUtf8File(io, allocator, text_confdata_case_packet_const_path);
    defer allocator.free(text_confdata_case_packet_const);
    for (CONFDATA_CASE_PACKET_CONST) |marker| try guard.requireMarker(text_confdata_case_packet_const, marker);
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

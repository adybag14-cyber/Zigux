const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET=pass";
pub const self_test_pass_marker = "PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST=pass";

const REQUIRED_HELPER_ANCHORS = [_][]const u8{
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "conf bridge emits randconfig tunables when present",
    "conf bridge emits explicit randconfig allconfig override when present",
    "conf bridge omits randconfig allconfig sentinel without explicit override",
};

const REQUIRED_BRIDGE_SOURCE_MARKERS = [_][]const u8{
    "var alldefconfig_path_capture = try TestCapture.init(std.testing.allocator, 224);",
    "try runConfBridge(&alldefconfig_path_capture, .{",
    ".allconfig = \"mini-all.config\",",
};

const REQUIRED_CLOSURE_MARKERS = [_][]const u8{
    "scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4",
};

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_allconfig_helper_packet.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_allconfig_helper_packet.zig",
};

const REQUIRED_PHASE2_VALIDATE_MARKERS = [_][]const u8{
    "\"scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig\",",
    "\"run: zig run scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig --self-test\",",
    "\"run: zig run scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig\",",
    "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_allconfig_helper_packet.zig --self-test\",",
    "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_allconfig_helper_packet.zig\",",
};

const REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS = [_][]const u8{
    "\"zig run scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig\",",
    "- `zig run scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig`",
    "\"make -C zigux phase2-kconfig\",",
    "SHARED_TOOLING_COMMANDS = (",
    "SHARED_TOOLING_REQUIRED_NOTE_MARKERS = (",
    "MANIFEST_SURFACE_KEYS = (",
};

const REQUIRED_TOOL_MANIFEST_CHECKERS = [_][]const u8{
    "scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
};

const BRIDGE_CHECKER_IMPLICIT_OMISSION_MODES_CONST = [_][]const u8{
    "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES",
};

const BRIDGE_CHECKER_EXPLICIT_OVERRIDE_MODES_CONST = [_][]const u8{
    "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES",
};

const BRIDGE_CHECKER_HELPER_ANCHORS_CONST = [_][]const u8{
    "REQUIRED_CONF_HELPER_ANCHORS",
};

const SELF_TEST_IMPLICIT_MODES = [_][]const u8{
    "allmodconfig",
    "randconfig",
};

const SELF_TEST_EXPLICIT_MODES = [_][]const u8{
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_helper_anchors_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_helper_anchors_path);
    const text_required_helper_anchors = try guard.readUtf8File(io, allocator, text_required_helper_anchors_path);
    defer allocator.free(text_required_helper_anchors);
    for (REQUIRED_HELPER_ANCHORS) |marker| try guard.requireMarker(text_required_helper_anchors, marker);
    const text_required_bridge_source_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_bridge_source_markers_path);
    const text_required_bridge_source_markers = try guard.readUtf8File(io, allocator, text_required_bridge_source_markers_path);
    defer allocator.free(text_required_bridge_source_markers);
    for (REQUIRED_BRIDGE_SOURCE_MARKERS) |marker| try guard.requireMarker(text_required_bridge_source_markers, marker);
    const text_required_closure_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_closure_markers_path);
    const text_required_closure_markers = try guard.readUtf8File(io, allocator, text_required_closure_markers_path);
    defer allocator.free(text_required_closure_markers);
    for (REQUIRED_CLOSURE_MARKERS) |marker| try guard.requireMarker(text_required_closure_markers, marker);
    const text_required_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_workflow_lines_path);
    const text_required_workflow_lines = try guard.readUtf8File(io, allocator, text_required_workflow_lines_path);
    defer allocator.free(text_required_workflow_lines);
    for (REQUIRED_WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_required_workflow_lines, marker, 1);
    const text_required_makefile_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_makefile_lines_path);
    const text_required_makefile_lines = try guard.readUtf8File(io, allocator, text_required_makefile_lines_path);
    defer allocator.free(text_required_makefile_lines);
    for (REQUIRED_MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_required_makefile_lines, marker, 1);
    const text_required_phase2_validate_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_phase2_validate_markers_path);
    const text_required_phase2_validate_markers = try guard.readUtf8File(io, allocator, text_required_phase2_validate_markers_path);
    defer allocator.free(text_required_phase2_validate_markers);
    for (REQUIRED_PHASE2_VALIDATE_MARKERS) |marker| try guard.requireMarker(text_required_phase2_validate_markers, marker);
    const text_required_phase2_closure_validate_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_phase2_closure_validate_markers_path);
    const text_required_phase2_closure_validate_markers = try guard.readUtf8File(io, allocator, text_required_phase2_closure_validate_markers_path);
    defer allocator.free(text_required_phase2_closure_validate_markers);
    for (REQUIRED_PHASE2_CLOSURE_VALIDATE_MARKERS) |marker| try guard.requireMarker(text_required_phase2_closure_validate_markers, marker);
    const text_required_tool_manifest_checkers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_tool_manifest_checkers_path);
    const text_required_tool_manifest_checkers = try guard.readUtf8File(io, allocator, text_required_tool_manifest_checkers_path);
    defer allocator.free(text_required_tool_manifest_checkers);
    for (REQUIRED_TOOL_MANIFEST_CHECKERS) |marker| try guard.requireMarker(text_required_tool_manifest_checkers, marker);
    const text_bridge_checker_implicit_omission_modes_const_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bridge_checker_implicit_omission_modes_const_path);
    const text_bridge_checker_implicit_omission_modes_const = try guard.readUtf8File(io, allocator, text_bridge_checker_implicit_omission_modes_const_path);
    defer allocator.free(text_bridge_checker_implicit_omission_modes_const);
    for (BRIDGE_CHECKER_IMPLICIT_OMISSION_MODES_CONST) |marker| try guard.requireMarker(text_bridge_checker_implicit_omission_modes_const, marker);
    const text_bridge_checker_explicit_override_modes_const_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bridge_checker_explicit_override_modes_const_path);
    const text_bridge_checker_explicit_override_modes_const = try guard.readUtf8File(io, allocator, text_bridge_checker_explicit_override_modes_const_path);
    defer allocator.free(text_bridge_checker_explicit_override_modes_const);
    for (BRIDGE_CHECKER_EXPLICIT_OVERRIDE_MODES_CONST) |marker| try guard.requireMarker(text_bridge_checker_explicit_override_modes_const, marker);
    const text_bridge_checker_helper_anchors_const_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bridge_checker_helper_anchors_const_path);
    const text_bridge_checker_helper_anchors_const = try guard.readUtf8File(io, allocator, text_bridge_checker_helper_anchors_const_path);
    defer allocator.free(text_bridge_checker_helper_anchors_const);
    for (BRIDGE_CHECKER_HELPER_ANCHORS_CONST) |marker| try guard.requireMarker(text_bridge_checker_helper_anchors_const, marker);
    const text_self_test_implicit_modes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_implicit_modes_path);
    const text_self_test_implicit_modes = try guard.readUtf8File(io, allocator, text_self_test_implicit_modes_path);
    defer allocator.free(text_self_test_implicit_modes);
    for (SELF_TEST_IMPLICIT_MODES) |marker| try guard.requireMarker(text_self_test_implicit_modes, marker);
    const text_self_test_explicit_modes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_explicit_modes_path);
    const text_self_test_explicit_modes = try guard.readUtf8File(io, allocator, text_self_test_explicit_modes_path);
    defer allocator.free(text_self_test_explicit_modes);
    for (SELF_TEST_EXPLICIT_MODES) |marker| try guard.requireMarker(text_self_test_explicit_modes, marker);
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

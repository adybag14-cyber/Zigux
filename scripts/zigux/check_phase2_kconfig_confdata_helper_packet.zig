const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_KCONFIG_CONFDATA_HELPER_PACKET=pass";
pub const self_test_pass_marker = "PHASE2_KCONFIG_CONFDATA_HELPER_PACKET_SELF_TEST=pass";

const REQUIRED_HELPER_ANCHORS = [_][]const u8{
    "confdata bridge parses bounded config states",
    "confdata bridge keeps only the last assignment for duplicate symbols",
    "confdata bridge keeps explicit empty assignments distinct from quoted empty strings",
    "confdata bridge preserves duplicate unset ownership on allocation failure",
};

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_phase2_kconfig_confdata_helper_packet.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_kconfig_confdata_helper_packet.zig",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_confdata_helper_packet.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_confdata_helper_packet.zig",
};

const REQUIRED_PHASE2_VALIDATE_MARKERS = [_][]const u8{
    "\"scripts\\zigux/check_phase2_kconfig_confdata_helper_packet.zig\",",
    "\"run: zig run scripts\\zigux/check_phase2_kconfig_confdata_helper_packet.zig -- --self-test\",",
    "\"run: zig run scripts\\zigux/check_phase2_kconfig_confdata_helper_packet.zig\",",
    "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_confdata_helper_packet.zig -- --self-test\",",
    "\"$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_confdata_helper_packet.zig\",",
};

const REQUIRED_TOOL_MANIFEST_CHECKERS = [_][]const u8{
    "scripts\\zigux/check_phase2_kconfig_confdata_helper_packet.zig",
};

const BRIDGE_CHECKER_CONFDATA_CASES_CONST = [_][]const u8{
    "SAMPLE_CONFDATA_CASES",
};

const BRIDGE_CHECKER_CONFDATA_HELPER_ANCHORS_CONST = [_][]const u8{
    "REQUIRED_CONFDATA_HELPER_ANCHORS",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_helper_anchors_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_helper_anchors_path);
    const text_required_helper_anchors = try guard.readUtf8File(io, allocator, text_required_helper_anchors_path);
    defer allocator.free(text_required_helper_anchors);
    for (REQUIRED_HELPER_ANCHORS) |marker| try guard.requireMarker(text_required_helper_anchors, marker);
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
    const text_required_tool_manifest_checkers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_tool_manifest_checkers_path);
    const text_required_tool_manifest_checkers = try guard.readUtf8File(io, allocator, text_required_tool_manifest_checkers_path);
    defer allocator.free(text_required_tool_manifest_checkers);
    for (REQUIRED_TOOL_MANIFEST_CHECKERS) |marker| try guard.requireMarker(text_required_tool_manifest_checkers, marker);
    const text_bridge_checker_confdata_cases_const_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bridge_checker_confdata_cases_const_path);
    const text_bridge_checker_confdata_cases_const = try guard.readUtf8File(io, allocator, text_bridge_checker_confdata_cases_const_path);
    defer allocator.free(text_bridge_checker_confdata_cases_const);
    for (BRIDGE_CHECKER_CONFDATA_CASES_CONST) |marker| try guard.requireMarker(text_bridge_checker_confdata_cases_const, marker);
    const text_bridge_checker_confdata_helper_anchors_const_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bridge_checker_confdata_helper_anchors_const_path);
    const text_bridge_checker_confdata_helper_anchors_const = try guard.readUtf8File(io, allocator, text_bridge_checker_confdata_helper_anchors_const_path);
    defer allocator.free(text_bridge_checker_confdata_helper_anchors_const);
    for (BRIDGE_CHECKER_CONFDATA_HELPER_ANCHORS_CONST) |marker| try guard.requireMarker(text_bridge_checker_confdata_helper_anchors_const, marker);
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

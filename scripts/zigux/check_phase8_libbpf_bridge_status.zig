const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_LIBBPF_BRIDGE_STATUS=pass";
pub const self_test_pass_marker = "PHASE8_LIBBPF_BRIDGE_STATUS_SELF_TEST=pass";

const SCRIPT_PATH = [_][]const u8{
    "scripts\\zigux/check_phase8_libbpf_bridge_status.zig",
};

const MANIFEST_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/manifest.json",
};

const SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
};

const TEST_PATH = [_][]const u8{
    "zigux/tests/phase8_libbpf_segments.zig",
};

const REQUIRED_SURVEY_MARKERS = [_][]const u8{
    "map-reuse-compatibility",
    "fdinfo-map-info-helpers",
    "file-path-and-handle-bridge",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_script_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_bridge_status.zig");
    defer allocator.free(text_script_path_path);
    const text_script_path = try guard.readUtf8File(io, allocator, text_script_path_path);
    defer allocator.free(text_script_path);
    for (SCRIPT_PATH) |marker| try guard.requireMarker(text_script_path, marker);
    const text_manifest_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_bridge_status.zig");
    defer allocator.free(text_manifest_path_path);
    const text_manifest_path = try guard.readUtf8File(io, allocator, text_manifest_path_path);
    defer allocator.free(text_manifest_path);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text_manifest_path, marker);
    const text_survey_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_bridge_status.zig");
    defer allocator.free(text_survey_path_path);
    const text_survey_path = try guard.readUtf8File(io, allocator, text_survey_path_path);
    defer allocator.free(text_survey_path);
    for (SURVEY_PATH) |marker| try guard.requireMarker(text_survey_path, marker);
    const text_test_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_bridge_status.zig");
    defer allocator.free(text_test_path_path);
    const text_test_path = try guard.readUtf8File(io, allocator, text_test_path_path);
    defer allocator.free(text_test_path);
    for (TEST_PATH) |marker| try guard.requireMarker(text_test_path, marker);
    const text_required_survey_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_bridge_status.zig");
    defer allocator.free(text_required_survey_markers_path);
    const text_required_survey_markers = try guard.readUtf8File(io, allocator, text_required_survey_markers_path);
    defer allocator.free(text_required_survey_markers);
    for (REQUIRED_SURVEY_MARKERS) |marker| try guard.requireMarker(text_required_survey_markers, marker);
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

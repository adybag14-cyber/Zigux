const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_DOCS_CMDLINE_GAP=pass";
pub const self_test_pass_marker = "PHASE7_DOCS_CMDLINE_GAP_SELF_TEST=pass";

const CMDLINE_GUARD = [_][]const u8{
    "scripts\\zigux/check_phase7_cmdline_packet.zig",
};

const EXPECTED_DOCS_ROOT_MARKERS = [_][]const u8{
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "scripts\\zigux/check_phase7_shared_surface.zig",
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "scripts\\zigux/check_phase7_argv_split_packet.zig",
    "scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "scripts\\zigux/validate_phase7.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_cmdline_guard_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_cmdline_guard_path);
    const text_cmdline_guard = try guard.readUtf8File(io, allocator, text_cmdline_guard_path);
    defer allocator.free(text_cmdline_guard);
    for (CMDLINE_GUARD) |marker| try guard.requireMarker(text_cmdline_guard, marker);
    const text_expected_docs_root_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_docs_root_markers_path);
    const text_expected_docs_root_markers = try guard.readUtf8File(io, allocator, text_expected_docs_root_markers_path);
    defer allocator.free(text_expected_docs_root_markers);
    for (EXPECTED_DOCS_ROOT_MARKERS) |marker| try guard.requireMarker(text_expected_docs_root_markers, marker);
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

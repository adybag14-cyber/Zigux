const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_FIXDEP_SCRIPTS_SURFACE=pass";
pub const self_test_pass_marker = "PHASE2_FIXDEP_SCRIPTS_SURFACE_SELF_TEST=pass";

const WORKFLOW_REQUIRED_MARKERS = [_][]const u8{
    "      - name: Self-test current Phase 2 fixdep scripts-surface checker\n        run: zig run scripts\\zigux/check_phase2_fixdep_scripts_surface.zig -- --self-test",
    "      - name: Check current Phase 2 fixdep scripts-surface packet\n        run: zig run scripts\\zigux/check_phase2_fixdep_scripts_surface.zig",
    "      - name: Run current Phase 2 fixdep direct replay\n        run: zig test scripts/zigux/fixdep.zig",
};

const WORKFLOW_FORBIDDEN_MARKERS = [_][]const u8{
    "zig run scripts\\zigux/check_phase2_fixdep_gate.zig",
    "zig run scripts\\zigux/check_fixdep_diff.zig",
};

const FIXDEP_FIXTURES = [_][]const u8{
    "ROOT/zigux/tests/fixtures/fixdep/sample_dependency_continuation.d",
    "ROOT/zigux/tests/fixtures/fixdep/sample_dependency_continuation_expected.txt",
    "ROOT/zigux/tests/fixtures/fixdep/sample_escaped_colon.d",
    "ROOT/zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt",
    "ROOT/zigux/tests/fixtures/fixdep/sample_escaped_space.d",
    "ROOT/zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_required_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_required_markers_path);
    const text_workflow_required_markers = try guard.readUtf8File(io, allocator, text_workflow_required_markers_path);
    defer allocator.free(text_workflow_required_markers);
    for (WORKFLOW_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_workflow_required_markers, marker);
    const text_workflow_forbidden_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_forbidden_markers_path);
    const text_workflow_forbidden_markers = try guard.readUtf8File(io, allocator, text_workflow_forbidden_markers_path);
    defer allocator.free(text_workflow_forbidden_markers);
    for (WORKFLOW_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text_workflow_forbidden_markers, marker);
    const text_fixdep_fixtures_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_fixdep_fixtures_path);
    const text_fixdep_fixtures = try guard.readUtf8File(io, allocator, text_fixdep_fixtures_path);
    defer allocator.free(text_fixdep_fixtures);
    for (FIXDEP_FIXTURES) |marker| try guard.requireMarker(text_fixdep_fixtures, marker);
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

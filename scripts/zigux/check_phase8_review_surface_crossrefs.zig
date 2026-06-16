const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "CHECK_PHASE8_REVIEW_SURFACE_CROSSREFS=pass";
pub const self_test_pass_marker = "CHECK_PHASE8_REVIEW_SURFACE_CROSSREFS_SELF_TEST=pass";

const SHARED_MARKERS = [_][]const u8{
    "scripts\\zigux/validate_phase8.zig",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "make -C zigux phase8-validate",
    "make -C zigux phase8-exec-cmd-test",
    "make -C zigux phase8-libbpf-segments-test",
};

const TESTS_README_MARKERS = [_][]const u8{
    "Phase 8 review packet",
    "Documentation/zigux/phase8-tooling-lane-sequencing.md",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "make -C zigux phase8-test",
    "keep the shared Phase 8 tooling packet explicit here too",
};

const REVIEW_CHECKLIST_MARKERS = [_][]const u8{
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "tools/lib/subcmd/exec-cmd.zig",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "scripts\\zigux/check_phase8_libbpf_segment_gate.zig",
    "scripts\\zigux/check_phase8_libbpf_shard_routes.zig",
    "tools/lib/bpf/zigux_segments/manifest.json",
    "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_shared_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_shared_markers_path);
    const text_shared_markers = try guard.readUtf8File(io, allocator, text_shared_markers_path);
    defer allocator.free(text_shared_markers);
    for (SHARED_MARKERS) |marker| try guard.requireMarker(text_shared_markers, marker);
    const text_tests_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_tests_readme_markers_path);
    const text_tests_readme_markers = try guard.readUtf8File(io, allocator, text_tests_readme_markers_path);
    defer allocator.free(text_tests_readme_markers);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text_tests_readme_markers, marker);
    const text_review_checklist_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_review_checklist_markers_path);
    const text_review_checklist_markers = try guard.readUtf8File(io, allocator, text_review_checklist_markers_path);
    defer allocator.free(text_review_checklist_markers);
    for (REVIEW_CHECKLIST_MARKERS) |marker| try guard.requireMarker(text_review_checklist_markers, marker);
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

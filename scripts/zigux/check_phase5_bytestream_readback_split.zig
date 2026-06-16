const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_BYTESTREAM_READBACK_SPLIT=pass";
pub const self_test_pass_marker = "PHASE5_BYTESTREAM_READBACK_SPLIT_SELF_TEST=pass";

const SURFACES__Documentation_zigux_phase5-sample-review-guide_md = [_][]const u8{
    "zigux/tests/phase5_bytestream_fifo_manifest.json",
    "zigux/tests/phase5_bytestream_fifo.zig",
    "zigux/tests/phase5_bytestream_fifo_survey.zig",
    "zigux/tests/phase5_build.zig",
};

const SURFACES__samples_zigux_README_md = [_][]const u8{
    "Fresh authenticated contents readback in this run now recovers this bytestream companion path too:",
    "zigux/tests/phase5_bytestream_fifo_manifest.json",
    "zigux/tests/phase5_bytestream_fifo.zig",
    "zigux/tests/phase5_bytestream_fifo_survey.zig",
    "zigux/tests/phase5_build.zig",
};

const SURFACES__scripts_zigux_README_md = [_][]const u8{
    "the directly readable companion manifest `zigux/tests/phase5_bytestream_fifo_manifest.json`",
    "authenticated contents readback in this environment still fails for `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and the shared `zigux/tests/phase5_build.zig` route",
};

const SURFACES__zigux_tests_README_md = [_][]const u8{
    "zigux/tests/phase5_bytestream_fifo_manifest.json",
    "current public-tree-backed Phase 5 bytestream companions: `zigux/tests/phase5_bytestream_fifo.zig` and `zigux/tests/phase5_bytestream_fifo_survey.zig`",
    "current public-tree-backed Phase 5 shared-build companion: `zigux/tests/phase5_build.zig`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_surfaces__documentation_zigux_phase5-sample-review-guide_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-sample-review-guide.md");
    defer allocator.free(text_surfaces__documentation_zigux_phase5-sample-review-guide_md_path);
    const text_surfaces__documentation_zigux_phase5-sample-review-guide_md = try guard.readUtf8File(io, allocator, text_surfaces__documentation_zigux_phase5-sample-review-guide_md_path);
    defer allocator.free(text_surfaces__documentation_zigux_phase5-sample-review-guide_md);
    for (SURFACES__Documentation_zigux_phase5-sample-review-guide_md) |marker| try guard.requireMarker(text_surfaces__documentation_zigux_phase5-sample-review-guide_md, marker);
    const text_surfaces__samples_zigux_readme_md_path = try guard.joinPath(allocator, root, "samples/zigux/README.md");
    defer allocator.free(text_surfaces__samples_zigux_readme_md_path);
    const text_surfaces__samples_zigux_readme_md = try guard.readUtf8File(io, allocator, text_surfaces__samples_zigux_readme_md_path);
    defer allocator.free(text_surfaces__samples_zigux_readme_md);
    for (SURFACES__samples_zigux_README_md) |marker| try guard.requireMarker(text_surfaces__samples_zigux_readme_md, marker);
    const text_surfaces__scripts_zigux_readme_md_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_surfaces__scripts_zigux_readme_md_path);
    const text_surfaces__scripts_zigux_readme_md = try guard.readUtf8File(io, allocator, text_surfaces__scripts_zigux_readme_md_path);
    defer allocator.free(text_surfaces__scripts_zigux_readme_md);
    for (SURFACES__scripts_zigux_README_md) |marker| try guard.requireMarker(text_surfaces__scripts_zigux_readme_md, marker);
    const text_surfaces__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_surfaces__zigux_tests_readme_md_path);
    const text_surfaces__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_surfaces__zigux_tests_readme_md_path);
    defer allocator.free(text_surfaces__zigux_tests_readme_md);
    for (SURFACES__zigux_tests_README_md) |marker| try guard.requireMarker(text_surfaces__zigux_tests_readme_md, marker);
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

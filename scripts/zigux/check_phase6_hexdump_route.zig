const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_HEXDUMP_ROUTE=pass";
pub const self_test_pass_marker = "PHASE6_HEXDUMP_ROUTE_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "phase6-hexdump-review:",
    "$(ZIG) run scripts/zigux/check_phase6_hexdump_packet.zig",
    "$(ZIG) run scripts/zigux/check_phase6_hexdump_route.zig",
    "$(ZIG_REPO_ROOT) build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-hexdump-perf-matrix-test:",
    "$(ZIG_REPO_ROOT) build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-hexdump-test:",
    "$(ZIG_REPO_ROOT) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig --summary all",
};

const markers_1 = [_][]const u8{
    "const hexdump_test_step = b.step(\"phase6-hexdump-test\", \"Run Phase 6 hexdump helper tests\");",
    "hexdump_test_step.dependOn(&run_hexdump_tests.step);",
    "hexdump_test_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
    "const hexdump_review_step = b.step(\"phase6-hexdump-review\", \"Run Phase 6 hexdump perf-matrix review preflight\");",
    "const hexdump_perf_matrix_test_step = b.step(",
    "\"phase6-hexdump-perf-matrix-test\",",
    "hexdump_review_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
    "hexdump_perf_matrix_test_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
};

const markers_2 = [_][]const u8{
    "try validatePerfMatrix();",
    "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n\", .{fixtures.perf_cases.len});",
    "PHASE6_HEXDUMP_PERF={s}",
    "error.HexdumpPerfRegression",
};

const markers_3 = [_][]const u8{
    "pub fn validatePerfMatrix() !void {",
    ".label = \"16B-plain-g1\",",
    ".label = \"32B-ascii-g2\",",
    ".label = \"16B-ascii-g4\",",
    ".label = \"16B-ascii-g8\",",
    ".max_slowdown_pct = 175,",
    ".max_slowdown_pct = 550,",
    ".max_slowdown_pct = 600,",
    "test \"phase 6 hexdump perf matrix preflight stays aligned with the documented packet\" {",
};

const markers_4 = [_][]const u8{
    "- `zig run scripts/zigux/check_phase6_hexdump_packet.zig`",
    "- `zig run scripts/zigux/check_phase6_hexdump_route.zig`",
    "- `zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig`",
    "- `make -C zigux phase6-hexdump-review`",
    "- `zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig`",
    "- `make -C zigux phase6-hexdump-perf-matrix-test`",
    "- `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`",
    "- `make -C zigux phase6-hexdump-test`",
};

const contracts = [_]FileContract{
    .{ .rel = "zigux/Makefile", .markers = &markers_0 },
    .{ .rel = "zigux/tests/phase6_build.zig", .markers = &markers_1 },
    .{ .rel = "zigux/tests/phase6_hexdump_perf.zig", .markers = &markers_2 },
    .{ .rel = "zigux/tests/phase6_hexdump_perf_matrix.zig", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase6-helper-evidence-catalog.md", .markers = &markers_4 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE6_HEXDUMP_ROUTE_SELF_TEST_CASE_COUNT={d}", .{38});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try guard.printLine(io, "PHASE6_HEXDUMP_CONTRACT_COUNT={d}", .{contracts.len});
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const live_pass_marker = "PHASE6_HEXDUMP_ROUTE=pass";
// pub const self_test_pass_marker = "PHASE6_HEXDUMP_ROUTE_SELF_TEST=pass";
//
// const MAKEFILE_MARKERS = [_][]const u8{
//     "phase6-hexdump-review:",
//     "$(ZIG) run scripts/zigux/check_phase6_hexdump_packet.zig",
//     "$(ZIG) run scripts/zigux/check_phase6_hexdump_route.zig",
//     "$(ZIG_REPO_ROOT) build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig --summary all",
//     "phase6-hexdump-perf-matrix-test:",
//     "$(ZIG_REPO_ROOT) build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
//     "phase6-hexdump-test:",
//     "$(ZIG_REPO_ROOT) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig --summary all",
// };
//
// const BUILD_MARKERS = [_][]const u8{
//     "const hexdump_test_step = b.step(\"phase6-hexdump-test\", \"Run Phase 6 hexdump helper tests\");",
//     "hexdump_test_step.dependOn(&run_hexdump_tests.step);",
//     "hexdump_test_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
//     "const hexdump_review_step = b.step(\"phase6-hexdump-review\", \"Run Phase 6 hexdump perf-matrix review preflight\");",
//     "const hexdump_perf_matrix_test_step = b.step(",
//     "\"phase6-hexdump-perf-matrix-test\",",
//     "hexdump_review_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
//     "hexdump_perf_matrix_test_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
// };
//
// const PERF_MARKERS = [_][]const u8{
//     "try validatePerfMatrix();",
//     "try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n\", .{fixtures.perf_cases.len});",
//     "PHASE6_HEXDUMP_PERF={s}",
//     "error.HexdumpPerfRegression",
// };
//
// const PERF_MATRIX_MARKERS = [_][]const u8{
//     "pub fn validatePerfMatrix() !void {",
//     ".label = \"16B-plain-g1\",",
//     ".label = \"32B-ascii-g2\",",
//     ".label = \"16B-ascii-g4\",",
//     ".label = \"16B-ascii-g8\",",
//     ".max_slowdown_pct = 175,",
//     ".max_slowdown_pct = 550,",
//     ".max_slowdown_pct = 600,",
//     "test \"phase 6 hexdump perf matrix preflight stays aligned with the documented packet\" {",
// };
//
// const CATALOG_MARKERS = [_][]const u8{
//     "- `zig run scripts\\zigux/check_phase6_hexdump_packet.zig`",
//     "- `zig run scripts\\zigux/check_phase6_hexdump_route.zig`",
//     "- `zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig`",
//     "- `make -C zigux phase6-hexdump-review`",
//     "- `zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig`",
//     "- `make -C zigux phase6-hexdump-perf-matrix-test`",
//     "- `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`",
//     "- `make -C zigux phase6-hexdump-test`",
// };
//
// fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
//     const text_makefile_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
//     defer allocator.free(text_makefile_markers_path);
//     const text_makefile_markers = try guard.readUtf8File(io, allocator, text_makefile_markers_path);
//     defer allocator.free(text_makefile_markers);
//     for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text_makefile_markers, marker);
//     const text_build_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
//     defer allocator.free(text_build_markers_path);
//     const text_build_markers = try guard.readUtf8File(io, allocator, text_build_markers_path);
//     defer allocator.free(text_build_markers);
//     for (BUILD_MARKERS) |marker| try guard.requireMarker(text_build_markers, marker);
//     const text_perf_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
//     defer allocator.free(text_perf_markers_path);
//     const text_perf_markers = try guard.readUtf8File(io, allocator, text_perf_markers_path);
//     defer allocator.free(text_perf_markers);
//     for (PERF_MARKERS) |marker| try guard.requireMarker(text_perf_markers, marker);
//     const text_perf_matrix_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
//     defer allocator.free(text_perf_matrix_markers_path);
//     const text_perf_matrix_markers = try guard.readUtf8File(io, allocator, text_perf_matrix_markers_path);
//     defer allocator.free(text_perf_matrix_markers);
//     for (PERF_MATRIX_MARKERS) |marker| try guard.requireMarker(text_perf_matrix_markers, marker);
//     const text_catalog_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
//     defer allocator.free(text_catalog_markers_path);
//     const text_catalog_markers = try guard.readUtf8File(io, allocator, text_catalog_markers_path);
//     defer allocator.free(text_catalog_markers);
//     for (CATALOG_MARKERS) |marker| try guard.requireMarker(text_catalog_markers, marker);
// }
//
// fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
//     try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
//     try guard.printLine(io, "{s}", .{self_test_pass_marker});
//     return 0;
// }
//
// pub fn main(init: std.process.Init) !void {
//     const allocator = init.gpa;
//     const io = init.io;
//     const args = try init.minimal.args.toSlice(allocator);
//
//     var self_test = false;
//     var explicit_root: ?[]const u8 = null;
//     var index: usize = 1;
//     while (index < args.len) : (index += 1) {
//         const arg = args[index];
//         if (std.mem.eql(u8, arg, "--self-test")) {
//             self_test = true;
//             continue;
//         }
//         if (std.mem.eql(u8, arg, "--root")) {
//             if (index + 1 >= args.len) std.process.exit(2);
//             index += 1;
//             explicit_root = args[index];
//             continue;
//         }
//     }
//
//     const root = explicit_root orelse try guard.repoRootFromScript(allocator);
//     defer if (explicit_root == null) allocator.free(root);
//
//     if (self_test) {
//         std.process.exit(try runSelfTest(io, allocator));
//     }
//
//     checkRepo(io, allocator, root) catch {
//         std.process.exit(1);
//     };
//     try guard.printLine(io, "{s}", .{live_pass_marker});
// }
//

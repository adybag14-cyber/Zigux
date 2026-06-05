const std = @import("std");
const build_options = @import("build_options");

const max_file_size = 2 * 1024 * 1024;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_file_size),
    );
}

fn expectContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn expectContainsOnce(text: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, text, needle));
}

fn expectLineOnce(text: []const u8, line: []const u8) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |current| {
        if (std.mem.eql(u8, std.mem.trim(u8, current, " \t\r"), line)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectOrder(text: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, text, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, text, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn lineIndex(text: []const u8, line: []const u8) !usize {
    var index: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |current| : (index += 1) {
        if (std.mem.eql(u8, std.mem.trim(u8, current, " \t\r"), line)) {
            return index;
        }
    }
    return error.MissingLineMarker;
}

fn expectLineOrder(text: []const u8, first: []const u8, second: []const u8) !void {
    try std.testing.expect(try lineIndex(text, first) < try lineIndex(text, second));
}

test "tests README keeps the direct-anchor lane in the Phase 1 reminder packet" {
    const allocator = std.testing.allocator;
    const readme = try readFile(allocator, build_options.tests_readme_path);
    defer allocator.free(readme);

    try expectContains(readme, "current direct-readback Phase 1 reminder packet:");
    try expectContains(readme, "- `scripts/zigux/check-phase1-direct-owner-markers.py`");
    try expectContains(readme, "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`");
    try expectContains(readme, "- `scripts/zigux/check-phase1-shared-reminder-packet.py`");
    try expectContains(readme, "- `zigux/tests/build.zig`");
    try expectContains(readme, "- `.github/workflows/zigux-bootstrap.yml`");
    try expectContains(readme, "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContains(readme, "only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`");
}

test "bootstrap workflow keeps direct-owner and direct-anchor gates before downstream Phase 1 handoff" {
    const allocator = std.testing.allocator;
    const workflow = try readFile(allocator, build_options.workflow_path);
    defer allocator.free(workflow);

    const ordered_lines = [_][]const u8{
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
        "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
        "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
        "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "run: python3 scripts/zigux/check-phase1-bench.py",
        "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
        "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    };

    for (ordered_lines) |line| {
        try expectLineOnce(workflow, line);
    }
    for (ordered_lines[0 .. ordered_lines.len - 1], ordered_lines[1..]) |first, second| {
        try expectLineOrder(workflow, first, second);
    }

    try expectLineOrder(
        workflow,
        "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    );
    try expectOrder(
        workflow,
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "run: python3 scripts/zigux/run-phase3-checks.py",
    );
}

test "shared reminder checker still exact-checks the direct-anchor workflow packet" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, build_options.shared_reminder_checker_path);
    defer allocator.free(checker);

    try expectContains(checker, "\"scripts/zigux/check-phase1-direct-owner-markers.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase1-find-bit-review-packet.py\"");
    try expectContains(checker, "\"scripts/zigux/check-phase1-rbtree-review-packet.py\"");
    try expectContains(checker, "\".github/workflows/zigux-bootstrap.yml\"");
    try expectContains(checker, "\"zigux/tests/build.zig\"");
    try expectContains(checker, "\"zigux/tests/phase1_host_tools_smoke.zig\"");
    try expectContainsOnce(checker, "\"run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\"");
    try expectContainsOnce(checker, "\"run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test\"");
    try expectContainsOnce(checker, "\"run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\"");
}

test "tests-root build file keeps the shared Phase 1 smoke route wired" {
    const allocator = std.testing.allocator;
    const tests_build = try readFile(allocator, build_options.tests_build_path);
    defer allocator.free(tests_build);

    try expectContains(tests_build, "fn addPhase1HostToolsSmoke(");
    try expectContains(tests_build, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\"),");
    try expectContains(tests_build, ".name = \"phase1-host-tools-smoke\",");
    try expectContains(tests_build, "const phase1_step = b.step(");
    try expectContains(tests_build, "\"phase1-host-tools-smoke\"");
    try expectContains(tests_build, "smoke_step.dependOn(&phase1_host_tools_smoke.step);");
    try expectContains(tests_build, "test_step.dependOn(&phase1_host_tools_smoke.step);");

    const imports = [_][]const u8{
        "root_module.addImport(\"argv_split\", argv_split_module);",
        "root_module.addImport(\"cmdline\", cmdline_module);",
        "root_module.addImport(\"find_bit\", find_bit_module);",
        "root_module.addImport(\"bitmap\", bitmap_module);",
        "root_module.addImport(\"ctype\", ctype_module);",
        "root_module.addImport(\"hweight\", hweight_module);",
        "root_module.addImport(\"list_sort\", list_sort_module);",
        "root_module.addImport(\"rbtree\", rbtree_module);",
        "root_module.addImport(\"string\", string_module);",
        "root_module.addImport(\"slab\", slab_module);",
        "root_module.addImport(\"str_error_r\", str_error_r_module);",
        "root_module.addImport(\"vsprintf\", vsprintf_module);",
        "root_module.addImport(\"zalloc\", zalloc_module);",
    };
    for (imports) |marker| {
        try expectContains(tests_build, marker);
    }
}

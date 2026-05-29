const std = @import("std");

fn readFirst(allocator: std.mem.Allocator, paths: []const []const u8) ![]u8 {
    var last_error: anyerror = error.FileNotFound;
    for (paths) |path| {
        var io_instance: std.Io.Threaded = .init(allocator, .{});
        defer io_instance.deinit();

        return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(1024 * 1024)) catch |err| {
            last_error = err;
            continue;
        };
    }
    return last_error;
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn requireOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var start: usize = 0;
    for (needles) |needle| {
        const index = std.mem.indexOfPos(u8, haystack, start, needle) orelse return error.MissingOrderedMarker;
        start = index + needle.len;
    }
}

test "phase2 cross fixture keeps the bounded two-target route inventory" {
    const fixture = try readFirst(std.testing.allocator, &.{
        "zigux/tests/fixtures/phase2_cross_targets.json",
        "fixtures/phase2_cross_targets.json",
    });
    defer std.testing.allocator.free(fixture);

    try requireContains(fixture, "\"phase\": \"Phase 2\"");
    try requireContains(fixture, "\"status\": \"active\"");
    try requireContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try requireContains(fixture, "\"target\": \"x86_64-linux\"");
    try requireContains(fixture, "\"validation_mode\": \"archive_required\"");
    try requireContains(fixture, "\"target\": \"aarch64-linux\"");
    try requireContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try requireNotContains(fixture, "\"target\": \"riscv64-linux\"");
    try std.testing.expectEqual(@as(usize, 2), countNeedle(fixture, "\"target\": "));
    try std.testing.expectEqual(@as(usize, 3), countNeedle(fixture, "\"route\": \"make -C zigux phase2-cross\""));
}

test "phase2 toolchain policy pins only the archive-backed cross target" {
    const policy = try readFirst(std.testing.allocator, &.{
        "scripts/zigux/zig-toolchain-policy.json",
        "../../scripts/zigux/zig-toolchain-policy.json",
    });
    defer std.testing.allocator.free(policy);

    try requireContains(policy, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try requireContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try requireContains(policy, "\"phase2-cross\"");
    try requireNotContains(policy, "\"aarch64-linux\"");
    try requireNotContains(policy, "\"riscv64-linux\"");
}

test "phase2 cross make route keeps direct checker then alignment checker order" {
    const makefile = try readFirst(std.testing.allocator, &.{
        "zigux/Makefile",
        "../Makefile",
    });
    defer std.testing.allocator.free(makefile);

    const route_markers = [_][]const u8{
        "phase2-cross:\n",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py\n",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py\n",
        "phase2-genksyms:",
    };

    try requireContains(makefile, ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross");
    try requireContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try requireOrdered(makefile, &route_markers);
}

test "bootstrap workflow keeps the cross checker cluster before the phase2 make routes" {
    const workflow = try readFirst(std.testing.allocator, &.{
        ".github/workflows/zigux-bootstrap.yml",
        "../../.github/workflows/zigux-bootstrap.yml",
    });
    defer std.testing.allocator.free(workflow);

    const workflow_markers = [_][]const u8{
        "Self-test current Phase 2 cross checker",
        "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
        "Check current Phase 2 direct cross-route packet",
        "run: python3 scripts/zigux/check-phase2-cross.py",
        "Self-test current Phase 2 cross selftest alignment checker",
        "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
        "Check current Phase 2 cross alignment packet",
        "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "Run current Phase 2 cross make route",
        "run: make -C zigux phase2-cross",
        "Run current Phase 2 validate make route",
    };

    try requireContains(workflow, "'zigux/**'");
    try requireOrdered(workflow, &workflow_markers);
    try std.testing.expectEqual(@as(usize, 1), countNeedle(workflow, "run: make -C zigux phase2-cross"));
}

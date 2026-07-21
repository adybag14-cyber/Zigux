const std = @import("std");
const testing = std.testing;

const fixture = @embedFile("fixtures/phase2_cross_targets.json");

fn readRepoFile(allocator: std.mem.Allocator, repo_root_path: []const u8, tests_root_path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        repo_root_path,
        allocator,
        .limited(1024 * 1024),
    ) catch |repo_root_err| switch (repo_root_err) {
        error.FileNotFound => std.Io.Dir.cwd().readFileAlloc(
            testing.io,
            tests_root_path,
            allocator,
            .limited(1024 * 1024),
        ),
        else => repo_root_err,
    };
}

fn countExactTrimmedLine(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrderedTrimmedLines(haystack: []const u8, markers: []const []const u8) !void {
    var marker_index: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (marker_index == markers.len) break;
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (std.mem.eql(u8, trimmed, markers[marker_index])) {
            marker_index += 1;
        }
    }
    try testing.expectEqual(markers.len, marker_index);
}

test "workflow carries direct cross checks into later phase2 make routes" {
    const workflow = try readRepoFile(
        testing.allocator,
        ".github/workflows/zigux-bootstrap.yml",
        "../../.github/workflows/zigux-bootstrap.yml",
    );
    defer testing.allocator.free(workflow);

    const ordered_markers = [_][]const u8{
        "run: zig run scripts/zigux/check_phase2_cross.zig -- --self-test",
        "run: zig run scripts/zigux/check_phase2_cross.zig",
        "run: zig run scripts/zigux/check_phase2_cross_selftest_alignment.zig -- --self-test",
        "run: zig run scripts/zigux/check_phase2_cross_selftest_alignment.zig",
        "run: make -C zigux phase2-cross",
        "run: zig run scripts/zigux/check_phase2_required_make_routes.zig -- --self-test",
        "run: zig run scripts/zigux/check_phase2_required_make_routes.zig",
        "run: make -C zigux phase2-genksyms",
        "run: make -C zigux phase2-validate",
        "run: make -C zigux phase2",
        "run: zig run scripts/zigux/validate_phase2.zig",
        "run: zig run scripts/zigux/validate_phase2_closure.zig -- --self-test",
        "run: zig run scripts/zigux/validate_phase2_closure.zig",
    };
    try requireOrderedTrimmedLines(workflow, &ordered_markers);

    try testing.expectEqual(@as(usize, 1), countExactTrimmedLine(workflow, "run: make -C zigux phase2-cross"));
    try testing.expectEqual(@as(usize, 1), countExactTrimmedLine(workflow, "run: make -C zigux phase2-validate"));
    try testing.expectEqual(@as(usize, 1), countExactTrimmedLine(workflow, "run: make -C zigux phase2"));
}

test "makefile keeps phase2 cross inside the aggregate phase2 route" {
    const makefile = try readRepoFile(testing.allocator, "zigux/Makefile", "../Makefile");
    defer testing.allocator.free(makefile);

    const ordered_markers = [_][]const u8{
        "phase2-cross:",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig -- --self-test",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig -- --self-test",
        "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig",
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
        "phase2: phase2-validate",
    };
    try requireOrderedTrimmedLines(makefile, &ordered_markers);

    try testing.expectEqual(@as(usize, 1), countExactTrimmedLine(makefile, "phase2-cross:"));
    try testing.expectEqual(
        @as(usize, 1),
        countExactTrimmedLine(
            makefile,
            "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
        ),
    );
    try testing.expectEqual(@as(usize, 1), countExactTrimmedLine(makefile, "phase2: phase2-validate"));
}

test "fixture keeps both current targets on the phase2 cross route" {
    try requireContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try requireContains(fixture, "\"target\": \"x86_64-linux\"");
    try requireContains(fixture, "\"validation_mode\": \"archive_required\"");
    try requireContains(fixture, "\"target\": \"aarch64-linux\"");
    try requireContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try requireAbsent(fixture, "\"target\": \"riscv64-linux\"");
}

test "stale matrix job markers stay out of the aggregate route handoff" {
    const workflow = try readRepoFile(
        testing.allocator,
        ".github/workflows/zigux-bootstrap.yml",
        "../../.github/workflows/zigux-bootstrap.yml",
    );
    defer testing.allocator.free(workflow);

    try requireAbsent(workflow, "matrix.zig_target");
    try requireAbsent(workflow, "--target ${{ matrix.zig_target }}");
    try requireAbsent(workflow, "Detect Phase 2 cross-target scope changes");
    try requireAbsent(workflow, "name: Run current Phase 2 cross matrix job");
}

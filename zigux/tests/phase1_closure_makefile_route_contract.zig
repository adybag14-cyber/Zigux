const std = @import("std");

const max_file_size = 512 * 1024;

const FileSet = struct {
    closure_note: []const u8,
    validator: []const u8,
    tests_readme: []const u8,
    makefile: []const u8,

    fn deinit(self: FileSet, allocator: std.mem.Allocator) void {
        allocator.free(self.closure_note);
        allocator.free(self.validator);
        allocator.free(self.tests_readme);
        allocator.free(self.makefile);
    }
};

fn loadFiles(allocator: std.mem.Allocator) !FileSet {
    return .{
        .closure_note = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "Documentation/zigux/phase1-closure.md", allocator, .limited(max_file_size)),
        .validator = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "scripts/zigux/validate-phase1-closure.py", allocator, .limited(max_file_size)),
        .tests_readme = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "zigux/tests/README.md", allocator, .limited(max_file_size)),
        .makefile = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "zigux/Makefile", allocator, .limited(max_file_size)),
    };
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, haystack, needle));
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 0), std.mem.count(u8, haystack, needle));
}

fn expectInOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "Makefile keeps Phase 1 closure route summary as the only active Phase 1 wrapper" {
    const allocator = std.testing.allocator;
    const files = try loadFiles(allocator);
    defer files.deinit(allocator);

    try expectContainsOnce(files.makefile, ".PHONY: phase1-route-summary ");
    try expectContainsOnce(files.makefile, "phase1-route-summary:\n");
    try expectContainsOnce(files.makefile, "scripts/zigux/check-phase1-route-summary-counts.py --self-test");
    try expectContainsOnce(files.makefile, "scripts/zigux/check-phase1-route-summary-counts.py\n");

    const historical_phase1_wrappers = [_][]const u8{
        "\nphase1-validate:",
        "\nphase1-test:",
        "\nphase1-bench:",
        "\nphase1:",
    };
    for (historical_phase1_wrappers) |wrapper| {
        try expectAbsent(files.makefile, wrapper);
    }
}

test "closure note documents the Makefile route summary boundary" {
    const allocator = std.testing.allocator;
    const files = try loadFiles(allocator);
    defer files.deinit(allocator);

    try expectContainsOnce(files.closure_note, "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`");
    try expectContainsOnce(files.closure_note, "Current `master` does materialize `zigux/Makefile` again");
    try expectContainsOnce(files.closure_note, "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`");
    try expectInOrder(
        files.closure_note,
        "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "It still does not expose `make -C zigux phase1-validate`",
    );
}

test "validator pins the current Makefile markers and forbids stale Phase 1 routes" {
    const allocator = std.testing.allocator;
    const files = try loadFiles(allocator);
    defer files.deinit(allocator);

    try expectContainsOnce(files.validator, "ZIGUX_MAKEFILE_REL = Path(\"zigux/Makefile\")");
    try expectContainsOnce(files.validator, "EXPECTED_MAKEFILE_MARKERS = (");
    try expectContainsOnce(files.validator, "\"phase1-route-summary:\"");
    try expectContainsOnce(files.validator, "FORBIDDEN_MAKEFILE_MARKERS = (");

    const forbidden_validator_markers = [_][]const u8{
        "\"phase1-validate:\"",
        "\"phase1-test:\"",
        "\"phase1-bench:\"",
        "\"phase1:\"",
    };
    for (forbidden_validator_markers) |marker| {
        try expectContainsOnce(files.validator, marker);
    }
}

test "tests README mirrors the closure Makefile boundary without reviving old routes" {
    const allocator = std.testing.allocator;
    const files = try loadFiles(allocator);
    defer files.deinit(allocator);

    try expectContainsOnce(files.tests_readme, "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContainsOnce(files.tests_readme, "current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`");
    try expectContainsOnce(files.tests_readme, "current `master` does materialize `zigux/Makefile` again");
    try expectContainsOnce(files.tests_readme, "older Phase 1 wrapper names remain historical packet members rather than active tests-root proof");
    try expectInOrder(
        files.tests_readme,
        "current `master` does materialize `zigux/Makefile` again",
        "older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    );
}

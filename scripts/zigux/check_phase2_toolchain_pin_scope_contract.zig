const std = @import("std");

const checker_paths = [_][]const u8{
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "check-phase2-toolchain-pin-scope.py",
};

const marker_families = [_][]const u8{
    "DOCS_ROOT_MARKERS",
    "MAKEFILE_MARKERS",
};

const policy_markers = [_][]const u8{
    "def validate_policy",
    "channel_minimum_lockstep",
    "archive_target_scope",
    "required_make_routes",
    "archive_sha256",
    "x86_64-linux",
    "phase2-toolchain",
    "phase2-validate",
};

const checker_route_markers = [_][]const u8{
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
};

fn readCheckerSource(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    for (checker_paths) |path| {
        return std.Io.Dir.cwd().readFileAlloc(
            io_instance.io(),
            path,
            allocator,
            .limited(512 * 1024),
        ) catch |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        };
    }
    return error.FileNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try expectContains(haystack, needle);
    }
}

fn expectAnyContains(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        if (std.mem.indexOf(u8, haystack, needle) != null) return;
    }
    return error.MissingAnyMarker;
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn sliceBetween(haystack: []const u8, first: []const u8, second: []const u8) ![]const u8 {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const body_start = first_index + first.len;
    const second_relative_index = std.mem.indexOf(u8, haystack[body_start..], second) orelse return error.MissingSecondMarker;
    return haystack[body_start .. body_start + second_relative_index];
}

test "pin-scope checker keeps the toolchain marker families visible" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContainsAll(source, &marker_families);
    try expectAnyContains(source, &[_][]const u8{ "REVIEW_MARKERS", "REVIEW_CHECKLIST_MARKERS" });
    try expectAnyContains(source, &[_][]const u8{ "BOOTSTRAP_MARKERS", "CLOSURE_MARKERS" });
    try expectAnyContains(source, &[_][]const u8{ "WORKFLOW_MARKERS", "EXACT_WORKFLOW_RUN_COUNTS" });
    try expectAnyContains(source, &[_][]const u8{ "TESTS_MARKERS", "TESTS_README_MARKERS" });
    try expectContains(source, "validate_policy");
    try expectContains(source, "PHASE2_TOOLCHAIN_PIN_SCOPE=fail");
    try expectContains(source, "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass");
    try expectContains(source, "PHASE2_TOOLCHAIN_PIN_SCOPE=pass");
}

test "pin-scope checker keeps policy and archive scope checks explicit" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContainsAll(source, &policy_markers);
    const policy_body = try sliceBetween(source, "def validate_policy", "def collect_issues");
    try expectBefore(policy_body, "channel_minimum_lockstep", "archive_target_scope");
    try expectBefore(policy_body, "archive_target_scope", "required_make_routes");
}

test "pin-scope checker keeps workflow and make-route action paths explicit" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContainsAll(source, &checker_route_markers);
    try expectAnyContains(source, &[_][]const u8{
        "check-zig-toolchain.py --policy-only",
        "check-zig-toolchain.py --self-test",
    });
    try expectAnyContains(source, &[_][]const u8{
        "check-zig-toolchain.py --archive-only --allow-missing",
        "check-zig-toolchain.py --zig",
    });
}

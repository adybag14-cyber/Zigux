const std = @import("std");
const testing = std.testing;

const shared_tooling_checkers = [_][]const u8{
    "zig run scripts/zigux/check_phase2_tool_manifest.zig",
    "zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig",
    "zig run scripts/zigux/check_phase2_artifact_tools_manifest.zig",
    "zig run scripts/zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    "zig run scripts/zigux/check_phase2_cross.zig",
    "zig run scripts/zigux/check_phase2_fixdep_gate.zig",
    "zig run scripts/zigux/check_fixdep_diff.zig",
};

const shared_make_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

fn readText(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn requireExactOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try testing.expectEqual(@as(usize, 1), count);
}

fn joinedLine(comptime prefix: []const u8, comptime values: []const []const u8) []const u8 {
    comptime {
        var line: []const u8 = prefix;
        for (values, 0..) |value, index| {
            if (index != 0) line = line ++ ",";
            line = line ++ value;
        }
        return line;
    }
}

const expected_shared_tooling_line = joinedLine(
    "PHASE2_SHARED_TOOLING_CHECKERS=",
    &shared_tooling_checkers,
);

const expected_make_routes_line = joinedLine(
    "PHASE2_SHARED_MAKE_ROUTES=",
    &shared_make_routes,
);

test "phase2 closure note pins the shared tooling checker packet" {
    const closure = try readText("Documentation/zigux/phase2-closure.md");
    defer testing.allocator.free(closure);

    try requireContains(closure, expected_shared_tooling_line);
    try requireExactOnce(closure, expected_shared_tooling_line);

    for (shared_tooling_checkers) |checker| {
        try requireContains(closure, checker);
    }

    try requireOrdered(
        closure,
        "## Current Shared Repo-Tooling Evidence",
        expected_shared_tooling_line,
    );
    try requireOrdered(
        closure,
        "scripts\zigux/check_phase2_artifact_tools_manifest.zig",
        "scripts\zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    );
    try requireOrdered(
        closure,
        "scripts\zigux/check_phase2_cross.zig",
        "scripts\zigux/check_phase2_fixdep_gate.zig",
    );
    try requireMissing(closure, "PHASE2_SHARED_TOOLING_CHECKERS=zig run scripts/zigux/check_phase2_tool_manifest.zig,zig run scripts/zigux/check_phase2_cross.zig");
}

test "phase2 manifest and workflow keep shared tooling surfaces live" {
    const manifest = try readText("zigux/tests/fixtures/phase2_tool_manifest.json");
    defer testing.allocator.free(manifest);
    const workflow = try readText(".github/workflows/zigux-bootstrap.yml");
    defer testing.allocator.free(workflow);

    for (shared_tooling_checkers) |checker| {
        try requireContains(manifest, checker[8..]);
    }

    try requireContains(manifest, "\"scripts/zigux/artifact_diff.zig\"");
    try requireContains(manifest, "\"scripts\zigux/check_phase2_artifact_tools_manifest.zig\"");
    try requireContains(manifest, "\"scripts\zigux/check_phase2_kconfig_allconfig_helper_packet.zig\"");
    try requireContains(manifest, "\"scripts\zigux/check_phase2_fixdep_gate.zig\"");
    try requireContains(manifest, "\"scripts\zigux/check_fixdep_diff.zig\"");
    try requireContains(manifest, "\"repo_reality_gaps\": []");

    try requireOrdered(
        workflow,
        "run: zig run scripts/zigux/check_phase2_bootstrap_workflow_routes.zig",
        "run: zig run scripts/zigux/check_phase2_artifact_tools_manifest.zig",
    );
    try requireOrdered(
        workflow,
        "run: zig run scripts/zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
        "run: zig run scripts/zigux/check_phase2_kbuild_routes.zig -- --self-test",
    );
}

test "phase2 closure note and Makefile agree on shared make routes" {
    const closure = try readText("Documentation/zigux/phase2-closure.md");
    defer testing.allocator.free(closure);
    const makefile = try readText("zigux/Makefile");
    defer testing.allocator.free(makefile);

    try requireContains(closure, expected_make_routes_line);
    try requireExactOnce(closure, expected_make_routes_line);

    for (shared_make_routes) |route| {
        try requireContains(closure, route);
    }

    try requireOrdered(closure, expected_shared_tooling_line, expected_make_routes_line);
    try requireOrdered(makefile, "phase2-toolchain:", "phase2-tools:");
    try requireOrdered(makefile, "phase2-tools:", "phase2-kconfig:");
    try requireOrdered(makefile, "phase2-cross:", "phase2-genksyms:");
    try requireOrdered(makefile, "phase2-genksyms:", "phase2-fixdep:");
    try requireOrdered(
        makefile,
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
        "phase2: phase2-validate",
    );
    try requireMissing(closure, "make -C zigux phase2-closure");
}

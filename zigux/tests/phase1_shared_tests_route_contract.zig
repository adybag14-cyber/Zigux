const std = @import("std");
const data = @import("phase1_shared_tests_route_data");

const MissingMarker = error{MissingMarker};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) return MissingMarker.MissingMarker;
}

test "phase 1 closure note keeps the shared tests route explicit" {
    try expectContains(
        data.closure_note,
        "PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    );
    try expectContains(
        data.closure_note,
        "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py",
    );
    try expectContains(
        data.closure_note,
        "PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py",
    );
    try expectContains(data.closure_note, "zigux/tests/build.zig");
    try expectContains(data.closure_note, "zigux/tests/phase1_host_tools_smoke.zig");
    try expectContains(data.closure_note, "zigux/tests/phase1_helpers.zig");
}

test "tests-root build keeps phase 1 host tools smoke as a focused step" {
    try expectContains(data.tests_build, "fn addPhase1HostToolsSmoke(");
    try expectContains(data.tests_build, "phase1_host_tools_smoke.zig");
    try expectContains(data.tests_build, "phase1-host-tools-smoke");
    try expectContains(data.tests_build, "const phase1_step = b.step(");
    try expectContains(
        data.tests_build,
        "Run the shared Phase 1 host-tools smoke anchor from zigux/tests",
    );
    try expectContains(data.tests_build, "phase1_step.dependOn(&phase1_host_tools_smoke.step)");
}

test "shared route remains tied to the closed thirteen helper manifest" {
    const Manifest = struct {
        phase: []const u8,
        status: []const u8,
        helper_count: usize,
        helpers: []const []const u8,
    };

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, data.helper_manifest, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    try std.testing.expectEqualStrings("Phase 1", parsed.value.phase);
    try std.testing.expectEqualStrings("closed", parsed.value.status);
    try std.testing.expectEqual(@as(usize, 13), parsed.value.helper_count);
    try std.testing.expectEqual(parsed.value.helper_count, parsed.value.helpers.len);
}

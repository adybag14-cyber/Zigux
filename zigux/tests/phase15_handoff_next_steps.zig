const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| if (std.mem.eql(u8, item, needle)) return;
    return error.TestUnexpectedResult;
}

const Manifest = struct {
    surveyed_commit: []const u8,
    present_paths: []const []const u8,
    still_missing_paths: []const []const u8,
    required_markers: []const []const u8,
    missing_route_markers: []const []const u8,
};

test "phase 15 handoff manifest records route recovery as present evidence" {
    const source = try readRepoFile("zigux/tests/phase15_handoff_next_steps_manifest.json");
    defer std.testing.allocator.free(source);
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, source, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("current-master-readback-2026-07-21", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 0), manifest.still_missing_paths.len);
    try std.testing.expectEqual(@as(usize, 0), manifest.missing_route_markers.len);
    try expectSliceContains(manifest.present_paths, "Documentation/zigux/phase15-route-recovery.md");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_route_recovery.zig");
    try expectSliceContains(manifest.present_paths, "zigux/Makefile");
    try expectSliceContains(manifest.present_paths, ".github/workflows/zigux-bootstrap.yml");
    try expectSliceContains(manifest.required_markers, "PHASE15_ROUTE_RECOVERY_STATUS=landed");
    try expectSliceContains(manifest.required_markers, "No Architecture Council approval is recorded by route recovery");
}

test "phase 15 handoff note keeps route recovery and approval boundaries explicit" {
    const note = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md");
    defer std.testing.allocator.free(note);
    try expectContains(note, "PHASE15_ROUTE_RECOVERY_STATUS=landed");
    try expectContains(note, "keep the recovered Phase 15 wrapper and shared-CI routes green");
    try expectContains(note, "if a Phase 15 wrapper or shared-CI route drifts, rerun the route-recovery contract");
    try expectContains(note, "No Architecture Council approval is recorded by route recovery");
}

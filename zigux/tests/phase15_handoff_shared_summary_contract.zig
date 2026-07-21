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

test "Phase 15 handoff and shared summary expose route recovery" {
    const handoff = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md");
    defer std.testing.allocator.free(handoff);
    const summary = try readRepoFile("Documentation/zigux/phase15-shared-summary-gap.md");
    defer std.testing.allocator.free(summary);

    for ([_][]const u8{
        "PHASE15_ROUTE_RECOVERY_STATUS=landed",
        "make -C zigux phase15-validate",
        "make -C zigux phase15-test",
        "make -C zigux phase15",
        "No Architecture Council approval is recorded by route recovery",
    }) |marker| {
        try expectContains(handoff, marker);
        try expectContains(summary, marker);
    }
}

test "Phase 15 handoff identifies historical route-gap prose as superseded" {
    const handoff = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md");
    defer std.testing.allocator.free(handoff);
    try expectContains(handoff, "historical survey findings superseded by this current-state block");
    try expectContains(handoff, "Documentation/zigux/phase15-route-recovery.md");
    try expectContains(handoff, "keep the recovered Phase 15 wrapper and shared-CI routes green");
}

const std = @import("std");
const devres = @import("devres");

test "phase13 devres zero-sized coherent planning never retains detach-time cleanup ownership" {
    const plan = try devres.DevresHelperLab.planManagedDmamAllocCoherent(.{
        .requested_size = 0,
        .release_record_allocated = true,
        .allocation_succeeds = true,
    });

    try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
    try std.testing.expectEqual(@as(u64, 0), plan.requested_size);
    try std.testing.expect(!plan.allocation_ready);
    try std.testing.expect(!plan.added_to_devres);
    try std.testing.expect(!plan.release_record_retained);
    try std.testing.expect(plan.release_record_freed);
    try std.testing.expect(!plan.should_free_on_detach);
}

test "phase13 devres coherent planning tracks shared release-record lifetime decisions across the bounded matrix" {
    const cases = [_]struct {
        requested_size: u64,
        allocation_succeeds: bool,
        expect_retain: bool,
    }{
        .{ .requested_size = 0, .allocation_succeeds = false, .expect_retain = false },
        .{ .requested_size = 0, .allocation_succeeds = true, .expect_retain = false },
        .{ .requested_size = 4096, .allocation_succeeds = false, .expect_retain = false },
        .{ .requested_size = 4096, .allocation_succeeds = true, .expect_retain = true },
    };

    for (cases) |case| {
        const plan = try devres.DevresHelperLab.planManagedDmamAllocCoherent(.{
            .requested_size = case.requested_size,
            .release_record_allocated = true,
            .allocation_succeeds = case.allocation_succeeds,
        });
        const lifetime = devres.DevresHelperLab.planManagedReleaseRecordLifetime(case.expect_retain);

        try std.testing.expectEqual(case.expect_retain, plan.allocation_ready);
        try std.testing.expectEqual(lifetime.added_to_devres, plan.added_to_devres);
        try std.testing.expectEqual(lifetime.release_record_retained, plan.release_record_retained);
        try std.testing.expectEqual(lifetime.release_record_freed, plan.release_record_freed);
        try std.testing.expectEqual(lifetime.should_release_on_detach, plan.should_free_on_detach);
    }
}

const std = @import("std");
const devres_scatterlist = @import("devres_scatterlist");

test "phase13 devres descriptor records helper-first scatterlist planning" {
    const descriptor = devres_scatterlist.DevresScatterlistHelper.descriptor();

    try std.testing.expectEqualStrings("devres_scatterlist_helper", descriptor.name);
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_scatterlist_lifetime_planning);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_live_scatterlist);
}

test "phase13 devres retains the release record when helper-first scatterlist planning succeeds" {
    const plan = try devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistMap(.{
        .original_entries = 6,
        .mapped_entries = 4,
        .release_record_allocated = true,
    });

    try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
    try std.testing.expectEqual(@as(u32, 6), plan.original_entries);
    try std.testing.expectEqual(@as(u32, 4), plan.mapped_entries);
    try std.testing.expect(plan.mapping_ready);
    try std.testing.expect(plan.added_to_devres);
    try std.testing.expect(plan.release_record_retained);
    try std.testing.expect(!plan.release_record_freed);
    try std.testing.expect(plan.should_unmap_on_detach);
}

test "phase13 devres frees the scatterlist release record when no mapped segments are returned" {
    const plan = try devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistMap(.{
        .original_entries = 6,
        .mapped_entries = 0,
        .release_record_allocated = true,
    });

    try std.testing.expectEqual(@as(u32, 6), plan.original_entries);
    try std.testing.expectEqual(@as(u32, 0), plan.mapped_entries);
    try std.testing.expect(!plan.mapping_ready);
    try std.testing.expect(!plan.added_to_devres);
    try std.testing.expect(!plan.release_record_retained);
    try std.testing.expect(plan.release_record_freed);
    try std.testing.expect(!plan.should_unmap_on_detach);
}

test "phase13 devres frees the scatterlist release record when mapped segments exceed the original count" {
    const plan = try devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistMap(.{
        .original_entries = 3,
        .mapped_entries = 5,
        .release_record_allocated = true,
    });

    try std.testing.expectEqual(@as(u32, 3), plan.original_entries);
    try std.testing.expectEqual(@as(u32, 5), plan.mapped_entries);
    try std.testing.expect(!plan.mapping_ready);
    try std.testing.expect(!plan.added_to_devres);
    try std.testing.expect(!plan.release_record_retained);
    try std.testing.expect(plan.release_record_freed);
    try std.testing.expect(!plan.should_unmap_on_detach);
}

test "phase13 devres rejects scatterlist planning when the release record cannot be allocated" {
    try std.testing.expectError(error.OutOfMemory, devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistMap(.{
        .original_entries = 2,
        .mapped_entries = 2,
        .release_record_allocated = false,
    }));
}

test "phase13 devres scatterlist release matching stays exact across original and mapped counts" {
    const exact = devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistUnmap(6, 4, 6, 4);
    try std.testing.expectEqualStrings("lib/devres.c", exact.anchor);
    try std.testing.expect(exact.release_matches);
    try std.testing.expect(!exact.warns_on_release_miss);

    const miss = devres_scatterlist.DevresScatterlistHelper.planManagedScatterlistUnmap(6, 4, 6, 3);
    try std.testing.expect(!miss.release_matches);
    try std.testing.expect(miss.warns_on_release_miss);
}

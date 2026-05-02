const std = @import("std");
const devres_dma_coherent = @import("devres_dma_coherent");

test "phase13 devres descriptor records helper-first dma coherent planning" {
    const descriptor = devres_dma_coherent.DevresDmaCoherentHelper.descriptor();

    try std.testing.expectEqualStrings("devres_dma_coherent_helper", descriptor.name);
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_dma_coherent_lifetime_planning);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_live_scatterlist);
}

test "phase13 devres retains the release record when coherent dma planning returns both address and handle" {
    const plan = try devres_dma_coherent.DevresDmaCoherentHelper.planManagedDmaCoherentAlloc(.{
        .size = 0x200,
        .release_record_allocated = true,
        .cpu_address = 0xc000,
        .dma_handle = 0x1234,
    });

    try std.testing.expectEqualStrings("lib/devres.c", plan.anchor);
    try std.testing.expectEqual(@as(u64, 0x200), plan.size);
    try std.testing.expectEqual(@as(?usize, 0xc000), plan.cpu_address);
    try std.testing.expectEqual(@as(?u64, 0x1234), plan.dma_handle);
    try std.testing.expect(plan.mapping_ready);
    try std.testing.expect(plan.added_to_devres);
    try std.testing.expect(plan.release_record_retained);
    try std.testing.expect(!plan.release_record_freed);
    try std.testing.expect(plan.should_free_on_detach);
}

test "phase13 devres frees the coherent dma release record when the dma handle is missing" {
    const plan = try devres_dma_coherent.DevresDmaCoherentHelper.planManagedDmaCoherentAlloc(.{
        .size = 0x80,
        .release_record_allocated = true,
        .cpu_address = 0xc800,
        .dma_handle = null,
    });

    try std.testing.expectEqual(@as(?usize, 0xc800), plan.cpu_address);
    try std.testing.expectEqual(@as(?u64, null), plan.dma_handle);
    try std.testing.expect(!plan.mapping_ready);
    try std.testing.expect(!plan.added_to_devres);
    try std.testing.expect(!plan.release_record_retained);
    try std.testing.expect(plan.release_record_freed);
    try std.testing.expect(!plan.should_free_on_detach);
}

test "phase13 devres rejects coherent dma planning when the release record cannot be allocated" {
    try std.testing.expectError(error.OutOfMemory, devres_dma_coherent.DevresDmaCoherentHelper.planManagedDmaCoherentAlloc(.{
        .size = 0x40,
        .release_record_allocated = false,
        .cpu_address = 0xd000,
        .dma_handle = 0x55,
    }));
}

test "phase13 devres coherent dma release matching stays exact across address and handle" {
    const exact = devres_dma_coherent.DevresDmaCoherentHelper.planManagedDmaCoherentFree(0xd800, 0x100, 0xd800, 0x100);
    try std.testing.expectEqualStrings("lib/devres.c", exact.anchor);
    try std.testing.expect(exact.release_matches);
    try std.testing.expect(!exact.warns_on_release_miss);

    const miss = devres_dma_coherent.DevresDmaCoherentHelper.planManagedDmaCoherentFree(0xd800, 0x100, 0xd800, 0x101);
    try std.testing.expect(!miss.release_matches);
    try std.testing.expect(miss.warns_on_release_miss);
}

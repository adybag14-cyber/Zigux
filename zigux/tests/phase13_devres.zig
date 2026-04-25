const std = @import("std");
const devres = @import("devres");

test "phase13 devres descriptor stays anchored to lib/devres.c" {
    const descriptor = devres.DevresHelperLab.descriptor();

    try std.testing.expectEqualStrings("devres_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("lib/devres.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ioremap_lifetime_planning);
    try std.testing.expect(descriptor.provides_release_pointer_match);
    try std.testing.expect(!descriptor.touches_live_device_lists);
    try std.testing.expect(!descriptor.touches_live_mmio);
}

test "phase13 devres retains the release record when managed ioremap succeeds" {
    const result = try devres.DevresHelperLab.planManagedIoremapAcquire(.{
        .kind = .write_combined,
        .release_record_allocated = true,
        .mapped_address = 0x1000,
    });

    try std.testing.expectEqualStrings("lib/devres.c", result.anchor);
    try std.testing.expectEqual(devres.ManagedIoremapKind.write_combined, result.kind);
    try std.testing.expectEqual(@as(?usize, 0x1000), result.mapped_address);
    try std.testing.expect(result.added_to_devres);
    try std.testing.expect(result.release_record_retained);
    try std.testing.expect(!result.release_record_freed);
    try std.testing.expectEqual(devres.ReleaseAction.iounmap, result.release_action);
    try std.testing.expect(result.should_unmap_on_detach);
}

test "phase13 devres frees the release record when mapping fails after allocation" {
    const result = try devres.DevresHelperLab.planManagedIoremapAcquire(.{
        .kind = .non_posted,
        .release_record_allocated = true,
        .mapped_address = null,
    });

    try std.testing.expectEqual(devres.ManagedIoremapKind.non_posted, result.kind);
    try std.testing.expectEqual(@as(?usize, null), result.mapped_address);
    try std.testing.expect(!result.added_to_devres);
    try std.testing.expect(!result.release_record_retained);
    try std.testing.expect(result.release_record_freed);
    try std.testing.expect(!result.should_unmap_on_detach);
}

test "phase13 devres rejects ioremap planning when the release record cannot be allocated" {
    try std.testing.expectError(error.OutOfMemory, devres.DevresHelperLab.planManagedIoremapAcquire(.{
        .kind = .plain,
        .release_record_allocated = false,
        .mapped_address = 0x2000,
    }));
}

test "phase13 devres release matching stays pointer-exact" {
    try std.testing.expect(devres.DevresHelperLab.ioremapReleaseMatches(0x4000, 0x4000));
    try std.testing.expect(!devres.DevresHelperLab.ioremapReleaseMatches(0x4000, 0x4010));
}

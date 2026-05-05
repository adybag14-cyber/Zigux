const std = @import("std");
const virtio_driver_id = @import("virtio_driver_id");

test "phase10 virtio driver id helper records bounded registration identity strings" {
    const helper = try virtio_driver_id.VirtioDriverIdMatcher.init(7, 0x1040, 0x1AF4);
    const descriptor = virtio_driver_id.VirtioDriverIdMatcher.descriptor();
    const summary = helper.registrationSummary();

    try std.testing.expectEqualStrings("virtio_driver_id_matcher_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_validation);
    try std.testing.expect(!descriptor.touches_transport_mmio);

    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 7), summary.device_index);
    try std.testing.expectEqual(@as(u32, 0x1040), summary.device_id);
    try std.testing.expectEqual(@as(u32, 0x1AF4), summary.vendor_id);
    try std.testing.expectEqualStrings("virtio7", summary.device_name);
    try std.testing.expectEqualStrings("virtio:d00001040v00001af4", summary.modalias);
}

test "phase10 virtio driver id helper records exact id-table matches" {
    const helper = try virtio_driver_id.VirtioDriverIdMatcher.init(5, 0x1040, 0x1AF4);
    const summary = helper.driverIdMatchSummary(&.{
        .{ .device_id = 0x1000, .vendor_id = 0x1AF4 },
        .{ .device_id = 0x1040, .vendor_id = 0x1AF4 },
        .{ .device_id = virtio_driver_id.any_id, .vendor_id = virtio_driver_id.any_id },
    });

    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 0x1040), summary.device_id);
    try std.testing.expectEqual(@as(u32, 0x1AF4), summary.vendor_id);
    try std.testing.expectEqual(@as(usize, 3), summary.candidate_count);
    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(@as(?usize, 1), summary.matched_rule_index);
    try std.testing.expect(!summary.matched_device_any);
    try std.testing.expect(!summary.matched_vendor_any);
}

test "phase10 virtio driver id helper models wildcard and unmatched paths" {
    const helper = try virtio_driver_id.VirtioDriverIdMatcher.init(3, 0x1052, 0x1AF4);

    var summary = helper.driverIdMatchSummary(&.{
        .{ .device_id = virtio_driver_id.any_id, .vendor_id = 0x1AF4 },
    });
    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(@as(?usize, 0), summary.matched_rule_index);
    try std.testing.expect(summary.matched_device_any);
    try std.testing.expect(!summary.matched_vendor_any);

    summary = helper.driverIdMatchSummary(&.{
        .{ .device_id = 0x1052, .vendor_id = virtio_driver_id.any_id },
    });
    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(@as(?usize, 0), summary.matched_rule_index);
    try std.testing.expect(!summary.matched_device_any);
    try std.testing.expect(summary.matched_vendor_any);

    summary = helper.driverIdMatchSummary(&.{
        .{ .device_id = 0x1040, .vendor_id = 0x1AF4 },
    });
    try std.testing.expect(!summary.matched);
    try std.testing.expectEqual(@as(?usize, null), summary.matched_rule_index);
    try std.testing.expect(!summary.matched_device_any);
    try std.testing.expect(!summary.matched_vendor_any);
}
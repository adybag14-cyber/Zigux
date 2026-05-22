const std = @import("std");
const virtio_core = @import("virtio_core");
const virtio_driver_id = @import("virtio_driver_id");

test "phase10 virtio driver id replay keeps exact and wildcard dispositions reviewable" {
    var core = try virtio_core.VirtioCoreLab.init(0x1050, 2);

    var review = virtio_driver_id.reviewDriverIdMatch(&core, &.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
        .{ .device_id = 0x1050, .vendor_id = virtio_core.default_vendor_id },
    });
    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", review.anchor);
    try std.testing.expect(review.matched);
    try std.testing.expectEqual(@as(?usize, 1), review.matched_rule_index);
    try std.testing.expectEqual(virtio_driver_id.DriverIdMatchDisposition.exact_match, review.disposition);
    try std.testing.expect(review.exact_device_match);
    try std.testing.expect(review.exact_vendor_match);

    core.setVendorId(0x1AF5);
    review = virtio_driver_id.reviewDriverIdMatch(&core, &.{
        .{ .device_id = virtio_core.any_id, .vendor_id = 0x1AF5 },
    });
    try std.testing.expect(review.matched);
    try std.testing.expectEqual(@as(?usize, 0), review.matched_rule_index);
    try std.testing.expectEqual(virtio_driver_id.DriverIdMatchDisposition.device_wildcard_match, review.disposition);
    try std.testing.expect(!review.exact_device_match);
    try std.testing.expect(review.exact_vendor_match);

    const summary = virtio_driver_id.summarize(&core, &.{
        .{ .device_id = virtio_core.any_id, .vendor_id = 0x1AF5 },
    });
    try std.testing.expectEqual(virtio_driver_id.MatchDisposition.device_any, virtio_driver_id.disposition(summary));
    try std.testing.expect(virtio_driver_id.matchedRuleUsesWildcard(summary));
}

test "phase10 virtio driver id replay keeps vendor wildcard and no-match paths separate" {
    const wildcard_summary = try virtio_driver_id.reviewDevice(0x1052, 0x1AF6, 1, &.{
        .{ .device_id = 0x1052, .vendor_id = virtio_core.any_id },
    });
    try std.testing.expect(wildcard_summary.matched);
    try std.testing.expectEqual(
        virtio_driver_id.DriverIdMatchDisposition.vendor_wildcard_match,
        wildcard_summary.disposition,
    );
    try std.testing.expect(wildcard_summary.exact_device_match);
    try std.testing.expect(!wildcard_summary.exact_vendor_match);

    const missing_summary = try virtio_driver_id.reviewDevice(0x1052, 0x1AF6, 1, &.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
    });
    try std.testing.expect(!missing_summary.matched);
    try std.testing.expectEqual(@as(?usize, null), missing_summary.matched_rule_index);
    try std.testing.expectEqual(
        virtio_driver_id.DriverIdMatchDisposition.no_match,
        missing_summary.disposition,
    );
}

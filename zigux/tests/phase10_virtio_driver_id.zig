const std = @import("std");
const virtio_core = @import("virtio_core");
const virtio_driver_id = @import("virtio_driver_id");

test "phase10 virtio driver id replay keeps exact first-match claims reviewable" {
    var core = try virtio_core.VirtioCoreLab.init(0x1040, 2);

    const summary = virtio_driver_id.summarize(&core, &.{
        .{ .device_id = 0x1000, .vendor_id = virtio_core.default_vendor_id },
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
        .{ .device_id = virtio_core.any_id, .vendor_id = virtio_core.any_id },
    });

    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(@as(?usize, 1), summary.matched_rule_index);
    try std.testing.expectEqual(virtio_driver_id.MatchDisposition.exact, virtio_driver_id.disposition(summary));
    try std.testing.expect(!virtio_driver_id.matchedRuleUsesWildcard(summary));
}

test "phase10 virtio driver id replay distinguishes wildcard dispositions" {
    var core = try virtio_core.VirtioCoreLab.init(0x1052, 2);

    var summary = virtio_driver_id.summarize(&core, &.{
        .{ .device_id = virtio_core.any_id, .vendor_id = virtio_core.default_vendor_id },
    });
    try std.testing.expectEqual(virtio_driver_id.MatchDisposition.device_any, virtio_driver_id.disposition(summary));
    try std.testing.expect(virtio_driver_id.matchedRuleUsesWildcard(summary));

    core.setVendorId(0x1AF5);
    summary = virtio_driver_id.summarize(&core, &.{
        .{ .device_id = 0x1052, .vendor_id = virtio_core.any_id },
    });
    try std.testing.expectEqual(virtio_driver_id.MatchDisposition.vendor_any, virtio_driver_id.disposition(summary));

    summary = virtio_driver_id.summarize(&core, &.{
        .{ .device_id = virtio_core.any_id, .vendor_id = virtio_core.any_id },
    });
    try std.testing.expectEqual(virtio_driver_id.MatchDisposition.any_any, virtio_driver_id.disposition(summary));
}

test "phase10 virtio driver id replay keeps first wildcard winner visible" {
    var core = try virtio_core.VirtioCoreLab.init(0x1040, 1);

    const summary = virtio_driver_id.summarize(&core, &.{
        .{ .device_id = virtio_core.any_id, .vendor_id = virtio_core.default_vendor_id },
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
    });

    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(@as(?usize, 0), summary.matched_rule_index);
    try std.testing.expectEqual(virtio_driver_id.MatchDisposition.device_any, virtio_driver_id.disposition(summary));
}

test "phase10 virtio driver id replay keeps unmatched tables explicit" {
    var core = try virtio_core.VirtioCoreLab.init(0x1040, 1);
    core.setVendorId(0x1AF5);

    const summary = virtio_driver_id.summarize(&core, &.{
        .{ .device_id = 0x1000, .vendor_id = virtio_core.default_vendor_id },
    });

    try std.testing.expect(!summary.matched);
    try std.testing.expectEqual(@as(?usize, null), summary.matched_rule_index);
    try std.testing.expectEqual(virtio_driver_id.MatchDisposition.unmatched, virtio_driver_id.disposition(summary));
    try std.testing.expect(!virtio_driver_id.matchedRuleUsesWildcard(summary));
}

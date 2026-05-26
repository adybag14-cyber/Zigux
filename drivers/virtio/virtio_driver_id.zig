const std = @import("std");
const virtio_core = @import("virtio_core");

pub const anchor_path = virtio_core.anchor_path;

pub const MatchRule = virtio_core.DriverIdMatchRule;
pub const MatchSummary = virtio_core.DriverIdMatchSummary;

pub const DriverIdMatchDisposition = enum {
    no_match,
    exact_match,
    device_wildcard_match,
    vendor_wildcard_match,
    full_wildcard_match,
};

pub const DriverIdReviewSummary = struct {
    anchor: []const u8,
    device_id: u32,
    vendor_id: u32,
    candidate_count: usize,
    matched: bool,
    matched_rule_index: ?usize,
    matched_device_any: bool,
    matched_vendor_any: bool,
    disposition: DriverIdMatchDisposition,
    exact_device_match: bool,
    exact_vendor_match: bool,
};

pub const MatchDisposition = enum {
    unmatched,
    exact,
    device_any,
    vendor_any,
    any_any,
};

pub fn reviewDriverIdMatch(
    core: *const virtio_core.VirtioCoreLab,
    rules: []const virtio_core.DriverIdMatchRule,
) DriverIdReviewSummary {
    return reviewSummary(core.driverIdMatchSummary(rules));
}

pub fn summarize(core: *const virtio_core.VirtioCoreLab, rules: []const MatchRule) MatchSummary {
    return core.driverIdMatchSummary(rules);
}

pub fn disposition(summary: MatchSummary) MatchDisposition {
    if (!summary.matched) return .unmatched;
    if (summary.matched_device_any and summary.matched_vendor_any) return .any_any;
    if (summary.matched_device_any) return .device_any;
    if (summary.matched_vendor_any) return .vendor_any;
    return .exact;
}

pub fn matchedRuleUsesWildcard(summary: MatchSummary) bool {
    return summary.matched_device_any or summary.matched_vendor_any;
}

pub fn reviewDevice(
    device_id: u32,
    vendor_id: u32,
    queue_count: u16,
    rules: []const virtio_core.DriverIdMatchRule,
) !DriverIdReviewSummary {
    var core = try virtio_core.VirtioCoreLab.init(device_id, queue_count);
    core.setVendorId(vendor_id);
    return reviewDriverIdMatch(&core, rules);
}

fn reviewSummary(summary: MatchSummary) DriverIdReviewSummary {
    const review_disposition: DriverIdMatchDisposition = if (!summary.matched)
        .no_match
    else if (summary.matched_device_any and summary.matched_vendor_any)
        .full_wildcard_match
    else if (summary.matched_device_any)
        .device_wildcard_match
    else if (summary.matched_vendor_any)
        .vendor_wildcard_match
    else
        .exact_match;

    return .{
        .anchor = summary.anchor,
        .device_id = summary.device_id,
        .vendor_id = summary.vendor_id,
        .candidate_count = summary.candidate_count,
        .matched = summary.matched,
        .matched_rule_index = summary.matched_rule_index,
        .matched_device_any = summary.matched_device_any,
        .matched_vendor_any = summary.matched_vendor_any,
        .disposition = review_disposition,
        .exact_device_match = summary.matched and !summary.matched_device_any,
        .exact_vendor_match = summary.matched and !summary.matched_vendor_any,
    };
}

test "phase10 virtio driver id review keeps exact matches explicit" {
    const summary = try reviewDevice(0x1040, virtio_core.default_vendor_id, 1, &.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
        .{ .device_id = virtio_core.any_id, .vendor_id = virtio_core.any_id },
    });

    try std.testing.expectEqualStrings(anchor_path, summary.anchor);
    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(@as(?usize, 0), summary.matched_rule_index);
    try std.testing.expectEqual(DriverIdMatchDisposition.exact_match, summary.disposition);
    try std.testing.expect(summary.exact_device_match);
    try std.testing.expect(summary.exact_vendor_match);
}

test "phase10 virtio driver id review keeps wildcard matches and misses distinct" {
    var summary = try reviewDevice(0x1052, 0x1AF5, 1, &.{
        .{ .device_id = virtio_core.any_id, .vendor_id = 0x1AF5 },
    });
    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(DriverIdMatchDisposition.device_wildcard_match, summary.disposition);
    try std.testing.expect(!summary.exact_device_match);
    try std.testing.expect(summary.exact_vendor_match);

    summary = try reviewDevice(0x1052, virtio_core.default_vendor_id, 1, &.{
        .{ .device_id = 0x1052, .vendor_id = virtio_core.any_id },
    });
    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(DriverIdMatchDisposition.vendor_wildcard_match, summary.disposition);
    try std.testing.expect(summary.exact_device_match);
    try std.testing.expect(!summary.exact_vendor_match);

    summary = try reviewDevice(0x1052, 0x1AF5, 1, &.{
        .{ .device_id = virtio_core.any_id, .vendor_id = virtio_core.any_id },
    });
    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(DriverIdMatchDisposition.full_wildcard_match, summary.disposition);
    try std.testing.expect(!summary.exact_device_match);
    try std.testing.expect(!summary.exact_vendor_match);

    summary = try reviewDevice(0x1052, 0x1AF5, 1, &.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
    });
    try std.testing.expect(!summary.matched);
    try std.testing.expectEqual(@as(?usize, null), summary.matched_rule_index);
    try std.testing.expectEqual(DriverIdMatchDisposition.no_match, summary.disposition);
}

test "phase10 virtio driver id compatibility helpers preserve the thin replay API" {
    const summary = try reviewDevice(0x1040, virtio_core.default_vendor_id, 1, &.{
        .{ .device_id = virtio_core.any_id, .vendor_id = virtio_core.default_vendor_id },
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
    });
    var core = try virtio_core.VirtioCoreLab.init(0x1040, 1);
    const thin = summarize(&core, &.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
    });

    try std.testing.expectEqual(MatchDisposition.device_any, disposition(.{
        .anchor = summary.anchor,
        .device_id = summary.device_id,
        .vendor_id = summary.vendor_id,
        .candidate_count = summary.candidate_count,
        .matched = true,
        .matched_rule_index = summary.matched_rule_index,
        .matched_device_any = true,
        .matched_vendor_any = false,
    }));
    try std.testing.expectEqual(MatchDisposition.exact, disposition(thin));
    try std.testing.expect(!matchedRuleUsesWildcard(thin));
}

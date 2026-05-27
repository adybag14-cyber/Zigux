const std = @import("std");
const virtio_core = @import("virtio_core");

pub const DriverIdMatchRule = virtio_core.DriverIdMatchRule;
pub const DriverLifecycleBlocker = virtio_core.DriverLifecycleBlocker;

pub const ProbeMatchReviewBlocker = enum {
    device_absent,
    device_needs_reset,
    device_failed,
    probe_state_dirty,
    no_driver_id_match,
    wildcard_driver_id_match,
};

pub const ProbeMatchReviewSummary = struct {
    anchor: []const u8,
    device_id: u32,
    vendor_id: u32,
    queue_count: u16,
    candidate_count: usize,
    matched: bool,
    matched_rule_index: ?usize,
    matched_device_any: bool,
    matched_vendor_any: bool,
    exact_driver_id_match: bool,
    wildcard_match_requires_review: bool,
    probe_preflight_ready: bool,
    remove_review_required: bool,
    reset_cleanup_required: bool,
    blocker: ?ProbeMatchReviewBlocker,
    ready_for_probe_handoff: bool,
    lifecycle_blocker: ?DriverLifecycleBlocker,
    config_generation: u8,
};

pub fn summarizeProbeMatchReview(
    core: *const virtio_core.VirtioCoreLab,
    rules: []const DriverIdMatchRule,
) ProbeMatchReviewSummary {
    const id_summary = core.driverIdMatchSummary(rules);
    const probe_summary = core.probeRemoveDispositionSummary();
    const exact_driver_id_match = id_summary.matched and
        !id_summary.matched_device_any and
        !id_summary.matched_vendor_any;
    const wildcard_match_requires_review = id_summary.matched and !exact_driver_id_match;

    const blocker: ?ProbeMatchReviewBlocker = if (!probe_summary.device_present)
        .device_absent
    else if (probe_summary.failed)
        .device_failed
    else if (probe_summary.needs_reset)
        .device_needs_reset
    else if (!probe_summary.probe_preflight_ready)
        .probe_state_dirty
    else if (!id_summary.matched)
        .no_driver_id_match
    else if (wildcard_match_requires_review)
        .wildcard_driver_id_match
    else
        null;

    return .{
        .anchor = probe_summary.anchor,
        .device_id = id_summary.device_id,
        .vendor_id = id_summary.vendor_id,
        .queue_count = if (probe_summary.device_present) core.queue_count else 0,
        .candidate_count = id_summary.candidate_count,
        .matched = id_summary.matched,
        .matched_rule_index = id_summary.matched_rule_index,
        .matched_device_any = id_summary.matched_device_any,
        .matched_vendor_any = id_summary.matched_vendor_any,
        .exact_driver_id_match = exact_driver_id_match,
        .wildcard_match_requires_review = wildcard_match_requires_review,
        .probe_preflight_ready = probe_summary.probe_preflight_ready,
        .remove_review_required = probe_summary.remove_review_required,
        .reset_cleanup_required = probe_summary.reset_cleanup_required,
        .blocker = blocker,
        .ready_for_probe_handoff = blocker == null,
        .lifecycle_blocker = probe_summary.blocker,
        .config_generation = probe_summary.config_generation,
    };
}

pub fn requiresIdReview(summary: ProbeMatchReviewSummary) bool {
    return summary.wildcard_match_requires_review;
}

pub fn canHandProbeToDriver(summary: ProbeMatchReviewSummary) bool {
    return summary.ready_for_probe_handoff;
}

test "phase10 virtio probe-match review keeps exact id matches ready only when probe state is still clean" {
    var core = try virtio_core.VirtioCoreLab.init(0x1040, 2);

    const summary = summarizeProbeMatchReview(&core, &.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
    });

    try std.testing.expectEqualStrings(virtio_core.anchor_path, summary.anchor);
    try std.testing.expectEqual(@as(u32, 0x1040), summary.device_id);
    try std.testing.expectEqual(@as(u32, virtio_core.default_vendor_id), summary.vendor_id);
    try std.testing.expectEqual(@as(u16, 2), summary.queue_count);
    try std.testing.expect(summary.matched);
    try std.testing.expectEqual(@as(?usize, 0), summary.matched_rule_index);
    try std.testing.expect(summary.exact_driver_id_match);
    try std.testing.expect(!summary.wildcard_match_requires_review);
    try std.testing.expect(summary.probe_preflight_ready);
    try std.testing.expect(!summary.remove_review_required);
    try std.testing.expect(!summary.reset_cleanup_required);
    try std.testing.expectEqual(@as(?ProbeMatchReviewBlocker, null), summary.blocker);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .acknowledge_missing), summary.lifecycle_blocker);
    try std.testing.expect(canHandProbeToDriver(summary));
    try std.testing.expect(!requiresIdReview(summary));
}

test "phase10 virtio probe-match review fences wildcard-only matches behind explicit review" {
    var core = try virtio_core.VirtioCoreLab.init(0x1052, 1);

    const summary = summarizeProbeMatchReview(&core, &.{
        .{ .device_id = virtio_core.any_id, .vendor_id = virtio_core.default_vendor_id },
    });

    try std.testing.expect(summary.matched);
    try std.testing.expect(summary.matched_device_any);
    try std.testing.expect(!summary.matched_vendor_any);
    try std.testing.expect(!summary.exact_driver_id_match);
    try std.testing.expect(summary.wildcard_match_requires_review);
    try std.testing.expect(summary.probe_preflight_ready);
    try std.testing.expectEqual(@as(?ProbeMatchReviewBlocker, .wildcard_driver_id_match), summary.blocker);
    try std.testing.expect(!canHandProbeToDriver(summary));
    try std.testing.expect(requiresIdReview(summary));
}

test "phase10 virtio probe-match review keeps id mismatches from presenting as probe-ready" {
    var core = try virtio_core.VirtioCoreLab.init(0x1052, 1);

    const summary = summarizeProbeMatchReview(&core, &.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
    });

    try std.testing.expect(!summary.matched);
    try std.testing.expect(summary.probe_preflight_ready);
    try std.testing.expectEqual(@as(?ProbeMatchReviewBlocker, .no_driver_id_match), summary.blocker);
    try std.testing.expect(!summary.ready_for_probe_handoff);
}

test "phase10 virtio probe-match review lets dirty probe state override an otherwise exact match" {
    var core = try virtio_core.VirtioCoreLab.init(0x1040, 2);
    core.setStatusBits(virtio_core.status_acknowledge);

    const summary = summarizeProbeMatchReview(&core, &.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
    });

    try std.testing.expect(summary.matched);
    try std.testing.expect(!summary.probe_preflight_ready);
    try std.testing.expect(summary.remove_review_required);
    try std.testing.expect(!summary.reset_cleanup_required);
    try std.testing.expectEqual(@as(?ProbeMatchReviewBlocker, .probe_state_dirty), summary.blocker);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .driver_missing), summary.lifecycle_blocker);
    try std.testing.expect(!summary.ready_for_probe_handoff);
}

test "phase10 virtio probe-match review keeps reset and failed states above match quality" {
    var core = try virtio_core.VirtioCoreLab.init(0x1040, 1);

    core.setStatusBits(virtio_core.status_acknowledge | virtio_core.status_driver);
    core.noteFeaturesNegotiated();
    _ = try core.selectQueue(0);
    core.setStatusBits(virtio_core.status_driver_ok | virtio_core.status_device_needs_reset);

    var summary = summarizeProbeMatchReview(&core, &.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
    });
    try std.testing.expectEqual(@as(?ProbeMatchReviewBlocker, .device_needs_reset), summary.blocker);
    try std.testing.expect(summary.remove_review_required);
    try std.testing.expect(summary.reset_cleanup_required);
    try std.testing.expect(!summary.ready_for_probe_handoff);

    core.setStatusBits(virtio_core.status_failed);
    summary = summarizeProbeMatchReview(&core, &.{
        .{ .device_id = 0x1040, .vendor_id = virtio_core.default_vendor_id },
    });
    try std.testing.expectEqual(@as(?ProbeMatchReviewBlocker, .device_failed), summary.blocker);
    try std.testing.expectEqual(@as(?DriverLifecycleBlocker, .device_failed), summary.lifecycle_blocker);
    try std.testing.expect(!summary.ready_for_probe_handoff);
}

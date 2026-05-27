const std = @import("std");
const virtio_input = @import("virtio_input");

pub const ProbePreflightSummary = virtio_input.ProbePreflightSummary;
pub const ProbePreflightBlocker = virtio_input.ProbePreflightBlocker;

pub fn summarize(device: *const virtio_input.VirtioInputLab) ProbePreflightSummary {
    return device.probePreflightSummary();
}

pub fn blockerTag(blocker: ProbePreflightBlocker) []const u8 {
    return @tagName(blocker);
}

pub fn identityReady(summary: ProbePreflightSummary) bool {
    return summary.identity_ready;
}

pub fn queuePlanReady(summary: ProbePreflightSummary) bool {
    return summary.queue_plan_ready;
}

pub fn deviceReady(summary: ProbePreflightSummary) bool {
    return summary.device_ready;
}

pub fn capabilitySetupReady(summary: ProbePreflightSummary) bool {
    return summary.capability_setup_ready;
}

pub fn multitouchSlotsReady(summary: ProbePreflightSummary) bool {
    return summary.multitouch_slots_ready;
}

pub fn waitingOnIdentity(summary: ProbePreflightSummary) bool {
    return summary.blocker == .identity_incomplete;
}

pub fn waitingOnEventQueue(summary: ProbePreflightSummary) bool {
    return summary.blocker == .event_queue_unconfigured;
}

pub fn waitingOnStatusQueue(summary: ProbePreflightSummary) bool {
    return summary.blocker == .status_queue_unconfigured;
}

pub fn waitingOnEventBuffers(summary: ProbePreflightSummary) bool {
    return summary.blocker == .event_buffers_unfilled;
}

pub fn waitingOnDeviceReady(summary: ProbePreflightSummary) bool {
    return summary.blocker == .device_not_ready;
}

pub fn waitingOnCapabilitySetup(summary: ProbePreflightSummary) bool {
    return summary.blocker == .capability_setup_incomplete;
}

pub fn waitingOnMultitouchSlots(summary: ProbePreflightSummary) bool {
    return summary.blocker == .multitouch_slots_unplanned;
}

pub fn readyForProbeHandoff(summary: ProbePreflightSummary) bool {
    return summary.ready_for_probe_handoff;
}

test "phase10 virtio input probe preflight helper exposes staged blocker predicates through multitouch readiness" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-31", 11, null);

    var summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expectEqualStrings("event_queue_unconfigured", blockerTag(summary.blocker.?));
    try std.testing.expect(identityReady(summary));
    try std.testing.expect(!queuePlanReady(summary));
    try std.testing.expect(!deviceReady(summary));
    try std.testing.expect(!capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(!waitingOnIdentity(summary));
    try std.testing.expect(waitingOnEventQueue(summary));
    try std.testing.expect(!waitingOnStatusQueue(summary));
    try std.testing.expect(!waitingOnEventBuffers(summary));
    try std.testing.expect(!waitingOnDeviceReady(summary));
    try std.testing.expect(!waitingOnCapabilitySetup(summary));
    try std.testing.expect(!waitingOnMultitouchSlots(summary));
    try std.testing.expect(!readyForProbeHandoff(summary));

    try device.configureEventQueue(16);
    summary = summarize(&device);
    try std.testing.expect(identityReady(summary));
    try std.testing.expect(!queuePlanReady(summary));
    try std.testing.expect(waitingOnStatusQueue(summary));

    try device.configureStatusQueue(8);
    summary = summarize(&device);
    try std.testing.expect(identityReady(summary));
    try std.testing.expect(!queuePlanReady(summary));
    try std.testing.expect(waitingOnEventBuffers(summary));

    _ = try device.fillEventBuffers();
    summary = summarize(&device);
    try std.testing.expect(identityReady(summary));
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(!deviceReady(summary));
    try std.testing.expect(waitingOnDeviceReady(summary));

    try device.markReady();
    summary = summarize(&device);
    try std.testing.expect(identityReady(summary));
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(deviceReady(summary));
    try std.testing.expect(!capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(waitingOnCapabilitySetup(summary));

    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 3,
    });

    summary = summarize(&device);
    try std.testing.expect(identityReady(summary));
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(deviceReady(summary));
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(!multitouchSlotsReady(summary));
    try std.testing.expect(!waitingOnCapabilitySetup(summary));
    try std.testing.expect(waitingOnMultitouchSlots(summary));
    try std.testing.expect(!readyForProbeHandoff(summary));

    const slot_plan = try device.planMultitouchSlots();
    try std.testing.expectEqual(@as(u16, 4), slot_plan.planned_slot_count);

    summary = summarize(&device);
    try std.testing.expect(identityReady(summary));
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(deviceReady(summary));
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(readyForProbeHandoff(summary));
}

test "phase10 virtio input probe preflight helper keeps plain-device probe handoff below slot planning" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Tablet Lab", "serial-plain", 12, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();

    var summary = summarize(&device);
    try std.testing.expect(identityReady(summary));
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(deviceReady(summary));
    try std.testing.expect(!capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(waitingOnCapabilitySetup(summary));
    try std.testing.expect(!waitingOnMultitouchSlots(summary));
    try std.testing.expect(!readyForProbeHandoff(summary));

    try device.configureConfigBitmap(.ev_bits, 0x02, &[_]u16{ 0x00, 0x01 });

    summary = summarize(&device);
    try std.testing.expect(identityReady(summary));
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(deviceReady(summary));
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(readyForProbeHandoff(summary));
}

test "phase10 virtio input probe preflight helper keeps identity blockers ahead of registration-ready devices" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Tablet Lab", "serial-identity", 13, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.ev_bits, 0x02, &[_]u16{ 0x00, 0x01 });

    var summary = summarize(&device);
    try std.testing.expect(identityReady(summary));
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(deviceReady(summary));
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(readyForProbeHandoff(summary));

    const saved_name_len = device.name_len;
    device.name_len = 0;

    summary = summarize(&device);
    try std.testing.expect(!identityReady(summary));
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(deviceReady(summary));
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expectEqual(virtio_input.ProbePreflightBlocker.identity_incomplete, summary.blocker.?);
    try std.testing.expect(waitingOnIdentity(summary));
    try std.testing.expect(!readyForProbeHandoff(summary));

    device.name_len = saved_name_len;
    summary = summarize(&device);
    try std.testing.expect(identityReady(summary));
    try std.testing.expect(summary.blocker == null);
    try std.testing.expect(readyForProbeHandoff(summary));
}

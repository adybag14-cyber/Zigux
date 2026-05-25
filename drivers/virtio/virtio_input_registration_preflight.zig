const std = @import("std");
const virtio_input = @import("virtio_input");

pub const RegistrationPreflightSummary = virtio_input.RegistrationPreflightSummary;
pub const RegistrationBlocker = virtio_input.RegistrationBlocker;

pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {
    return device.registrationPreflightSummary();
}

pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {
    return @tagName(blocker);
}

pub fn queuePlanReady(summary: RegistrationPreflightSummary) bool {
    return summary.queue_plan_ready;
}

pub fn capabilitySetupReady(summary: RegistrationPreflightSummary) bool {
    return summary.capability_setup_ready;
}

pub fn multitouchSlotsReady(summary: RegistrationPreflightSummary) bool {
    return summary.multitouch_slots_ready;
}

pub fn waitingOnCapabilitySetup(summary: RegistrationPreflightSummary) bool {
    return summary.blocker == .capability_setup_incomplete;
}

pub fn waitingOnMultitouchSlots(summary: RegistrationPreflightSummary) bool {
    return summary.blocker == .multitouch_slots_unplanned;
}

pub fn readyForRegistration(summary: RegistrationPreflightSummary) bool {
    return summary.ready_for_registration;
}

test "phase10 virtio input registration preflight helper keeps blocker predicates aligned across multitouch bring-up" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Touch Lab", "serial-29", 8, null);

    var summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.event_queue_unconfigured, summary.blocker.?);
    try std.testing.expectEqualStrings("event_queue_unconfigured", blockerTag(summary.blocker.?));
    try std.testing.expect(!queuePlanReady(summary));
    try std.testing.expect(!capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(!waitingOnCapabilitySetup(summary));
    try std.testing.expect(!waitingOnMultitouchSlots(summary));
    try std.testing.expect(!readyForRegistration(summary));

    try device.configureEventQueue(16);
    summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.status_queue_unconfigured, summary.blocker.?);
    try std.testing.expect(!queuePlanReady(summary));

    try device.configureStatusQueue(8);
    summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.event_buffers_unfilled, summary.blocker.?);
    try std.testing.expect(!queuePlanReady(summary));

    _ = try device.fillEventBuffers();
    summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.device_not_ready, summary.blocker.?);
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(!waitingOnCapabilitySetup(summary));

    try device.markReady();
    summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.capability_setup_incomplete, summary.blocker.?);
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(!capabilitySetupReady(summary));
    try std.testing.expect(waitingOnCapabilitySetup(summary));
    try std.testing.expect(!waitingOnMultitouchSlots(summary));

    try device.configureConfigBitmap(.ev_bits, virtio_input.ev_abs, &[_]u16{virtio_input.abs_mt_slot});
    try device.configureAbsInfo(virtio_input.abs_mt_slot, .{
        .minimum = 0,
        .maximum = 3,
    });

    summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.multitouch_slots_unplanned, summary.blocker.?);
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(!multitouchSlotsReady(summary));
    try std.testing.expect(!waitingOnCapabilitySetup(summary));
    try std.testing.expect(waitingOnMultitouchSlots(summary));

    const slot_plan = try device.planMultitouchSlots();
    try std.testing.expectEqual(@as(u16, 4), slot_plan.planned_slot_count);

    summary = summarize(&device);
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(!waitingOnCapabilitySetup(summary));
    try std.testing.expect(!waitingOnMultitouchSlots(summary));
    try std.testing.expectEqual(@as(?virtio_input.RegistrationBlocker, null), summary.blocker);
    try std.testing.expect(readyForRegistration(summary));
}

test "phase10 virtio input registration preflight helper keeps non-multitouch devices registration-ready without slot planning" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Tablet Lab", "serial-plain", 9, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();

    var summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.capability_setup_incomplete, summary.blocker.?);
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(!capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(waitingOnCapabilitySetup(summary));
    try std.testing.expect(!waitingOnMultitouchSlots(summary));
    try std.testing.expect(!readyForRegistration(summary));

    try device.configureConfigBitmap(.ev_bits, 0x02, &[_]u16{ 0x00, 0x01 });

    summary = summarize(&device);
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(!waitingOnCapabilitySetup(summary));
    try std.testing.expect(!waitingOnMultitouchSlots(summary));
    try std.testing.expectEqual(@as(?virtio_input.RegistrationBlocker, null), summary.blocker);
    try std.testing.expect(readyForRegistration(summary));
}

test "phase10 virtio input registration preflight helper revokes registration until capability setup is restored after reset" {
    var device = try virtio_input.VirtioInputLab.init("Virtio Tablet Lab", "serial-reset", 10, null);

    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();
    try device.configureConfigBitmap(.ev_bits, 0x02, &[_]u16{ 0x00, 0x01 });

    var summary = summarize(&device);
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(!waitingOnCapabilitySetup(summary));
    try std.testing.expect(!waitingOnMultitouchSlots(summary));
    try std.testing.expectEqual(@as(?virtio_input.RegistrationBlocker, null), summary.blocker);
    try std.testing.expect(readyForRegistration(summary));

    device.reset();
    try device.configureEventQueue(8);
    try device.configureStatusQueue(4);
    _ = try device.fillEventBuffers();
    try device.markReady();

    summary = summarize(&device);
    try std.testing.expectEqual(virtio_input.RegistrationBlocker.capability_setup_incomplete, summary.blocker.?);
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(!capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(waitingOnCapabilitySetup(summary));
    try std.testing.expect(!waitingOnMultitouchSlots(summary));
    try std.testing.expect(!readyForRegistration(summary));

    try device.configureConfigBitmap(.ev_bits, 0x02, &[_]u16{ 0x00, 0x01 });

    summary = summarize(&device);
    try std.testing.expect(queuePlanReady(summary));
    try std.testing.expect(summary.device_ready);
    try std.testing.expect(capabilitySetupReady(summary));
    try std.testing.expect(multitouchSlotsReady(summary));
    try std.testing.expect(!waitingOnCapabilitySetup(summary));
    try std.testing.expect(!waitingOnMultitouchSlots(summary));
    try std.testing.expectEqual(@as(?virtio_input.RegistrationBlocker, null), summary.blocker);
    try std.testing.expect(readyForRegistration(summary));
}

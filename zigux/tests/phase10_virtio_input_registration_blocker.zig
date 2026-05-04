const std = @import("std");
const registration_blocker = @import("../../drivers/virtio/virtio_input_registration_blocker.zig");

test "phase10 virtio input registration blocker keeps risky lifecycle claims parked after probe readiness converges" {
    var summary = registration_blocker.summarize(.{
        .registration_preflight_ready = false,
        .queue_callback_ready = false,
        .probe_handoff_ready = false,
    });

    try std.testing.expectEqualStrings("drivers/virtio/virtio_input.c", summary.anchor);
    try std.testing.expect(!summary.registration_preflight_ready);
    try std.testing.expect(!summary.queue_callback_ready);
    try std.testing.expect(!summary.probe_handoff_ready);
    try std.testing.expect(summary.input_registration_lifecycle_blocked);
    try std.testing.expect(summary.transport_queue_callbacks_blocked);
    try std.testing.expect(summary.freeze_restore_blocked);
    try std.testing.expect(summary.probe_remove_blocked);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", summary.risky_transport_posture);

    summary = registration_blocker.summarize(.{
        .registration_preflight_ready = true,
        .queue_callback_ready = true,
        .probe_handoff_ready = true,
    });

    try std.testing.expect(summary.registration_preflight_ready);
    try std.testing.expect(summary.queue_callback_ready);
    try std.testing.expect(summary.probe_handoff_ready);
    try std.testing.expect(summary.input_registration_lifecycle_blocked);
    try std.testing.expect(summary.transport_queue_callbacks_blocked);
    try std.testing.expect(summary.freeze_restore_blocked);
    try std.testing.expect(summary.probe_remove_blocked);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", summary.risky_transport_posture);
}

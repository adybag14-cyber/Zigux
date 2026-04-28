const std = @import("std");

const SurveySummary = struct {
    virtio_ring_c_lines: usize,
    preexisting_phase10_test_files: usize,
    preexisting_virtio_core_zig_present: bool,
    preexisting_phase10_build_present: bool,
    preexisting_phase10_core_doc_present: bool,
    preexisting_virtio_ring_zig_present: bool,
    preexisting_virtio_ring_doc_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_risky_transport");
}

test "phase10 virtio ring survey manifest records the live queue-reset and MMIO follow-up ladder" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase10_virtio_ring_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P10-L07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 10", manifest.phase);
    try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.c", manifest.anchor);
    try std.testing.expectEqualStrings("60bf9d6537457e95f3dad1d89c6033c031def374", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.virtio_ring_c_lines >= 3000);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_core_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase10_core_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_ring_doc_present);
    try std.testing.expect(manifest.gaps.len >= 7);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_ring_helper = false;
    var saw_used_buffer_polling = false;
    var saw_callback_disable_helper = false;
    var saw_callback_enable_helper = false;
    var saw_callback_delay_helper = false;
    var saw_notify_prepare_helper = false;
    var saw_queue_reset_helper = false;
    var saw_mmio_register_window = false;
    var saw_mmio_queue_register = false;
    var saw_mmio_blocker = false;
    var saw_ring_slice_note = false;
    var saw_core_progress_note = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_risky_transport")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtqueue-shape-helper")) {
            saw_ring_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase10-used-buffer-polling-helper")) {
            saw_used_buffer_polling = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "newly consumed chains") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-callback-disable-helper")) {
            saw_callback_disable_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "callback disable helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "follow-up poll") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-callback-enable-helper")) {
            saw_callback_enable_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "follow-up poll") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-callback-delay-helper")) {
            saw_callback_delay_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "delayed-callback pacing") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-notify-prepare-helper")) {
            saw_notify_prepare_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notify-prepare helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "virtqueue_kick_prepare()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "num_added") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-queue-reset-helper")) {
            saw_queue_reset_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_ring.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue reset helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "registered queue shape") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reset path") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-core-lab-starter")) {
            saw_core_progress_note = true;
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "descriptor-shape metadata") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notification accounting") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-register-window-helper")) {
            saw_mmio_register_window = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "register-window helper") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-queue-register-helper")) {
            saw_mmio_queue_register = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "queue select") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ready-state bookkeeping") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-mmio-lifecycle-and-irq-paths")) {
            saw_mmio_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_risky_transport", gap.status);
            try std.testing.expectEqualStrings("drivers/virtio/virtio_mmio.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "interrupt acknowledgement") != null or std.mem.indexOf(u8, gap.why_now, "lifecycle") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase10-virtio-ring-slice-note")) {
            saw_ring_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase10-virtio-ring-slice.md", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expect(starter_landed_count >= 5);
    try std.testing.expect(ready_next_count >= 1);
    try std.testing.expect(blocked_count >= 1);
    try std.testing.expect(saw_core_progress_note);
    try std.testing.expect(saw_ring_helper);
    try std.testing.expect(saw_used_buffer_polling);
    try std.testing.expect(saw_callback_disable_helper);
    try std.testing.expect(saw_callback_enable_helper);
    try std.testing.expect(saw_callback_delay_helper);
    try std.testing.expect(saw_notify_prepare_helper);
    try std.testing.expect(saw_queue_reset_helper);
    try std.testing.expect(saw_mmio_register_window);
    try std.testing.expect(saw_mmio_queue_register);
    try std.testing.expect(saw_ring_slice_note);
    try std.testing.expect(saw_mmio_blocker);
}

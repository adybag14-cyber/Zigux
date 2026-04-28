const std = @import("std");

const SurveySummary = struct {
    bcm2835_wdt_c_lines: usize,
    preexisting_phase11_build_present: bool,
    preexisting_phase11_gpio_lane_present: bool,
    bcm2835_wdt_zig_present: bool,
    bcm2835_wdt_test_present: bool,
    bcm2835_wdt_slice_note_present: bool,
    bcm2835_wdt_validation_matrix_present: bool,
    bcm2835_wdt_platform_handoff_present: bool,
    bcm2835_wdt_shared_replay_evidence_present: bool,
    bcm2835_wdt_survey_gate_present: bool,
    bcm2835_wdt_survey_note_present: bool,
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
        std.mem.eql(u8, status, "blocked_on_driver_scaffold");
}

test "phase11 bcm2835_wdt survey manifest and validation matrix record the landed handoff summary plus replay surface" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_bcm2835_wdt_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const matrix_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(matrix_doc);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P11-L05", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", manifest.anchor);
    try std.testing.expectEqualStrings("53adda107fb76e2329b5458faf8c515fc5a077a4", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_c_lines >= 240);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_gpio_lane_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_zig_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_slice_note_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_validation_matrix_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_platform_handoff_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_shared_replay_evidence_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_survey_note_present);
    try std.testing.expectEqual(@as(usize, 12), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "PHASE11_BCM2835_WDT_STATUS=platform_handoff_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "## Shared Replay Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-bcm2835-wdt-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-bcm2835-wdt-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig build test --build-file zigux/tests/phase11_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig test zigux/tests/phase11_bcm2835_wdt_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "full platform registration") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "PM base ioremap") != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_driver_gap = false;
    var saw_driver_tests = false;
    var saw_slice_note = false;
    var saw_validation_matrix = false;
    var saw_probe_summary = false;
    var saw_registration_summary = false;
    var saw_platform_handoff = false;
    var saw_remove_followup = false;
    var saw_live_platform_gap = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_driver_scaffold")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase11-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_build.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_bcm2835_wdt_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "validation matrix status") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-driver-starter")) {
            saw_driver_gap = true;
            try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "registration-facing handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-registration and PM-base handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time ownership summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-driver-tests")) {
            saw_driver_tests = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-handoff prerequisites") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time poweroff ownership outcomes") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-bcm2835-wdt-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time ownership summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-validation-matrix")) {
            saw_validation_matrix = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 11 test gate") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landed platform-handoff review surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "replay commands") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-probe-summary")) {
            saw_probe_summary = true;
            try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bootloader-carried running state") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "stop-on-reboot") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-registration-and-poweroff")) {
            saw_registration_summary = true;
            try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "registration-facing handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "poweroff claim-vs-conflict") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-platform-registration")) {
            saw_platform_handoff = true;
            try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-registration and PM-base handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "register-device intent") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-remove-summary")) {
            saw_remove_followup = true;
            try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time ownership summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "currently owns it") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-live-platform-registration")) {
            saw_live_platform_gap = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_driver_scaffold", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hardware-validation plan") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "PM base plumbing") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 11), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_driver_gap);
    try std.testing.expect(saw_driver_tests);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_validation_matrix);
    try std.testing.expect(saw_probe_summary);
    try std.testing.expect(saw_registration_summary);
    try std.testing.expect(saw_platform_handoff);
    try std.testing.expect(saw_remove_followup);
    try std.testing.expect(saw_live_platform_gap);
}

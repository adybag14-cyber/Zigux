const std = @import("std");

const SurveySummary = struct {
    bcm2835_wdt_c_lines: usize,
    preexisting_phase11_build_present: bool,
    preexisting_phase11_gpio_lane_present: bool,
    bcm2835_wdt_zig_present: bool,
    bcm2835_wdt_test_present: bool,
    bcm2835_wdt_slice_note_present: bool,
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

test "phase11 bcm2835_wdt survey manifest records the landed get-timeleft summary and remaining platform gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_bcm2835_wdt_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const driver_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/watchdog/bcm2835_wdt.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(driver_source);

    const driver_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_bcm2835_wdt.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(driver_tests);

    const shared_phase11_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(shared_phase11_build);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P11-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 40), manifest.surveyed_commit.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_c_lines >= 240);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_gpio_lane_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_zig_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_slice_note_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_survey_note_present);
    try std.testing.expectEqual(@as(usize, 10), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub fn registrationSummary(") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub fn getTimeleft(") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub fn removeSummary(") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "clear_poweroff_handler_requested") != null);

    try std.testing.expect(std.mem.indexOf(u8, driver_tests, "phase11 bcm2835_wdt registration summary records watchdog registration and poweroff ownership outcomes") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_tests, "phase11 bcm2835_wdt remove summary only clears the shared poweroff handler when bcm2835 owns it") != null);

    try std.testing.expect(std.mem.indexOf(u8, shared_phase11_build, "phase11-bcm2835-wdt-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, shared_phase11_build, "phase11-bcm2835-wdt-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, shared_phase11_build, "../../drivers/watchdog/bcm2835_wdt.zig") != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_driver_gap = false;
    var saw_driver_tests = false;
    var saw_slice_note = false;
    var saw_probe_summary = false;
    var saw_registration_summary = false;
    var saw_get_timeleft_summary = false;
    var saw_registration_blocker = false;

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
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-driver-starter")) {
            saw_driver_gap = true;
            try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "registration-facing handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "poweroff ownership summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "explicit get-timeleft helper") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-driver-tests")) {
            saw_driver_tests = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "direct get-timeleft parity") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-bcm2835-wdt-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "explicit get-timeleft helper") != null);
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

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-get-timeleft")) {
            saw_get_timeleft_summary = true;
            try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "explicit get-timeleft helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "WDOG_TICKS_TO_SECS") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-platform-registration")) {
            saw_registration_blocker = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_driver_scaffold", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Platform registration") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hardware-validation matrix") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 9), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_driver_gap);
    try std.testing.expect(saw_driver_tests);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_probe_summary);
    try std.testing.expect(saw_registration_summary);
    try std.testing.expect(saw_get_timeleft_summary);
    try std.testing.expect(saw_registration_blocker);
}

test "phase11 bcm2835_wdt survey docs keep the landed validation matrix and next handoff step explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-bcm2835-wdt-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const validation_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(validation_matrix);

    try std.testing.expect(std.mem.indexOf(u8, slice_note, "hardware-validation matrix now records that bounded validation posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "tiny platform-facing handoff note") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "explicit get-timeleft helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "add a tiny hardware-validation matrix") == null);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase11-bcm2835-wdt-validation-matrix.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "hardware validation coverage beyond the bounded matrix") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "focused survey gate now reads the live driver, dedicated test, and shared Phase 11 build packet directly") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "tiny platform-facing handoff note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "explicit get-timeleft helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "add a tiny hardware-validation matrix") == null);

    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "PHASE11_BCM2835_WDT_STATUS=hardware_validation_matrix_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "explicit get-timeleft helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "current validation posture in one place") != null);
}

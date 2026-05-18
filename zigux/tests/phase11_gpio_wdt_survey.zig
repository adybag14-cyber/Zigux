const std = @import("std");

const SurveySummary = struct {
    gpio_wdt_c_lines: usize,
    preexisting_phase11_test_files: usize,
    preexisting_phase11_build_present: bool,
    preexisting_gpio_wdt_zig_present: bool,
    preexisting_gpio_wdt_test_present: bool,
    preexisting_phase11_survey_note_present: bool,
    preexisting_phase11_module_note_present: bool,
    preexisting_phase11_validation_matrix_present: bool,
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
        std.mem.eql(u8, status, "blocked_on_driver_scaffold");
}

test "phase11 gpio_wdt survey manifest records the refreshed starter state and remaining gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_gpio_wdt_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P11-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", manifest.anchor);
    try std.testing.expectEqualStrings("41ee426b91cf612f2d7a5ef5e4754109fc8b6e16", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.gpio_wdt_c_lines >= 190);
    try std.testing.expectEqual(@as(usize, 2), manifest.survey_summary.preexisting_phase11_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_gpio_wdt_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_gpio_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_module_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_validation_matrix_present);
    try std.testing.expectEqual(@as(usize, 15), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_driver_gap = false;
    var saw_build_gate = false;
    var saw_doc_gate = false;
    var saw_test_gate = false;
    var saw_slice_note = false;
    var saw_teardown_note = false;
    var saw_validation_matrix = false;
    var saw_stop_followup = false;
    var saw_handoff_followup = false;
    var saw_descriptor_preflight = false;
    var saw_timeout_checkpoint = false;
    var saw_drvdata_checkpoint = false;
    var saw_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_driver_scaffold")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase11-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_build.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-survey-note")) {
            saw_doc_gate = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-gpio-wdt-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "failure-mode parity") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-driver-starter")) {
            saw_driver_gap = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hw_algo") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "heartbeat margin") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-driver-tests")) {
            saw_test_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-gpio-wdt-module-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-teardown-note")) {
            saw_teardown_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-gpio-wdt-teardown-note.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "drvdata ownership checkpoint") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-validation-matrix")) {
            saw_validation_matrix = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-gpio-wdt-validation-matrix.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "validation posture") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-probe-summary-followup")) {
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "gpio_wdt_probe()") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-nowayout-followup")) {
            saw_stop_followup = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog-core stop") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-registration-handoff-followup")) {
            saw_handoff_followup = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "registration-facing handoff") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-descriptor-preflight")) {
            saw_descriptor_preflight = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm_gpiod_get()") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-timeout-property-checkpoint")) {
            saw_timeout_checkpoint = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`hw_margin_ms`") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-drvdata-ownership-checkpoint")) {
            saw_drvdata_checkpoint = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "drvdata ownership checkpoint") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-platform-registration")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_driver_scaffold", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog core registration") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "failure-mode") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 14), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_doc_gate);
    try std.testing.expect(saw_driver_gap);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_teardown_note);
    try std.testing.expect(saw_validation_matrix);
    try std.testing.expect(saw_stop_followup);
    try std.testing.expect(saw_handoff_followup);
    try std.testing.expect(saw_descriptor_preflight);
    try std.testing.expect(saw_timeout_checkpoint);
    try std.testing.expect(saw_drvdata_checkpoint);
    try std.testing.expect(saw_blocker);
}

test "phase11 gpio_wdt survey note and validation matrix stay aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-gpio-wdt-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const validation_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(validation_matrix);

    const teardown_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-gpio-wdt-teardown-note.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(teardown_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase11-gpio-wdt-validation-matrix.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase11-gpio-wdt-teardown-note.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "descriptorPreflightSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "timeoutPropertyCheckpointSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drvdataOwnershipCheckpointSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "failure-mode parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "live GPIO descriptor lookup") != null);

    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "PHASE11_GPIO_WDT_STATUS=hardware_validation_matrix_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "phase11-gpio-wdt-teardown-note.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "descriptorPreflightSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "timeoutPropertyCheckpointSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "drvdataOwnershipCheckpointSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "phase11_gpio_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "teardown-facing handoff note") != null);

    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "requestStop()") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "drvdataOwnershipCheckpointSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "registrationHandoffSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "live reboot-hook, remove-hook, or shutdown execution") != null);
}

test "phase11 gpio_wdt module-slice note stays wired into the review packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const module_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-gpio-wdt-module-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(module_slice);

    const validation_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(validation_matrix);

    try std.testing.expect(std.mem.indexOf(u8, module_slice, "gpio_wdt_lab") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "descriptorPreflightSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "timeoutPropertyCheckpointSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "drvdataOwnershipCheckpointSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "phase11-gpio-wdt-teardown-note.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "platform-driver registration") != null);

    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "Documentation/zigux/phase11-gpio-wdt-module-slice.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "the module-slice note") != null);
}

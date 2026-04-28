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

    const matrix_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(matrix_doc);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P11-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", manifest.anchor);
    try std.testing.expectEqualStrings("0d1e336cf006e5477fc18df7df0f91520aebd647", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.gpio_wdt_c_lines >= 190);
    try std.testing.expectEqual(@as(usize, 2), manifest.survey_summary.preexisting_phase11_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_gpio_wdt_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_gpio_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_module_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_validation_matrix_present);
    try std.testing.expectEqual(@as(usize, 12), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "PHASE11_GPIO_WDT_STATUS=registration_preflight_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "## Shared Replay Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-gpio-wdt-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-gpio-wdt-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig build test --build-file zigux/tests/phase11_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig test zigux/tests/phase11_gpio_wdt_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "descriptor-facing registration handoff") != null);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_driver_gap = false;
    var saw_build_gate = false;
    var saw_doc_gate = false;
    var saw_test_gate = false;
    var saw_slice_note = false;
    var saw_validation_matrix = false;
    var saw_stop_followup = false;
    var saw_handoff_followup = false;
    var saw_plan_followup = false;
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
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-gpio-wdt-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-validation-matrix")) {
            saw_validation_matrix = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-gpio-wdt-validation-matrix.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 11 replay path") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "metadata-only registration handoff surface") != null);
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

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-registration-plan-followup")) {
            saw_plan_followup = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "registration surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "validation focus") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-platform-registration")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_driver_scaffold", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog core registration") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 11), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_doc_gate);
    try std.testing.expect(saw_driver_gap);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_validation_matrix);
    try std.testing.expect(saw_stop_followup);
    try std.testing.expect(saw_handoff_followup);
    try std.testing.expect(saw_plan_followup);
    try std.testing.expect(saw_blocker);
}

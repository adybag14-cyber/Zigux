const std = @import("std");

const SurveySummary = struct {
    dw_wdt_c_lines: usize,
    preexisting_phase11_build_present: bool,
    preexisting_phase11_gpio_lane_present: bool,
    preexisting_phase11_bcm2835_lane_present: bool,
    dw_wdt_zig_present: bool,
    dw_wdt_test_present: bool,
    dw_wdt_registration_scaffold_present: bool,
    dw_wdt_registration_order_present: bool,
    dw_wdt_slice_note_present: bool,
    dw_wdt_survey_gate_present: bool,
    dw_wdt_survey_note_present: bool,
    dw_wdt_pm_helper_present: bool,
    dw_wdt_restart_helper_present: bool,
    dw_wdt_verify_helper_present: bool,
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
        std.mem.eql(u8, status, "shared_gap_current_head");
}

fn loadFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

test "phase11 dw_wdt manifest records the current P11-L10 packet truth" {
    const allocator = std.testing.allocator;
    const manifest_json = try loadFile(
        allocator,
        "zigux/tests/phase11_dw_wdt_manifest.json",
        32 * 1024,
    );
    defer allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P11-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("75f8336c4305beed127d7abfae37d3999b7cc57c", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);

    try std.testing.expect(manifest.survey_summary.dw_wdt_c_lines >= 700);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_gpio_lane_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_bcm2835_lane_present);
    try std.testing.expect(!manifest.survey_summary.dw_wdt_zig_present);
    try std.testing.expect(!manifest.survey_summary.dw_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_registration_scaffold_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_registration_order_present);
    try std.testing.expect(!manifest.survey_summary.dw_wdt_slice_note_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_note_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_pm_helper_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_restart_helper_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_verify_helper_present);
    try std.testing.expectEqual(@as(usize, 14), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var shared_gap_count: usize = 0;

    var saw_build_gate = false;
    var saw_platform_scaffold = false;
    var saw_pm_helper = false;
    var saw_verify_helper = false;
    var saw_mmio_ready_next = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "shared_gap_current_head")) {
            shared_gap_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase11-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("shared_gap_current_head", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase11_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-platform-registration-scaffold")) {
            saw_platform_scaffold = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-teardown-parity")) {
            saw_verify_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt_verify.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-live-platform-pm")) {
            saw_pm_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt_pm.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-live-mmio-validation")) {
            saw_mmio_ready_next = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt.zig", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 12), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), shared_gap_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_platform_scaffold);
    try std.testing.expect(saw_pm_helper);
    try std.testing.expect(saw_verify_helper);
    try std.testing.expect(saw_mmio_ready_next);
}

test "phase11 dw_wdt survey note and validation matrix stay aligned" {
    const allocator = std.testing.allocator;

    const survey_note = try loadFile(
        allocator,
        "Documentation/zigux/phase11-dw-wdt-survey.md",
        16 * 1024,
    );
    defer allocator.free(survey_note);

    const validation_matrix = try loadFile(
        allocator,
        "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
        16 * 1024,
    );
    defer allocator.free(validation_matrix);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`P11-L10`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`P11-L05`") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared current-head") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "hardware-backed MMIO validation") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/watchdog/dw_wdt_pm.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/watchdog/dw_wdt_verify.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "`P11-L10`") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "`P11-L05`") == null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "`PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "shared current-head") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "drivers/watchdog/dw_wdt_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "drivers/watchdog/dw_wdt_pm.zig") != null);
}

test "phase11 dw_wdt clock acquisition plan stays aligned with the returned packet" {
    const allocator = std.testing.allocator;

    const clock_plan = try loadFile(
        allocator,
        "Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md",
        16 * 1024,
    );
    defer allocator.free(clock_plan);

    try std.testing.expect(std.mem.indexOf(u8, clock_plan, "drivers/watchdog/dw_wdt_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, clock_plan, "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, clock_plan, "optional reset-control absence can still remain a ready-to-register scaffold branch") != null);
    try std.testing.expect(std.mem.indexOf(u8, clock_plan, "broader direct driver, driver-test, slice, and teardown-note stack stays outside this direct contents bridge") != null);
}

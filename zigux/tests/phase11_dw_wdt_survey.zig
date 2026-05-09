const std = @import("std");

const SurveySummary = struct {
    dw_wdt_c_lines: usize,
    preexisting_phase11_build_present: bool,
    preexisting_phase11_gpio_lane_present: bool,
    preexisting_phase11_bcm2835_lane_present: bool,
    dw_wdt_zig_present: bool,
    dw_wdt_test_present: bool,
    dw_wdt_resource_preflight_present: bool,
    dw_wdt_registration_scaffold_present: bool,
    dw_wdt_registration_order_present: bool,
    dw_wdt_slice_note_present: bool,
    dw_wdt_survey_gate_present: bool,
    dw_wdt_survey_note_present: bool,
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

test "phase11 dw_wdt survey manifest records the landed registration handoff and remaining platform gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_dw_wdt_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P11-L12", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", manifest.anchor);
    try std.testing.expectEqualStrings("75f8336c4305beed127d7abfae37d3999b7cc57c", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.dw_wdt_c_lines >= 700);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_gpio_lane_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_bcm2835_lane_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_zig_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_resource_preflight_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_registration_scaffold_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_registration_order_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_slice_note_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_note_present);
    try std.testing.expectEqual(@as(usize, 13), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_driver_gap = false;
    var saw_resource_preflight = false;
    var saw_driver_tests = false;
    var saw_slice_note = false;
    var saw_platform_scaffold = false;
    var saw_live_platform_next = false;
    var saw_probe_summary = false;
    var saw_registration_gap = false;
    var saw_registration_order_scaffold = false;
    var saw_teardown_parity = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) starter_landed_count += 1
        else if (std.mem.eql(u8, gap.status, "ready_next")) ready_next_count += 1
        else if (std.mem.eql(u8, gap.status, "blocked_on_driver_scaffold")) blocked_count += 1;

        if (std.mem.eql(u8, gap.id, "phase11-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_build.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown-parity replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-resource preflight") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bounded platform-registration scaffold") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-driver-starter")) {
            saw_driver_gap = true;
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fixed TOP timeout windows") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe-time summary") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-platform-resource-preflight")) {
            saw_resource_preflight = true;
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared-clock fallback") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "blocked-no-timer-clock") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pretimeout-IRQ") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-driver-tests")) {
            saw_driver_tests = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-resource preflight choices") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "registration-facing handoff outputs") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-dw-wdt-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-probe-summary")) {
            saw_probe_summary = true;
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fixed-versus-custom TOP sourcing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "already-running watchdog state") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-registration-handoff")) {
            saw_registration_gap = true;
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog info selection") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "timeout-programming intent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "register-device handoff") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-registration-order-scaffold")) {
            saw_registration_order_scaffold = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt_registration_scaffold.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "timer-clock path choice") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "register-device request ordering") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-teardown-parity")) {
            saw_teardown_parity = true;
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt_verify.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown and failure-mode parity") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "unstoppable hardware") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "idle remove without a fabricated heartbeat") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "idle remove with reset-backed quiesce") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "idle stop outcomes across reset-controlled and non-stoppable hardware") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "idle IRQ-configured teardown without a fabricated stop path or continued heartbeat") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "IRQ-mode teardown outcomes") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-platform-registration-scaffold")) {
            saw_platform_scaffold = true;
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-resource preflight") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-registration scaffold") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "module_platform_driver") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dw_wdt_drv_probe") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-live-platform-pm")) {
            saw_live_platform_next = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "suspend and resume handling") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hardware-backed MMIO validation") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "real platform-backed probe or remove execution slice") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 12), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 0), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_driver_gap);
    try std.testing.expect(saw_resource_preflight);
    try std.testing.expect(saw_driver_tests);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_probe_summary);
    try std.testing.expect(saw_registration_gap);
    try std.testing.expect(saw_registration_order_scaffold);
    try std.testing.expect(saw_teardown_parity);
    try std.testing.expect(saw_platform_scaffold);
    try std.testing.expect(saw_live_platform_next);
}

test "phase11 dw_wdt survey note, slice note, validation matrix, and teardown note stay aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "Documentation/zigux/phase11-dw-wdt-survey.md", std.testing.allocator, .limited(32 * 1024));
    defer std.testing.allocator.free(survey_note);
    const validation_matrix = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "Documentation/zigux/phase11-dw-wdt-validation-matrix.md", std.testing.allocator, .limited(64 * 1024));
    defer std.testing.allocator.free(validation_matrix);
    const slice_note = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "Documentation/zigux/phase11-dw-wdt-slice.md", std.testing.allocator, .limited(16 * 1024));
    defer std.testing.allocator.free(slice_note);
    const teardown_note = try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), "Documentation/zigux/phase11-dw-wdt-teardown-note.md", std.testing.allocator, .limited(16 * 1024));
    defer std.testing.allocator.free(teardown_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase11-dw-wdt-validation-matrix.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase11-dw-wdt-teardown-note.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "bounded hardware-validation posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "teardown and failure-mode parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "platform-resource preflight summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared-clock fallback") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "platform-registration scaffold") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "module_platform_driver") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "dw_wdt_drv_shutdown") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "watchdog_register_device") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase11-dw-wdt-registration-scaffold-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase11_dw_wdt_registration_scaffold.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "register-device request ordering") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase11-dw-wdt-verify-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/watchdog/dw_wdt_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "stop, remove, and shutdown ownership split") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`P11-L12`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`P11-L05`") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`P11-L10`") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`P11-L11`") == null);

    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "platform registration scaffold") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "module_platform_driver") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "watchdog_register_device") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "phase11_dw_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "phase11-dw-wdt-verify-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "drivers/watchdog/dw_wdt_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "phase11-dw-wdt-teardown-note.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "`P11-L12`") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "`P11-L05`") == null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "`P11-L10`") == null);

    try std.testing.expect(std.mem.indexOf(u8, slice_note, "fixed-versus-custom TOP sourcing") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "watchdog_register_device") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "platform-resource preflight summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "named `tclk` versus shared-clock fallback") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "platform-registration scaffold summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "module_platform_driver") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "phase11-dw-wdt-validation-matrix.md") != null);

    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "drivers/watchdog/dw_wdt_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "phase11-dw-wdt-validation-matrix.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "continued-heartbeat") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "idle remove-time no-fabricated-heartbeat") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "reset-backed quiesce") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "removeSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "teardownSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "platformRegistrationScaffoldSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "dw_wdt_drv_shutdown") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "phase11_dw_wdt_registration_scaffold.zig") != null);
}

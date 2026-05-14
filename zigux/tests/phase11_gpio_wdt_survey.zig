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
    preexisting_phase11_shared_replay_evidence_present: bool,
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

fn readFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

fn findGap(manifest: Manifest, id: []const u8) ?Gap {
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

test "phase11 gpio_wdt archived survey gate keeps the visible starter and missing replay packet honest" {
    const manifest_json = try readFile(std.testing.allocator, "zigux/tests/phase11_gpio_wdt_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P11-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.gpio_wdt_c_lines >= 190);
    try std.testing.expectEqual(@as(usize, 2), manifest.survey_summary.preexisting_phase11_test_files);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_gpio_wdt_zig_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_gpio_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_module_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_validation_matrix_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase11_shared_replay_evidence_present);

    const survey_gate = findGap(manifest, "phase11-gpio-wdt-survey-gate") orelse return error.MissingSurveyGateGap;
    try std.testing.expectEqualStrings("starter_landed", survey_gate.status);
    try std.testing.expectEqualStrings("zigux/tests/phase11_gpio_wdt_survey.zig", survey_gate.zigux_destination);
    try std.testing.expect(std.mem.indexOf(u8, survey_gate.why_now, "visible starter") != null);

    const build_gate = findGap(manifest, "phase11-build-gate") orelse return error.MissingBuildGateGap;
    try std.testing.expectEqualStrings("blocked_on_driver_scaffold", build_gate.status);
    try std.testing.expectEqualStrings("zigux/tests/phase11_build.zig", build_gate.zigux_destination);

    const driver_gap = findGap(manifest, "phase11-gpio-wdt-driver-starter") orelse return error.MissingDriverGap;
    try std.testing.expectEqualStrings("starter_landed", driver_gap.status);
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", driver_gap.zigux_destination);
    try std.testing.expect(std.mem.indexOf(u8, driver_gap.why_now, "exposes the bounded gpio_wdt starter") != null);

    const test_gap = findGap(manifest, "phase11-gpio-wdt-driver-tests") orelse return error.MissingDriverTestGap;
    try std.testing.expectEqualStrings("blocked_on_driver_scaffold", test_gap.status);
    try std.testing.expectEqualStrings("zigux/tests/phase11_gpio_wdt.zig", test_gap.zigux_destination);

    const survey_note_gap = findGap(manifest, "phase11-gpio-wdt-survey-note") orelse return error.MissingSurveyNoteGap;
    try std.testing.expectEqualStrings("starter_landed", survey_note_gap.status);
    try std.testing.expect(std.mem.indexOf(u8, survey_note_gap.why_now, "now exposes `drivers/watchdog/gpio_wdt.zig` again") != null);

    const matrix_gap = findGap(manifest, "phase11-gpio-wdt-validation-matrix") orelse return error.MissingMatrixGap;
    try std.testing.expectEqualStrings("starter_landed", matrix_gap.status);
    try std.testing.expect(std.mem.indexOf(u8, matrix_gap.why_now, "visible starter") != null);

    const drvdata_gap = findGap(manifest, "phase11-gpio-wdt-platform-drvdata-tests") orelse return error.MissingDrvdataGap;
    try std.testing.expectEqualStrings("starter_landed", drvdata_gap.status);
    try std.testing.expectEqualStrings("zigux/tests/phase11_gpio_wdt_platform_drvdata.zig", drvdata_gap.zigux_destination);

    const archived_drvdata_gap = findGap(manifest, "phase11-gpio-wdt-drvdata-checkpoint") orelse return error.MissingArchivedDrvdataGap;
    try std.testing.expectEqualStrings("note_only_archived", archived_drvdata_gap.status);

    const archived_reboot_gap = findGap(manifest, "phase11-gpio-wdt-reboot-glue-checkpoint") orelse return error.MissingArchivedRebootGap;
    try std.testing.expectEqualStrings("note_only_archived", archived_reboot_gap.status);

    const blocker = findGap(manifest, "phase11-gpio-wdt-platform-registration") orelse return error.MissingPlatformRegistrationGap;
    try std.testing.expectEqualStrings("blocked_on_driver_scaffold", blocker.status);
    try std.testing.expect(std.mem.indexOf(u8, blocker.why_now, "hardware-backed validation") != null);
}

test "phase11 gpio_wdt archived notes stay aligned with the visible starter and the missing replay boundary" {
    const survey_note = try readFile(std.testing.allocator, "Documentation/zigux/phase11-gpio-wdt-survey.md", 32 * 1024);
    defer std.testing.allocator.free(survey_note);

    const validation_matrix = try readFile(std.testing.allocator, "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md", 64 * 1024);
    defer std.testing.allocator.free(validation_matrix);

    const module_slice = try readFile(std.testing.allocator, "Documentation/zigux/phase11-gpio-wdt-module-slice.md", 32 * 1024);
    defer std.testing.allocator.free(module_slice);

    const teardown_note = try readFile(std.testing.allocator, "Documentation/zigux/phase11-gpio-wdt-teardown-note.md", 32 * 1024);
    defer std.testing.allocator.free(teardown_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/watchdog/gpio_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase11_gpio_wdt_platform_drvdata.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase11_gpio_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase11_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "do not expose `drivers/watchdog/gpio_wdt.zig`") == null);

    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "drivers/watchdog/gpio_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "zigux/tests/phase11_gpio_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "zigux/tests/phase11_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "registerDeviceFailureSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "summarizeTeardown()") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "do not expose `drivers/watchdog/gpio_wdt.zig`") == null);

    try std.testing.expect(std.mem.indexOf(u8, module_slice, "descriptorRequestSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "platformDrvdataCheckpointSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "nowayoutPolicySummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "probeSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "registrationHandoffSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "registrationPlanSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "registerDeviceCallSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "registerDeviceFailureSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "summarizeTeardown()") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "timeoutPropertyCheckpointSummary()") == null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "drvdataCheckpointSummary()") == null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice, "rebootGlueCheckpointSummary()") == null);

    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "drivers/watchdog/gpio_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "summarizeTeardown()") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "requestStop()") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "registerDeviceFailureSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "zigux/tests/phase11_gpio_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "zigux/tests/phase11_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "do not expose `drivers/watchdog/gpio_wdt.zig`") == null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "teardownSummary()") == null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "rebootGlueCheckpointSummary()") == null);
}

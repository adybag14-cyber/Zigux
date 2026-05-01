const std = @import("std");

const SurveySummary = struct {
    dw_wdt_c_lines: usize,
    preexisting_phase11_build_present: bool,
    preexisting_phase11_gpio_lane_present: bool,
    preexisting_phase11_bcm2835_lane_present: bool,
    watchdog_uapi_header_present: bool,
    watchdog_core_header_present: bool,
    dw_wdt_zig_present: bool,
    dw_wdt_test_present: bool,
    dw_wdt_slice_note_present: bool,
    dw_wdt_validation_matrix_present: bool,
    dw_wdt_failure_mode_evidence_present: bool,
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

fn findGap(manifest: Manifest, id: []const u8) ?Gap {
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_driver_scaffold");
}

fn countLines(text: []const u8) usize {
    if (text.len == 0) return 0;

    var lines: usize = 1;
    for (text) |byte| {
        if (byte == '\n') lines += 1;
    }
    if (text[text.len - 1] == '\n') lines -= 1;
    return lines;
}

fn expectSurveyedCommitProvenance(survey_note: []const u8, surveyed_commit: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 40), surveyed_commit.len);
    for (surveyed_commit) |byte| {
        try std.testing.expect(std.ascii.isHex(byte));
    }
    try std.testing.expect(std.mem.indexOf(u8, survey_note, surveyed_commit) != null);
}

test "phase11 dw_wdt survey manifest and validation matrix record the landed lifecycle evidence packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_dw_wdt_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const matrix_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(matrix_doc);

    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-dw-wdt-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_doc);

    const slice_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-dw-wdt-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_doc);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    const anchor_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        manifest.anchor,
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(anchor_source);

    try std.testing.expectEqualStrings("P11-L11", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", manifest.anchor);
    try std.testing.expectEqualStrings("b2deef651d140045bdfb1d3675a3c18fde80de0e", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqual(manifest.survey_summary.dw_wdt_c_lines, countLines(anchor_source));
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_gpio_lane_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_bcm2835_lane_present);
    try std.testing.expect(manifest.survey_summary.watchdog_uapi_header_present);
    try std.testing.expect(manifest.survey_summary.watchdog_core_header_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_zig_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_slice_note_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_validation_matrix_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_failure_mode_evidence_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_note_present);
    try std.testing.expectEqual(@as(usize, 12), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "PHASE11_DW_WDT_STATUS=validation_matrix_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "## Shared Replay Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-dw-wdt-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-dw-wdt-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "fixed TOP timeout evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "IRQ pretimeout bookkeeping") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "imported running-state handoff evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "non-stoppable stop failure-mode boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "remove-time teardown handoff boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "summarizeTeardownLifecycle()") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "summarizeRemoveHandoff()") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig build test --build-file zigux/tests/phase11_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig test --dep dw_wdt -Mroot=zigux/tests/phase11_dw_wdt.zig -Mdw_wdt=drivers/watchdog/dw_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig test zigux/tests/phase11_dw_wdt_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "python3 scripts/zigux/validate-phase11.py") != null);

    try expectSurveyedCommitProvenance(survey_doc, manifest.surveyed_commit);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "bounded DesignWare starter for fixed TOP timeout windows") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "a tiny platform-resource preflight plus live resource-order summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now centralizes") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "latest carried-forward shared replay status remains `PHASE11_VALIDATION=pass`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "This lane still does not claim platform-driver registration") != null);

    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "keeps the DesignWare non-stoppable stop semantics explicit when reset control is unavailable") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "platform-resource preflight plus live resource-order summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "summarizeTeardownLifecycle()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "summarizeRemoveHandoff()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "This slice does not claim platform-driver registration") != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_driver_gap = false;
    var saw_driver_tests = false;
    var saw_header_boundary = false;
    var saw_slice_note = false;
    var saw_validation_matrix = false;
    var saw_platform_blocker = false;
    var saw_probe_summary = false;
    var saw_registration_gap = false;
    var saw_resource_gap = false;

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

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-handoff teardown evidence") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "validation-matrix status") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-driver-starter")) {
            saw_driver_gap = true;
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fixed TOP timeout windows") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe-time summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "summarizeRemoveHandoff()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "debugfs clear") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-driver-tests")) {
            saw_driver_tests = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "non-stoppable stop semantics") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-handoff teardown parity") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-watchdog-header-boundary")) {
            saw_header_boundary = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-dw-wdt-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct watchdog_info") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "WDIOC_*") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog_device") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog_ops") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-dw-wdt-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-handoff teardown packet") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-validation-matrix")) {
            saw_validation_matrix = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-dw-wdt-validation-matrix.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 11 test gate") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fixed-TOP timeout evidence") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "IRQ pretimeout bookkeeping") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "non-stoppable stop failure-mode coverage") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-handoff teardown parity") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "exact replay commands") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "driver-data setup") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "register-device intent") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-platform-resource-preflight")) {
            saw_resource_gap = true;
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "starter now includes") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "timer-clock choice") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "optional APB clock presence") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "optional pretimeout-IRQ wiring") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-platform-and-pm")) {
            saw_platform_blocker = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("blocked_on_driver_scaffold", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Platform-driver registration") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-handoff teardown packet") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-resource preflight") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "suspend and resume handling") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(manifest.gaps.len, starter_landed_count + ready_next_count + blocked_count);
    try std.testing.expectEqual(@as(usize, 11), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(blocked_count > 0);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_driver_gap);
    try std.testing.expect(saw_driver_tests);
    try std.testing.expect(saw_header_boundary);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_validation_matrix);
    try std.testing.expect(saw_probe_summary);
    try std.testing.expect(saw_registration_gap);
    try std.testing.expect(saw_resource_gap);
    try std.testing.expect(saw_platform_blocker);
}

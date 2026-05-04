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
    dw_wdt_suspend_resume_replay_present: bool,
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

const SharedManifest = struct {
    lane_key: []const u8,
    gaps: []const Gap,
};

fn findGap(manifest: Manifest, id: []const u8) ?Gap {
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

fn findSharedGap(manifest: SharedManifest, id: []const u8) ?Gap {
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

    const suspend_resume_test = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(suspend_resume_test);

    const remove_idle_split_test = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(remove_idle_split_test);

    const dw_wdt_zig = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/watchdog/dw_wdt.zig",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(dw_wdt_zig);

    const dw_wdt_test = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_dw_wdt.zig",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(dw_wdt_test);

    const phase11_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_build.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase11_build);

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

    try std.testing.expectEqualStrings("P11-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", manifest.anchor);
    try std.testing.expectEqualStrings("907e65f13e0035306d4106dec0ca3b3eb2fc7179", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqual(manifest.survey_summary.dw_wdt_c_lines, countLines(anchor_source));
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_gpio_lane_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_bcm2835_lane_present);
    try std.testing.expect(manifest.survey_summary.watchdog_uapi_header_present);
    try std.testing.expect(manifest.survey_summary.watchdog_core_header_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_zig_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_suspend_resume_replay_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_slice_note_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_validation_matrix_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_failure_mode_evidence_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_note_present);
    try std.testing.expectEqual(@as(usize, 12), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "PHASE11_DW_WDT_STATUS=validation_matrix_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "## Shared Replay Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-dw-wdt-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-dw-wdt-suspend-resume-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-dw-wdt-remove-idle-split-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-dw-wdt-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "fixed TOP timeout evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "IRQ pretimeout bookkeeping") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "imported running-state handoff evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "bounded suspend-resume state preservation") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "non-stoppable stop failure-mode boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "remove-time teardown handoff boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "idle remove-time pending-interrupt split") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "unconditional debugfs clear call site") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "summarizeSuspendResume()") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "summarizeTeardownLifecycle()") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "summarizeRemoveHandoff()") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig build test --build-file zigux/tests/phase11_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig test --dep dw_wdt -Mroot=zigux/tests/phase11_dw_wdt.zig -Mdw_wdt=drivers/watchdog/dw_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig test --dep dw_wdt -Mroot=zigux/tests/phase11_dw_wdt_suspend_resume.zig -Mdw_wdt=drivers/watchdog/dw_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig test --dep dw_wdt -Mroot=zigux/tests/phase11_dw_wdt_remove_idle_split.zig -Mdw_wdt=drivers/watchdog/dw_wdt.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig test zigux/tests/phase11_dw_wdt_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "python3 scripts/zigux/validate-phase11.py") != null);

    try expectSurveyedCommitProvenance(survey_doc, manifest.surveyed_commit);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "bounded DesignWare starter for fixed TOP timeout windows") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "a tiny platform-resource preflight plus live resource-order summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now centralizes") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "zigux/tests/phase11_dw_wdt_suspend_resume.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "bounded `summarizeSuspendResume()` helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "dedicated idle remove-time pending-interrupt split replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "zigux/tests/phase11_dw_wdt_remove_idle_split.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "the focused `dw_wdt` driver and survey replays for this landed starter packet remain green") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "the focused `dw_wdt` driver and survey replays for this landed starter packet remain green, but this archival watchdog note no longer claims that the whole current shared Phase 11 validator is green when unrelated non-watchdog drift can reopen elsewhere on `master`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "the legacy carried-forward marker text remains \"latest carried-forward shared replay status remains `PHASE11_VALIDATION=pass` for the landed starter packet\" only as archival validator continuity for this bounded note") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "unconditional debugfs clear call site") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "This lane still does not claim platform-driver registration") != null);

    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "keeps the DesignWare non-stoppable stop semantics explicit when reset control is unavailable") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "platform-resource preflight plus live resource-order summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "summarizeSuspendResume()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "summarizeTeardownLifecycle()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "summarizeRemoveHandoff()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "unconditional debugfs clear call site") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "keeps idle remove-time pending interrupts distinct when remove happens before the watchdog is running") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "This slice does not claim platform-driver registration") != null);

    try std.testing.expect(std.mem.indexOf(u8, suspend_resume_test, "test \"phase11 dw_wdt suspend-resume summary preserves running IRQ state and pretimeout bookkeeping\" {") != null);
    try std.testing.expect(std.mem.indexOf(u8, suspend_resume_test, "test \"phase11 dw_wdt suspend-resume summary keeps idle reset-mode state bounded without optional apb clock\" {") != null);
    try std.testing.expect(std.mem.indexOf(u8, suspend_resume_test, "try std.testing.expect(summary.resume_preserves_timeout_programming);") != null);

    try std.testing.expect(std.mem.indexOf(u8, remove_idle_split_test, "test \"phase11 dw_wdt keeps idle remove-time pending interrupts distinct when reset control is available or absent\" {") != null);
    try std.testing.expect(std.mem.indexOf(u8, remove_idle_split_test, "remove_preserves_pending_interrupt_without_reset") != null);
    try std.testing.expect(std.mem.indexOf(u8, remove_idle_split_test, "remove_clears_interrupt_status") != null);
    try std.testing.expect(std.mem.indexOf(u8, remove_idle_split_test, "remove_asserts_reset_control") != null);

    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_zig, "pub const SuspendResumeSummary = struct {") != null);
    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_zig, "pub const TeardownLifecycleSummary = struct {") != null);
    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_zig, "pub const RemoveSummary = struct {") != null);
    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_zig, "pub fn summarizeSuspendResume(") != null);
    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_zig, "pub fn summarizeTeardownLifecycle(") != null);
    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_zig, "pub fn summarizeRemoveHandoff(") != null);
    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_zig, "pub fn liveResourceOrderSummary(") != null);

    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_test, "test \"phase11 dw_wdt remove handoff keeps unregister and reset-control teardown parity explicit\" {") != null);
    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_test, "test \"phase11 dw_wdt stop and restart stay bounded to reset-control and non-stoppable semantics\" {") != null);
    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_test, "try std.testing.expect(unstoppable_summary.stop_preserves_pending_interrupt_without_reset);") != null);
    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_test, "try std.testing.expect(stoppable_summary.stop_uses_reset_pulse);") != null);
    try std.testing.expect(std.mem.indexOf(u8, dw_wdt_test, "try std.testing.expect(stoppable_summary.remove_asserts_reset_control);") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase11_build, ".name = \"phase11-dw-wdt-tests\",") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase11_build, ".name = \"phase11-dw-wdt-suspend-resume-tests\",") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase11_build, ".name = \"phase11-dw-wdt-remove-idle-split-tests\",") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase11_build, ".name = \"phase11-dw-wdt-survey-tests\",") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase11_build, "test_step.dependOn(&run_phase11_dw_wdt_tests.step);") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase11_build, "test_step.dependOn(&run_phase11_dw_wdt_suspend_resume_tests.step);") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase11_build, "test_step.dependOn(&run_phase11_dw_wdt_remove_idle_split_tests.step);") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase11_build, "test_step.dependOn(&run_phase11_dw_wdt_survey_tests.step);") != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_survey_note = false;
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

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-dw-wdt-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "anchors the live dw_wdt lane to `master`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-resource preflight packet") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "review packet provenance") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-driver-starter")) {
            saw_driver_gap = true;
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fixed TOP timeout windows") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe-time summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "summarizeRemoveHandoff()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "unconditional debugfs clear call site") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-driver-tests")) {
            saw_driver_tests = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "non-stoppable stop semantics") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-handoff teardown parity") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "debugfs-clear call-site ownership boundary") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "debugfs-clear ownership boundary") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "debugfs-clear call-site boundary") != null);
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
    try std.testing.expect(saw_survey_note);
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

test "phase11 dw_wdt survey keeps the shared watchdog header boundary aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const shared_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_uapi_header_parity_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(shared_manifest_json);

    const shared_survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-uapi-header-parity-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(shared_survey_doc);

    const dw_survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-dw-wdt-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(dw_survey_doc);

    const watchdog_uapi_header = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "include/uapi/linux/watchdog.h",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(watchdog_uapi_header);

    const watchdog_core_header = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "include/linux/watchdog.h",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(watchdog_core_header);

    const parsed_shared = try std.json.parseFromSlice(
        SharedManifest,
        std.testing.allocator,
        shared_manifest_json,
        .{ .ignore_unknown_fields = true },
    );
    defer parsed_shared.deinit();

    const shared_manifest = parsed_shared.value;
    const shared_dw_gap = findSharedGap(shared_manifest, "phase11-dw-wdt-watchdog-header-boundary") orelse return error.MissingSharedDwWdtBoundary;

    try std.testing.expectEqualStrings("P11-L17", shared_manifest.lane_key);
    try std.testing.expectEqualStrings("starter_landed", shared_dw_gap.status);
    try std.testing.expectEqualStrings("Documentation/zigux/phase11-dw-wdt-survey.md", shared_dw_gap.zigux_destination);

    for ([_][]const u8{
        "include/uapi/linux/watchdog.h",
        "include/linux/watchdog.h",
        "struct watchdog_info",
        "WDIOC_*",
        "WDIOF_*",
        "WDIOS_*",
        "watchdog_device",
        "watchdog_ops",
    }) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, shared_dw_gap.why_now, needle) != null);
        try std.testing.expect(std.mem.indexOf(u8, shared_survey_doc, needle) != null);
        try std.testing.expect(std.mem.indexOf(u8, dw_survey_doc, needle) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, shared_survey_doc, "dw_wdt survey packet now records") != null);
    try std.testing.expect(std.mem.indexOf(u8, shared_survey_doc, "without claiming full watchdog-core ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, dw_survey_doc, "driver-side bookkeeping instead of claiming public-header or watchdog-core parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "struct watchdog_info") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "WDIOC_GETSUPPORT") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "WDIOF_KEEPALIVEPING") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "WDIOS_DISABLECARD") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_core_header, "struct watchdog_ops") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_core_header, "struct watchdog_device") != null);
}

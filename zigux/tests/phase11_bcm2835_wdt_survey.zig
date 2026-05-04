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
    bcm2835_wdt_poweroff_summary_present: bool,
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

test "phase11 bcm2835_wdt survey manifest and validation matrix record the landed handoff plus poweroff review surface" {
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

    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_doc);

    const slice_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-bcm2835-wdt-slice.md",
        std.testing.allocator,
        .limited(32 * 32 * 1024),
    );
    defer std.testing.allocator.free(slice_doc);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P11-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.c", manifest.anchor);
    try std.testing.expectEqualStrings("f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_c_lines >= 240);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_gpio_lane_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_zig_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_slice_note_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_validation_matrix_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_platform_handoff_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_poweroff_summary_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_shared_replay_evidence_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_survey_note_present);
    try std.testing.expectEqual(@as(usize, 14), manifest.gaps.len);

    const expected_commit_pin = try std.fmt.allocPrint(
        std.testing.allocator,
        "reviewed against live `master` `{s}`",
        .{manifest.surveyed_commit},
    );
    defer std.testing.allocator.free(expected_commit_pin);

    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "PHASE11_BCM2835_WDT_STATUS=platform_handoff_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, expected_commit_pin) != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "latest focused replay: `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig` still passes for the bounded bcm2835 packet on current `master`") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "shared replay boundary: `zig build test --build-file zigux/tests/phase11_build.zig --summary all` still includes `phase11-bcm2835-wdt-tests` and `phase11-bcm2835-wdt-survey-tests`") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "## Shared Replay Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-bcm2835-wdt-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-bcm2835-wdt-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig build test --build-file zigux/tests/phase11_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig test zigux/tests/phase11_bcm2835_wdt_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "watchdog metadata surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "WDIOF_SETTIMEOUT") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "full platform registration") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "PM base ioremap") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "registration outcome failure boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "registrationOutcomeSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "poweroff path summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "shared system-poweroff callback") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "remove-time teardown boundary") != null);

    try std.testing.expect(std.mem.indexOf(u8, survey_doc, expected_commit_pin) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "archival checkpoint for the original Phase 11 roadmap gap") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "the focused replay `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig` still passes for the bounded bcm2835 packet on current `master`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "this archival watchdog note no longer claims that the whole current shared Phase 11 replay is green") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "bcm2835 starter for watchdog metadata, timeout tick encoding, running-bit detection") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "small poweroff-path summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "tiny registration-outcome summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "register-device success-versus-failure and poweroff-claim blocking evidence explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "tiny platform-registration or PM-base handoff summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`zigux/tests/phase11_build.zig` still compiles and runs the gpio starter checks, the bcm2835 starter checks, and the bcm2835 survey check together") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "the archival survey now carries `P11-L08` packet identity so the bcm2835 watchdog review record stays traceable alongside the live manifest, survey gate, and validator ownership for the current lane key") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`P11-L05`") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "Any later move into live platform registration, PM base plumbing, or shared poweroff-handler coordination should stay blocked") != null);

    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "tiny watchdog metadata summary for the Linux identity string, watchdog option flags, static timeout bounds, and bounded start or stop or get_timeleft or restart ops coverage") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "tiny registration-outcome summary for register-device success versus failure, probe-error return intent, and poweroff-handler claim follow-through or blocking when registration does not complete") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "tiny platform-registration and PM-base handoff summary for parent attachment, PM base availability, drvdata handoff readiness, register-device intent, and poweroff claim-vs-conflict reviewability") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "tiny poweroff-path summary for shared system-poweroff callback ownership, Raspberry Pi halt-partition request bits, and the short restart arming sequence") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "tiny remove-time teardown summary for devm-managed watchdog cleanup while clearing the shared poweroff handler only when the bcm2835 lane currently owns it") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "registration-outcome failure handling") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "remaining gap is a later hardware-facing decision about whether to model any live platform registration or PM base plumbing") != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_survey_note = false;
    var saw_driver_gap = false;
    var saw_metadata_summary = false;
    var saw_driver_tests = false;
    var saw_slice_note = false;
    var saw_validation_matrix = false;
    var saw_probe_summary = false;
    var saw_registration_summary = false;
    var saw_platform_handoff = false;
    var saw_poweroff_summary = false;
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

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-bcm2835-wdt-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "current master head") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog metadata summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "poweroff-path summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time teardown summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-driver-starter")) {
            saw_driver_gap = true;
            try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog metadata") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "registration-facing handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-registration and PM-base handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "poweroff-path summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time teardown summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-watchdog-metadata")) {
            saw_metadata_summary = true;
            try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Linux identity string") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog option flags") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "start or stop or get_timeleft or restart ops surface") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-driver-tests")) {
            saw_driver_tests = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog metadata") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-handoff prerequisites") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "poweroff-path sequencing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time poweroff ownership plus devm-managed teardown outcomes") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-bcm2835-wdt-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog metadata summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "poweroff-path summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time teardown summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-validation-matrix")) {
            saw_validation_matrix = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 11 test gate") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog metadata surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landed platform-handoff review surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "poweroff-path sequencing evidence") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time teardown scope") != null);
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

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-poweroff-summary")) {
            saw_poweroff_summary = true;
            try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared system-poweroff callback") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Raspberry Pi halt-partition request bits") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "short watchdog restart arming sequence") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-bcm2835-wdt-remove-summary")) {
            saw_remove_followup = true;
            try std.testing.expectEqualStrings("drivers/watchdog/bcm2835_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time teardown summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "devm-managed") != null);
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

    try std.testing.expectEqual(@as(usize, 13), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_driver_gap);
    try std.testing.expect(saw_metadata_summary);
    try std.testing.expect(saw_driver_tests);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_validation_matrix);
    try std.testing.expect(saw_probe_summary);
    try std.testing.expect(saw_registration_summary);
    try std.testing.expect(saw_platform_handoff);
    try std.testing.expect(saw_poweroff_summary);
    try std.testing.expect(saw_remove_followup);
    try std.testing.expect(saw_live_platform_gap);
}

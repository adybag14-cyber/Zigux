const std = @import("std");

const SurveySummary = struct {
    bcm2835_wdt_c_lines: usize,
    preexisting_phase11_build_present: bool,
    preexisting_phase11_gpio_lane_present: bool,
    bcm2835_wdt_zig_present: bool,
    bcm2835_wdt_test_present: bool,
    bcm2835_wdt_slice_note_present: bool,
    bcm2835_wdt_validation_matrix_present: bool,
    bcm2835_wdt_shared_contract_present: bool,
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

test "phase11 bcm2835_wdt survey manifest, shared contract, and validation matrix record the landed handoff plus poweroff review surface" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_bcm2835_wdt_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const contract_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-shared-replay-contract.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(contract_doc);

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
    try std.testing.expectEqualStrings("55568844ac3ce835b0e0bef624c24c17f22b78a1", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_c_lines >= 240);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_gpio_lane_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_zig_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_slice_note_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_validation_matrix_present);
    try std.testing.expect(manifest.survey_summary.bcm2835_wdt_shared_contract_present);
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

    for (manifest.gaps) |gap| {
        try std.testing.expect(isAllowedStatus(gap.status));
    }

    try std.testing.expect(std.mem.indexOf(u8, contract_doc, "`Documentation/zigux/phase11-bcm2835-wdt-survey.md`") != null);
    try std.testing.expect(std.mem.indexOf(u8, contract_doc, "`zigux/tests/phase11_bcm2835_wdt_manifest.json`") != null);
    try std.testing.expect(std.mem.indexOf(u8, contract_doc, "`zigux/tests/phase11_bcm2835_wdt_survey.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, contract_doc, "The active bcm2835 hardware-validation packet also stays explicit beside that shared route:") != null);

    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "PHASE11_BCM2835_WDT_STATUS=platform_handoff_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, expected_commit_pin) != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "latest focused replays: `zig test zigux/tests/phase11_bcm2835_wdt.zig`, `zig test drivers/watchdog/bcm2835_wdt_verify.zig`, and `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig` still pass for the bounded bcm2835 packet on current `master`") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "shared replay boundary: `zig build test --build-file zigux/tests/phase11_build.zig --summary all` still includes `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "## Shared Replay Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-bcm2835-wdt-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-bcm2835-wdt-verify-tests") != null);
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
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "drivers/watchdog/bcm2835_wdt_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "dedicated archival bcm2835 hardware-validation packet beside the shared replay route: `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, and `zigux/tests/phase11_bcm2835_wdt_survey.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "keep `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from either the shipped shared replay route or the dedicated bcm2835 archival packet") != null);

    try std.testing.expect(std.mem.indexOf(u8, survey_doc, expected_commit_pin) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "archival checkpoint for the original Phase 11 roadmap gap") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "the focused replays `zig test zigux/tests/phase11_bcm2835_wdt.zig`, `zig test drivers/watchdog/bcm2835_wdt_verify.zig`, and `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig` still pass for the bounded bcm2835 packet on current `master`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "this archival watchdog note no longer claims that the whole current shared Phase 11 replay is green") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "bcm2835 starter for watchdog metadata, timeout tick encoding, running-bit detection") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "bounded start and stop register transitions") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "small poweroff-path summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "tiny registration-outcome summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "tiny platform-registration or PM-base handoff summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`zigux/tests/phase11_build.zig` still compiles and runs the gpio starter checks, the bcm2835 starter checks, and the bcm2835 survey check together") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "the archival survey now carries `P11-L08` packet identity so the bcm2835 watchdog review record stays traceable alongside the live manifest, survey gate, and validator ownership for the current lane key") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "`P11-L05`") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "Any later move into live platform registration, PM base plumbing, or shared poweroff-handler coordination should stay blocked") != null);

    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "bounded `is_running`, `start`, `stop`, `get_timeleft`, and restart behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "tiny platform-registration and PM-base handoff summary for parent attachment, PM base availability, drvdata handoff readiness, register-device intent, and poweroff claim-vs-conflict reviewability") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "tiny poweroff-path summary for shared system-poweroff callback ownership, Raspberry Pi halt-partition request bits, and the short restart arming sequence") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "tiny remove-time teardown summary for devm-managed watchdog cleanup while clearing the shared poweroff callback only when `pm_power_off` still points at `bcm2835_power_off`") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "register-image transition coverage") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "remaining gap is a later hardware-facing decision about whether to model any live platform registration or PM base plumbing") != null);
}

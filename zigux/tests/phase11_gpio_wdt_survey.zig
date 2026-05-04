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

test "phase11 gpio_wdt survey manifest records the refreshed starter state, module slice, and remaining gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_gpio_wdt_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const driver_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/watchdog/gpio_wdt.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(driver_source);

    const matrix_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(matrix_doc);

    const slice_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-gpio-wdt-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_doc);

    const module_slice_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-gpio-wdt-module-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(module_slice_doc);

    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-gpio-wdt-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_doc);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P11-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.c", manifest.anchor);
    try std.testing.expectEqualStrings("0bd402fd6ca83ba2ace6b21e9e57459401b631cd", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.gpio_wdt_c_lines >= 190);
    try std.testing.expectEqual(@as(usize, 2), manifest.survey_summary.preexisting_phase11_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_gpio_wdt_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_gpio_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_module_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_validation_matrix_present);
    try std.testing.expectEqual(@as(usize, 16), manifest.gaps.len);

    const expected_commit_pin = try std.fmt.allocPrint(
        std.testing.allocator,
        "reviewed against live `master` `{s}`",
        .{manifest.surveyed_commit},
    );
    defer std.testing.allocator.free(expected_commit_pin);

    const expected_matrix_snapshot_line = try std.fmt.allocPrint(
        std.testing.allocator,
        "- inspected `master` head: `{s}`",
        .{manifest.surveyed_commit},
    );
    defer std.testing.allocator.free(expected_matrix_snapshot_line);

    const expected_active_owner_line = "- active continuity owner for this review packet: `P11-Y01`";

    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub const PlatformDriverRegistrationMode = enum") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub const PlatformDriverIdentitySummary = struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, "pub fn platformDriverIdentitySummary() PlatformDriverIdentitySummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, ".driver_name = \"gpio-wdt\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, ".of_compatible = \"linux,wdt-gpio\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, ".probe_callback = \"gpio_wdt_probe\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, ".default_registration_mode = .module_platform_driver") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver_source, ".supports_arch_initcall_override = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "PHASE11_GPIO_WDT_STATUS=metadata_teardown_and_register_device_surface_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, expected_commit_pin) != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, expected_active_owner_line) != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, expected_matrix_snapshot_line) != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "## Shared Replay Surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-gpio-wdt-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "phase11-gpio-wdt-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig build test --build-file zigux/tests/phase11_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "zig test zigux/tests/phase11_gpio_wdt_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "- lane key: `P11-L04`") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "- active continuity owner: `P11-Y01`") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "direct watchdog metadata surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "GPIO Watchdog") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "teardown-facing stop evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "nowayout failure-mode evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "explicit disable-order teardown summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "summarizeTeardown()") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "register-device call surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "explicit remaining blocker surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "registerDeviceFailureSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "descriptor preflight, platform registration, and reboot glue blockers") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix_doc, "descriptor-facing registration handoff") == null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "watchdog-info identity") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "summarizeTeardown()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "registerDeviceCallSummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "platformDriverIdentitySummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "gpio-wdt") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "linux,wdt-gpio") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "module_platform_driver()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "The active continuity owner for this review packet is `P11-Y01`.") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "first bounded `devm_watchdog_register_device()` request") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "The next honest bounded step inside the same Phase 11 lane is to leave the starter parked unless fresh repo inspection finds another comparably small simple-driver, teardown, or failure-mode drift inside `gpio_wdt`.") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "Keep descriptor-backed preflight, reboot glue, and broader watchdog registration work blocked from this slice.") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_doc, "move from that metadata-only registration plan to the first bounded register-device call surface") == null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice_doc, "`gpio_wdt_lab` descriptor") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice_doc, "`summarizeTeardown()` helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice_doc, "`registerDeviceCallSummary()` surface explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice_doc, "The active continuity owner for this review packet is `P11-Y01`, while the archived manifest identity remains `P11-L04` for traceability.") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice_doc, "The next honest bounded step inside the same Phase 11 lane is to leave this starter parked unless fresh repo inspection finds another comparably small teardown or failure-mode drift inside `gpio_wdt`.") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_slice_doc, "Avoid widening straight into descriptor-backed preflight, reboot glue, or broader watchdog registration work from this packet.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, expected_commit_pin) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, expected_active_owner_line) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "platformDriverIdentitySummary()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "gpio-wdt") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "linux,wdt-gpio") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "module_platform_driver()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "The next honest bounded step inside the same lane is to leave this starter parked unless fresh repo inspection finds another comparably small simple-driver, teardown, or failure-mode drift inside `gpio_wdt`.") != null);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_driver_gap = false;
    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_doc_gate = false;
    var saw_test_gate = false;
    var saw_slice_note = false;
    var saw_validation_matrix = false;
    var saw_metadata_followup = false;
    var saw_platform_driver_identity_followup = false;
    var saw_stop_followup = false;
    var saw_handoff_followup = false;
    var saw_plan_followup = false;
    var saw_register_device_followup = false;
    var saw_register_device_failure_followup = false;
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

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_gpio_wdt_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freshness check") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landed gpio_wdt starter") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "overclaim broader watchdog progress") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-survey-note")) {
            saw_doc_gate = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-gpio-wdt-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-driver shell") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown-facing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hardware-validation posture") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-driver-starter")) {
            saw_driver_gap = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hw_algo") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "heartbeat margin") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-driver shell") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown-facing") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-driver-tests")) {
            saw_test_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown-facing") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-gpio-wdt-slice.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-driver shell") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown-facing") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-validation-matrix")) {
            saw_validation_matrix = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-gpio-wdt-validation-matrix.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 11 replay path") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown-facing stop evidence") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "register-device call surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "explicit remaining blocker surface") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-watchdog-metadata-followup")) {
            saw_metadata_followup = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdogMetadataSummary()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "GPIO Watchdog") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "WDIOF_SETTIMEOUT") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "WDIOF_MAGICCLOSE") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "WDIOF_KEEPALIVEPING") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-platform-driver-identity-followup")) {
            saw_platform_driver_identity_followup = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platformDriverIdentitySummary()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "gpio-wdt") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "linux,wdt-gpio") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "gpio_wdt_probe()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "module_platform_driver()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "CONFIG_GPIO_WATCHDOG_ARCH_INITCALL") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown-facing") != null);
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

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-register-device-call-followup")) {
            saw_register_device_followup = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "register-device request summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog metadata") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown-adjacent startup state") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-gpio-wdt-register-device-failure-followup")) {
            saw_register_device_failure_followup = true;
            try std.testing.expectEqualStrings("drivers/watchdog/gpio_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "registerDeviceFailureSummary()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "descriptor preflight") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-registration") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reboot-glue blockers") != null);
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

    try std.testing.expectEqual(@as(usize, 15), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_doc_gate);
    try std.testing.expect(saw_driver_gap);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_validation_matrix);
    try std.testing.expect(saw_metadata_followup);
    try std.testing.expect(saw_platform_driver_identity_followup);
    try std.testing.expect(saw_stop_followup);
    try std.testing.expect(saw_handoff_followup);
    try std.testing.expect(saw_plan_followup);
    try std.testing.expect(saw_register_device_followup);
    try std.testing.expect(saw_register_device_failure_followup);
    try std.testing.expect(saw_blocker);
}

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

test "phase11 dw_wdt survey manifest records the landed registration handoff and platform-resource preflight" {
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
    try std.testing.expectEqualStrings("P11-L10", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.c", manifest.anchor);
    try std.testing.expectEqualStrings("e078a6f17710c8095c1ba9557651897d7eb615f1", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.dw_wdt_c_lines >= 700);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_gpio_lane_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_bcm2835_lane_present);
    try std.testing.expect(manifest.survey_summary.watchdog_uapi_header_present);
    try std.testing.expect(manifest.survey_summary.watchdog_core_header_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_zig_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_test_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_slice_note_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_note_present);
    try std.testing.expectEqual(@as(usize, 11), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_driver_gap = false;
    var saw_driver_tests = false;
    var saw_header_boundary = false;
    var saw_slice_note = false;
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
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-driver-starter")) {
            saw_driver_gap = true;
            try std.testing.expectEqualStrings("drivers/watchdog/dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fixed TOP timeout windows") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "probe-time summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-driver-tests")) {
            saw_driver_tests = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "platform-resource preflight") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "suspend and resume handling") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 10), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_driver_gap);
    try std.testing.expect(saw_driver_tests);
    try std.testing.expect(saw_header_boundary);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_probe_summary);
    try std.testing.expect(saw_registration_gap);
    try std.testing.expect(saw_resource_gap);
    try std.testing.expect(saw_platform_blocker);
}

test "phase11 dw_wdt survey keeps the watchdog header boundary explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-dw-wdt-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

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

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "include/uapi/linux/watchdog.h") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "struct watchdog_info") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "WDIOC_*") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "WDIOF_*") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "WDIOS_*") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "include/linux/watchdog.h") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "watchdog_device") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "watchdog_ops") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "struct watchdog_info") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "WDIOC_GETSUPPORT") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "WDIOF_SETTIMEOUT") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "WDIOS_DISABLECARD") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_core_header, "struct watchdog_ops") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_core_header, "struct watchdog_device") != null);
}

test "phase11 dw_wdt notes stay pinned to the manifest commit and platform-resource preflight wording" {
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

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-dw-wdt-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-dw-wdt-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const manifest = parsed.value;
    const preflight_gap = findGap(manifest, "phase11-dw-wdt-platform-resource-preflight").?;
    try std.testing.expectEqualStrings("starter_landed", preflight_gap.status);

    const commit_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "`master` `{s}`",
        .{manifest.surveyed_commit},
    );
    defer std.testing.allocator.free(commit_marker);

    const preflight_marker = "timer-clock choice, optional APB clock presence, reset-control availability, and optional pretimeout-IRQ wiring";
    try std.testing.expect(std.mem.indexOf(u8, survey_note, commit_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, preflight_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, preflight_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "blocked on platform-driver scaffold work") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "blocked on platform-driver scaffold work") != null);
}

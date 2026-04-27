const std = @import("std");
const layout_assert = @import("layout_assert");

const SurveySummary = struct {
    preexisting_phase11_build_present: bool,
    watchdog_uapi_header_present: bool,
    watchdog_core_header_present: bool,
    hvc_console_header_present: bool,
    dw_wdt_survey_note_present: bool,
    dw_wdt_manifest_present: bool,
    hvc_console_survey_note_present: bool,
    hvc_console_manifest_present: bool,
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

const WatchdogInfoLayout = extern struct {
    options: u32,
    firmware_version: u32,
    identity: [32]u8,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next");
}

test "phase11 shared header parity manifest records the bounded layout checkpoint" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_uapi_header_parity_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P11-L11", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("include/uapi/linux/watchdog.h", manifest.anchor);
    try std.testing.expectEqualStrings("71c0ed93260f46dd1058e043c0bb111270628ca1", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.watchdog_uapi_header_present);
    try std.testing.expect(manifest.survey_summary.watchdog_core_header_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_header_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_note_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_manifest_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_survey_note_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_manifest_present);
    try std.testing.expectEqual(@as(usize, 6), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_note = false;
    var saw_gate = false;
    var saw_dw_boundary = false;
    var saw_hvc_boundary = false;
    var saw_layout_checkpoint = false;
    var saw_phase3_followup = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase11-shared-header-parity-note")) {
            saw_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-uapi-header-parity-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase11-shared-header-parity-gate")) {
            saw_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_uapi_header_parity_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-watchdog-header-boundary")) {
            saw_dw_boundary = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-dw-wdt-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct watchdog_info") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "watchdog_ops") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-header-boundary")) {
            saw_hvc_boundary = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "MAX_NR_HVC_CONSOLES") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hv_ops") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-watchdog-info-layout-assert")) {
            saw_layout_checkpoint = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_uapi_header_parity_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "layout_assert") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "size, alignment, and field offsets") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-phase3-interop-followup")) {
            saw_phase3_followup = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-uapi-header-parity-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared struct layouts") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Phase 3 interop substrate") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 5), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_gate);
    try std.testing.expect(saw_dw_boundary);
    try std.testing.expect(saw_hvc_boundary);
    try std.testing.expect(saw_layout_checkpoint);
    try std.testing.expect(saw_phase3_followup);
}

test "phase11 shared header parity survey keeps the header boundary explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-uapi-header-parity-survey.md",
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

    const hvc_header = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/tty/hvc/hvc_console.h",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(hvc_header);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "include/uapi/linux/watchdog.h") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "struct watchdog_info") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "layout_assert") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "size 40") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "alignment 4") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "offsets 0, 4, and 8") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "watchdog_device") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "watchdog_ops") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 3 interop substrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared struct layouts") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "struct watchdog_info") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "__u32 options") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "__u32 firmware_version") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "__u8  identity[32]") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "WDIOC_GETSUPPORT") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "WDIOS_DISABLECARD") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_core_header, "struct watchdog_ops") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_core_header, "struct watchdog_device") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "MAX_NR_HVC_CONSOLES") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "HVC_ALLOC_TTY_ADAPTERS") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "struct hv_ops") != null);
}

test "phase11 shared header parity survey keeps a bounded watchdog_info layout proof" {
    comptime {
        layout_assert.assertSize(WatchdogInfoLayout, 40);
        layout_assert.assertAlign(WatchdogInfoLayout, 4);
        layout_assert.assertOffset(WatchdogInfoLayout, "options", 0);
        layout_assert.assertOffset(WatchdogInfoLayout, "firmware_version", 4);
        layout_assert.assertOffset(WatchdogInfoLayout, "identity", 8);
    }
}

const std = @import("std");

const SurveySummary = struct {
    shared_phase11_build_present: bool,
    shared_phase11_header_note_present: bool,
    shared_phase11_header_survey_present: bool,
    watchdog_info_layout_assert_present: bool,
    winsize_layout_assert_present: bool,
    hvc_export_surface_checked: bool,
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

const WatchdogInfo = extern struct {
    options: u32,
    firmware_version: u32,
    identity: [32]u8,
};

const WinSize = extern struct {
    ws_row: u16,
    ws_col: u16,
    ws_xpixel: u16,
    ws_ypixel: u16,
};

fn readFileAlloc(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase11 shared header parity survey manifest records the restored packet cleanly" {
    const manifest_json = try readFileAlloc(std.testing.allocator, "zigux/tests/phase11_uapi_header_parity_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P11-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839", manifest.surveyed_commit);
    try std.testing.expect(manifest.roadmap_destinations.len >= 4);
    try std.testing.expect(manifest.survey_summary.shared_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.shared_phase11_header_note_present);
    try std.testing.expect(manifest.survey_summary.shared_phase11_header_survey_present);
    try std.testing.expect(manifest.survey_summary.watchdog_info_layout_assert_present);
    try std.testing.expect(manifest.survey_summary.winsize_layout_assert_present);
    try std.testing.expect(manifest.survey_summary.hvc_export_surface_checked);

    var saw_build_gate = false;
    var saw_watchdog_layout = false;
    var saw_winsize_layout = false;
    var saw_export_surface = false;

    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.status.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.zigux_destination.len > 0);
        try std.testing.expect(gap.why_now.len > 0);

        if (std.mem.eql(u8, gap.id, "phase11-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-watchdog-info-layout-assert")) {
            saw_watchdog_layout = true;
        }
        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-winsize-layout-assert")) {
            saw_winsize_layout = true;
        }
        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-export-signature-assert")) {
            saw_export_surface = true;
        }
    }

    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_watchdog_layout);
    try std.testing.expect(saw_winsize_layout);
    try std.testing.expect(saw_export_surface);
}

test "phase11 shared header parity survey keeps a bounded watchdog_info layout proof" {
    try std.testing.expectEqual(@as(usize, 40), @sizeOf(WatchdogInfo));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(WatchdogInfo));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(WatchdogInfo, "options"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(WatchdogInfo, "firmware_version"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(WatchdogInfo, "identity"));
}

test "phase11 shared header parity survey keeps a bounded winsize layout proof" {
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(WinSize));
    try std.testing.expectEqual(@as(usize, 2), @alignOf(WinSize));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(WinSize, "ws_row"));
    try std.testing.expectEqual(@as(usize, 2), @offsetOf(WinSize, "ws_col"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(WinSize, "ws_xpixel"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(WinSize, "ws_ypixel"));
}

test "phase11 shared header parity survey keeps the note pinned to the manifest provenance" {
    const manifest_json = try readFileAlloc(std.testing.allocator, "zigux/tests/phase11_uapi_header_parity_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const note = try readFileAlloc(std.testing.allocator, "Documentation/zigux/phase11-uapi-header-parity-survey.md", 32 * 1024);
    defer std.testing.allocator.free(note);

    try expectContains(note, parsed.value.surveyed_commit);
    try expectContains(note, "PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_restored");
    try expectContains(note, "phase11-dw-wdt-watchdog-info-layout-assert");
    try expectContains(note, "phase11-hvc-console-winsize-layout-assert");
    try expectContains(note, "phase11-hvc-console-export-signature-assert");
    try expectContains(note, "phase11-uapi-header-parity-surface");
}

test "phase11 shared header parity survey keeps shared build inventory markers explicit" {
    const inventory = try readFileAlloc(std.testing.allocator, "zigux/tests/fixtures/phase11_build_inventory.json", 64 * 1024);
    defer std.testing.allocator.free(inventory);

    try expectContains(inventory, "phase11-uapi-header-parity-survey-tests");
    try expectContains(inventory, "phase11-dw-wdt-suspend-resume-tests");
    try expectContains(inventory, "phase11-dw-wdt-remove-idle-split-tests");
    try expectContains(inventory, "phase11-hvc-console-modem-control-split-tests");
    try expectContains(inventory, "phase11-hvc-console-poll-retry-split-tests");
    try expectContains(inventory, "phase11-hvc-console-survey-tests");
}

test "phase11 shared header parity survey keeps the exported hvc surface explicit" {
    const hvc_console = try readFileAlloc(std.testing.allocator, "drivers/tty/hvc/hvc_console.zig", 256 * 1024);
    defer std.testing.allocator.free(hvc_console);

    try expectContains(hvc_console, "MAX_NR_HVC_CONSOLES");
    try expectContains(hvc_console, "HVC_ALLOC_TTY_ADAPTERS");
    try expectContains(hvc_console, "pub fn hvc_instantiate");
    try expectContains(hvc_console, "pub fn hvc_alloc");
    try expectContains(hvc_console, "pub fn hvc_remove");
    try expectContains(hvc_console, "pub fn hvc_poll");
    try expectContains(hvc_console, "pub fn hvc_kick");
    try expectContains(hvc_console, "pub fn __hvc_resize");
    try expectContains(hvc_console, "pub fn notifier_add_irq");
    try expectContains(hvc_console, "pub fn notifier_del_irq");
}

test "phase11 shared header parity survey keeps the shared build hook explicit" {
    const build_file = try readFileAlloc(std.testing.allocator, "zigux/tests/phase11_build.zig", 32 * 1024);
    defer std.testing.allocator.free(build_file);

    try expectContains(build_file, "phase11_uapi_header_parity_survey.zig");
    try expectContains(build_file, "phase11-uapi-header-parity-survey-tests");
    try expectContains(build_file, "test_step.dependOn(&run_phase11_uapi_header_parity_survey_tests.step);");
}

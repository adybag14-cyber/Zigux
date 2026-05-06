const std = @import("std");
const layout_assert = @import("layout_assert");

const SurveySummary = struct {
    hvc_console_c_lines: usize,
    preexisting_phase11_build_present: bool,
    preexisting_phase11_watchdog_lanes: usize,
    hvc_console_zig_present: bool,
    hvc_console_test_present: bool,
    hvc_console_survey_gate_present: bool,
    hvc_console_survey_note_present: bool,
    winsize_layout_assert_present: bool,
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

const WinSize = extern struct {
    ws_row: u16,
    ws_col: u16,
    ws_xpixel: u16,
    ws_ypixel: u16,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_driver_scaffold") or
        std.mem.eql(u8, status, "blocked_on_kernel_integration");
}

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

test "phase11 hvc_console survey manifest records the landed starter and tty handoff cleanly" {
    const manifest_json = try readFileAlloc(
        std.testing.allocator,
        "zigux/tests/phase11_hvc_console_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P11-L14", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.c", manifest.anchor);
    try std.testing.expectEqualStrings("ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.hvc_console_c_lines >= 1000);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_phase11_watchdog_lanes);
    try std.testing.expect(manifest.survey_summary.hvc_console_zig_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_test_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_survey_note_present);
    try std.testing.expect(manifest.survey_summary.winsize_layout_assert_present);
    try std.testing.expectEqual(@as(usize, 12), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_winsize_layout = false;
    var saw_note = false;
    var saw_starter_gap = false;
    var saw_cleanup_handoff = false;
    var saw_remove_handoff = false;
    var saw_driver_test_block = false;
    var saw_validation_matrix = false;
    var saw_tty_handoff = false;
    var saw_sysrq_handoff = false;
    var saw_notifier_handoff = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_driver_scaffold") or
            std.mem.eql(u8, gap.status, "blocked_on_kernel_integration"))
        {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase11-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_build.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "cleanup handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sysrq handoff helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier handoff helper") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "targetless no-unregister edge") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-winsize-layout-assert")) {
            saw_winsize_layout = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct winsize") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "resize boundary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-survey-note")) {
            saw_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-hvc-console-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "cleanup handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sysrq handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier-facing handoff summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-driver-starter")) {
            saw_starter_gap = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "CRLF") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "flush intent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "cleanup handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sysrq handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier-facing handoff summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-cleanup-handoff")) {
            saw_cleanup_handoff = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "final-close") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hangup-driven tty_port_put() release") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-port reference is already gone") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-port lifecycle") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-remove-handoff")) {
            saw_remove_handoff = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "console-slot clearing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "IRQ handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty_port_put") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty_vhangup") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty_kref_put") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-driver-tests")) {
            saw_driver_test_block = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "newline framing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown gating") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sysrq handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "targetless no-unregister edge") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-validation-matrix")) {
            saw_validation_matrix = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-hvc-console-validation-matrix.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 11 test gate") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "cleanup replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sysrq handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier-facing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "targetless notifier no-unregister edge") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-tty-and-teardown-parity")) {
            saw_tty_handoff = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "close-wait ownership") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd-facing boundary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-sysrq-handoff")) {
            saw_sysrq_handoff = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "boot-console-only sysrq dispatch intent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "break detection") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier callback boundary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "worker execution") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-notifier-handoff")) {
            saw_notifier_handoff = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier registration intent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "deferred callback ownership") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "deferred unregister timing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "never-registered path") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "unregister timing stays false") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "targetless path") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "no notifier target was wired") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "worker execution") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 12), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 0), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_winsize_layout);
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_starter_gap);
    try std.testing.expect(saw_cleanup_handoff);
    try std.testing.expect(saw_remove_handoff);
    try std.testing.expect(saw_driver_test_block);
    try std.testing.expect(saw_validation_matrix);
    try std.testing.expect(saw_tty_handoff);
    try std.testing.expect(saw_sysrq_handoff);
    try std.testing.expect(saw_notifier_handoff);
}

test "phase11 hvc console survey keeps a bounded winsize layout proof" {
    comptime {
        layout_assert.assertSize(WinSize, 8);
        layout_assert.assertAlign(WinSize, 2);
        layout_assert.assertFieldType(WinSize, "ws_row", u16);
        layout_assert.assertFieldType(WinSize, "ws_col", u16);
        layout_assert.assertFieldType(WinSize, "ws_xpixel", u16);
        layout_assert.assertFieldType(WinSize, "ws_ypixel", u16);
        layout_assert.assertOffset(WinSize, "ws_row", 0);
        layout_assert.assertOffset(WinSize, "ws_col", 2);
        layout_assert.assertOffset(WinSize, "ws_xpixel", 4);
        layout_assert.assertOffset(WinSize, "ws_ypixel", 6);
    }
}

test "phase11 hvc console survey note records the winsize checkpoint" {
    const manifest_json = try readFileAlloc(
        std.testing.allocator,
        "zigux/tests/phase11_hvc_console_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const note = try readFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(note, parsed.value.surveyed_commit);
    try expectContains(note, "struct winsize");
    try expectContains(note, "resize boundary");
    try expectContains(note, "small shared-review truthfulness sync");
}

test "phase11 hvc_console survey gate proves validation matrix coverage directly" {
    const matrix = try readFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(matrix);

    try std.testing.expect(std.mem.indexOf(u8, matrix, "PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "zigux/tests/phase11_hvc_cleanup.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "Documentation/zigux/phase11-shared-replay-contract.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "zig build test --build-file zigux/tests/phase11_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "notifier callback boundary") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "deferred callback ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "never-registered path where unregister timing stays false because tty registration never became ready") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "targetless path where unregister timing also stays false because no notifier target was wired") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "do not claim notifier callbacks, khvcd execution, live sysrq dispatch, or host-backed I/O coverage until the Zig surface and tests for those behaviors exist") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "keep this handoff stable while the next follow-through stays inside shared review truthfulness instead of widening into live callback execution") != null);
}

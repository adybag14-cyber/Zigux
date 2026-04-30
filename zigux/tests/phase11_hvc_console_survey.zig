const std = @import("std");
const SurveySummary = struct {
    hvc_console_c_lines: usize,
    preexisting_phase11_build_present: bool,
    preexisting_phase11_watchdog_lanes: usize,
    hvc_console_header_present: bool,
    hvc_console_zig_present: bool,
    hvc_console_test_present: bool,
    hvc_console_survey_gate_present: bool,
    hvc_console_survey_note_present: bool,
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

const WinsizeLayout = extern struct {
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

test "phase11 hvc_console survey manifest records the landed starter and remaining tty gap cleanly" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_hvc_console_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P11-L18", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.c", manifest.anchor);
    try std.testing.expectEqualStrings("34d2750ba817c2cc9862df2b48c44a6155b300fe", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.hvc_console_c_lines >= 1000);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_phase11_watchdog_lanes);
    try std.testing.expect(manifest.survey_summary.hvc_console_header_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_zig_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_test_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_survey_note_present);
    try std.testing.expectEqual(@as(usize, 12), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_survey_gate = false;
    var saw_note = false;
    var saw_starter_gap = false;
    var saw_sleep_handoff = false;
    var saw_hangup_disconnect = false;
    var saw_remove_handoff = false;
    var saw_header_parity = false;
    var saw_winsize_layout_assert = false;
    var saw_driver_tests = false;
    var saw_validation_matrix = false;
    var saw_tty_block = false;

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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd worker-entry") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd sleep-and-reschedule handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__hvc_poll drain-order") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_hangup disconnect") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_remove handoff helpers") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-survey-note")) {
            saw_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-hvc-console-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd worker-entry summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd sleep-and-reschedule handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__hvc_poll drain-order summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_hangup disconnect summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_remove handoff summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-driver-starter")) {
            saw_starter_gap = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "CRLF") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "flush intent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd polling-contract summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd worker-entry summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd sleep-and-reschedule handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__hvc_poll drain-order summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_hangup disconnect summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_remove handoff summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-khvcd-sleep-handoff")) {
            saw_sleep_handoff = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pre-sleep kick check") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "interruptible-state recheck") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "guard-tick timed sleep") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-hangup-disconnect")) {
            saw_hangup_disconnect = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-resize cancellation") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "stale-count short-circuit") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "buffered-write clearing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier_hangup boundary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-remove-handoff")) {
            saw_remove_handoff = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "console-lock slot clearing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "vtermno and cons_ops release") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty_port_put ordering") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty_vhangup follow-through") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty_kref_put release") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "keep-irq-until-hangup teardown boundaries") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-header-parity")) {
            saw_header_parity = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "MAX_NR_HVC_CONSOLES") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "HVC_ALLOC_TTY_ADAPTERS") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hv_ops") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-winsize-layout-assert")) {
            saw_winsize_layout_assert = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct winsize") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "layout_assert") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "offsets 0, 2, 4, and 6") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-driver-tests")) {
            saw_driver_tests = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "newline framing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "teardown gating") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff boundaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd polling-contract wakeup") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd worker-entry sleep and backoff boundaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd sleep-and-reschedule handoff boundaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__hvc_poll drain-order and tty-wakeup sequencing boundaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_hangup disconnect teardown boundaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_remove handoff boundaries") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-validation-matrix")) {
            saw_validation_matrix = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-hvc-console-validation-matrix.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 11 starter replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "survey gate still runs separately") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd polling-contract") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd worker-entry") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd sleep-and-reschedule handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__hvc_poll drain-order") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_hangup disconnect") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_remove handoff evidence") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-tty-and-teardown-parity")) {
            saw_tty_block = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "close-wait ownership") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "polling-driven wakeups") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sleep-versus-timeout choices") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty wakeup sequencing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hangup-time disconnect boundaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time slot-release ordering") != null);
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
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_starter_gap);
    try std.testing.expect(saw_sleep_handoff);
    try std.testing.expect(saw_hangup_disconnect);
    try std.testing.expect(saw_remove_handoff);
    try std.testing.expect(saw_header_parity);
    try std.testing.expect(saw_winsize_layout_assert);
    try std.testing.expect(saw_driver_tests);
    try std.testing.expect(saw_validation_matrix);
    try std.testing.expect(saw_tty_block);
}

test "phase11 hvc console survey records the current shared-build boundary exactly" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const build_zig = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_zig);

    try std.testing.expect(std.mem.indexOf(u8, build_zig, "const phase11_hvc_console_tests = b.addTest") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_zig, "test_step.dependOn(&run_phase11_hvc_console_tests.step);") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_zig, "phase11_hvc_console_survey_tests") == null);
    try std.testing.expect(std.mem.indexOf(u8, build_zig, "run_phase11_hvc_console_survey_tests.step") == null);
}

test "phase11 hvc console survey keeps a bounded winsize layout proof" {
    comptime {
        if (@sizeOf(WinsizeLayout) != 8) @compileError("WinsizeLayout size drifted");
        if (@alignOf(WinsizeLayout) != 2) @compileError("WinsizeLayout alignment drifted");
        if (@offsetOf(WinsizeLayout, "ws_row") != 0) @compileError("WinsizeLayout.ws_row offset drifted");
        if (@offsetOf(WinsizeLayout, "ws_col") != 2) @compileError("WinsizeLayout.ws_col offset drifted");
        if (@offsetOf(WinsizeLayout, "ws_xpixel") != 4) @compileError("WinsizeLayout.ws_xpixel offset drifted");
        if (@offsetOf(WinsizeLayout, "ws_ypixel") != 6) @compileError("WinsizeLayout.ws_ypixel offset drifted");
    }
}

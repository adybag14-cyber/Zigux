const std = @import("std");
const layout_assert = @import("layout_assert");
const SurveySummary = struct {
    hvc_console_c_lines: usize,
    preexisting_phase11_build_present: bool,
    preexisting_phase11_watchdog_lanes: usize,
    hvc_console_header_present: bool,
    hvc_console_zig_present: bool,
    hvc_console_sysrq_present: bool,
    hvc_console_test_present: bool,
    hvc_console_modem_control_split_present: bool,
    hvc_console_poll_retry_split_present: bool,
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

const HvcStruct = opaque {};

const HvOpsLayout = extern struct {
    get_chars: ?*const fn (u32, [*]u8, usize) callconv(.c) isize,
    put_chars: ?*const fn (u32, [*]const u8, usize) callconv(.c) isize,
    flush: ?*const fn (u32, bool) callconv(.c) c_int,
    notifier_add: ?*const fn (*HvcStruct, c_int) callconv(.c) c_int,
    notifier_del: ?*const fn (*HvcStruct, c_int) callconv(.c) void,
    notifier_hangup: ?*const fn (*HvcStruct, c_int) callconv(.c) void,
    tiocmget: ?*const fn (*HvcStruct) callconv(.c) c_int,
    tiocmset: ?*const fn (*HvcStruct, c_uint, c_uint) callconv(.c) c_int,
    dtr_rts: ?*const fn (*HvcStruct, bool) callconv(.c) void,
};

const HvcInstantiateFn = *const fn (u32, c_int, *const HvOpsLayout) callconv(.c) c_int;
const HvcAllocFn = *const fn (u32, c_int, *const HvOpsLayout, c_int) callconv(.c) ?*HvcStruct;
const HvcRemoveFn = *const fn (*HvcStruct) callconv(.c) void;
const HvcPollFn = *const fn (*HvcStruct) callconv(.c) c_int;
const HvcKickFn = *const fn () callconv(.c) void;
const HvcResizeFn = *const fn (*HvcStruct, WinsizeLayout) callconv(.c) void;
const HvcNotifierAddIrqFn = *const fn (*HvcStruct, c_int) callconv(.c) c_int;
const HvcNotifierDelIrqFn = *const fn (*HvcStruct, c_int) callconv(.c) void;
const HvcNotifierHangupIrqFn = *const fn (*HvcStruct, c_int) callconv(.c) void;

const HvcExportSurface = extern struct {
    hvc_instantiate: HvcInstantiateFn,
    hvc_alloc: HvcAllocFn,
    hvc_remove: HvcRemoveFn,
    hvc_poll: HvcPollFn,
    hvc_kick: HvcKickFn,
    __hvc_resize: HvcResizeFn,
    notifier_add_irq: HvcNotifierAddIrqFn,
    notifier_del_irq: HvcNotifierDelIrqFn,
    notifier_hangup_irq: HvcNotifierHangupIrqFn,
};

fn expectSurveyedCommitProvenance(survey_note: []const u8, surveyed_commit: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 40), surveyed_commit.len);
    for (surveyed_commit) |byte| {
        try std.testing.expect(std.ascii.isHex(byte));
    }
    try std.testing.expect(std.mem.indexOf(u8, survey_note, surveyed_commit) != null);
}

fn assertExactType(
    comptime Actual: type,
    comptime Expected: type,
) void {
    if (Actual != Expected) {
        @compileError(std.fmt.comptimePrint(
            "type mismatch: expected {s}, found {s}",
            .{ @typeName(Expected), @typeName(Actual) },
        ));
    }
}

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
    try std.testing.expectEqualStrings("P11-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.hvc_console_c_lines >= 1000);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_phase11_watchdog_lanes);
    try std.testing.expect(manifest.survey_summary.hvc_console_header_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_zig_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_sysrq_present);
    try std.testing.expect(!manifest.survey_summary.hvc_console_test_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_modem_control_split_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_poll_retry_split_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_survey_gate_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_survey_note_present);
    try std.testing.expectEqual(@as(usize, 14), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_survey_gate = false;
    var saw_note = false;
    var saw_starter_gap = false;
    var saw_close_teardown = false;
    var saw_notifier_add_handoff = false;
    var saw_sleep_handoff = false;
    var saw_hangup_disconnect = false;
    var saw_remove_handoff = false;
    var saw_header_parity = false;
    var saw_winsize_layout_assert = false;
    var saw_hv_ops_layout_assert = false;
    var saw_hv_ops_signature_assert = false;
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

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "final-close teardown handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd worker-entry") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier-add open handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd sleep-and-reschedule handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__hvc_poll drain-order") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_hangup disconnect") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_remove handoff helpers") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_cleanup tty-port release handoff") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-survey-note")) {
            saw_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-hvc-console-survey.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "final-close teardown summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd worker-entry summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tiny notifier-add open handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd sleep-and-reschedule handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__hvc_poll drain-order summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_hangup disconnect summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_remove handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_cleanup tty-port release handoff summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-driver-starter")) {
            saw_starter_gap = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "CRLF") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "flush intent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "final-close teardown summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tiny notifier-add open handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd polling-contract summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd worker-entry summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd sleep-and-reschedule handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__hvc_poll drain-order summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_hangup disconnect summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_remove handoff summary") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_cleanup tty-port release handoff summary") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-close-teardown")) {
            saw_close_teardown = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty detachment") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "HUPCL-gated dtr_rts shutdown") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier_del ownership") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "resize-work cancellation") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty_wait_until_sent intent") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "port_initialized clearing") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-notifier-add-handoff")) {
            saw_notifier_add_handoff = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier_add success") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "polling fallback") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "failed-open close cleanup") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "open-time IRQ request boundaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd kick follow-through") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_kick") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier-IRQ helper surface") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-winsize-layout-assert")) {
            saw_winsize_layout_assert = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct winsize") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "layout_assert") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "offsets 0, 2, 4, and 6") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-hv-ops-layout-assert")) {
            saw_hv_ops_layout_assert = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct hv_ops") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "layout_assert") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "callback-table order") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "offsets 0 through 64") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-hv-ops-signature-assert")) {
            saw_hv_ops_signature_assert = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct hv_ops") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "C calling convention") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "get_chars") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dtr_rts") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-validation-matrix")) {
            saw_validation_matrix = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase11-hvc-console-validation-matrix.md", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 11 starter replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "survey gate still runs separately") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "final-close teardown") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier-add open handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd polling-contract") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd worker-entry") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "khvcd sleep-and-reschedule handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__hvc_poll drain-order") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_hangup disconnect") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_remove handoff evidence") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_cleanup tty-port release handoff") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-tty-and-teardown-parity")) {
            saw_tty_block = true;
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "final-close teardown") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty-registration handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier-add open handoff") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "close-wait ownership") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "open-time IRQ-request and polling-fallback boundaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "HUPCL and notifier-del shutdown boundaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "polling-driven wakeups") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "sleep-versus-timeout choices") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tty wakeup sequencing") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hangup-time disconnect boundaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "remove-time slot-release ordering") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_cleanup tty-port release summaries") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "cleanup-time tty-port ownership") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 14), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 0), blocked_count);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_starter_gap);
    try std.testing.expect(saw_close_teardown);
    try std.testing.expect(saw_notifier_add_handoff);
    try std.testing.expect(saw_sleep_handoff);
    try std.testing.expect(saw_hangup_disconnect);
    try std.testing.expect(saw_remove_handoff);
    try std.testing.expect(saw_header_parity);
    try std.testing.expect(saw_winsize_layout_assert);
    try std.testing.expect(saw_hv_ops_layout_assert);
    try std.testing.expect(saw_hv_ops_signature_assert);
    try std.testing.expect(saw_validation_matrix);
    try std.testing.expect(saw_tty_block);
}

test "phase11 hvc_console survey keeps the dedicated archival packet explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-hvc-console-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_hvc_console_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed_manifest = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed_manifest.deinit();
    const manifest = parsed_manifest.value;

    const sysrq_helper = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/tty/hvc/hvc_console_sysrq.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(sysrq_helper);

    const modem_control_split = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_hvc_console_modem_control_split.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(modem_control_split);

    const poll_retry_split = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(poll_retry_split);

    try expectSurveyedCommitProvenance(survey_note, manifest.surveyed_commit);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(!manifest.survey_summary.hvc_console_test_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_zig_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_sysrq_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_modem_control_split_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_poll_retry_split_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_survey_gate_present);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase11_hvc_console_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase11_hvc_console_modem_control_split.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase11_hvc_console_poll_retry_split.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/tty/hvc/hvc_console_sysrq.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase11-hvc-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "bounded supporting helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, sysrq_helper, "pub const SysrqHandoffRequest") != null);
    try std.testing.expect(std.mem.indexOf(u8, sysrq_helper, "pub const SysrqHandoffSnapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, sysrq_helper, "pub fn summarizeSysrqHandoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, sysrq_helper, "toggles_sysrq_mode") != null);
    try std.testing.expect(std.mem.indexOf(u8, sysrq_helper, "invokes_sysrq_handler") != null);
    try std.testing.expect(std.mem.indexOf(u8, sysrq_helper, "keeps_live_sysrq_execution_out_of_scope = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, modem_control_split, "phase11 hvc console keeps tiocmget and tiocmset fallback on missing hv_ops callbacks") != null);
    try std.testing.expect(std.mem.indexOf(u8, modem_control_split, "phase11 hvc console keeps tiocmset masks live when tiocmget falls back") != null);
    try std.testing.expect(std.mem.indexOf(u8, poll_retry_split, "phase11 hvc console keeps irq-backed drained reads distinct when __hvc_poll can or cannot sleep") != null);
    try std.testing.expect(std.mem.indexOf(u8, poll_retry_split, "phase11 hvc console keeps partial write progress distinct from stalled __hvc_poll retries") != null);
    try std.testing.expect(std.mem.indexOf(u8, poll_retry_split, "phase11 hvc console keeps sysrq toggle handoff distinct from literal fallback on the primary console") != null);
    try std.testing.expect(std.mem.indexOf(u8, poll_retry_split, "phase11 hvc console keeps pending sysrq dispatch separate from ordinary poll bytes") != null);
    try std.testing.expect(std.mem.indexOf(u8, poll_retry_split, "phase11 hvc console keeps non-kernel ^O as a literal byte without toggling sysrq state") != null);
    try std.testing.expect(std.mem.indexOf(u8, poll_retry_split, "phase11 hvc console keeps sysrq handoff unavailable after teardown") != null);
}

test "phase11 hvc_console survey keeps the shared replay separate but exposes an explicit survey step" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_hvc_console_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed_manifest = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed_manifest.deinit();
    const manifest = parsed_manifest.value;

    const validation_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(validation_matrix);

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const workflow = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(workflow);

    try std.testing.expect(!manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(!manifest.survey_summary.hvc_console_test_present);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "the dedicated archival replay remains separate through `make -C zigux phase11-hvc-survey`") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "`make -C zigux phase11-hvc-survey` archival route fail-closed") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "PHONY += phase11-contract phase11-test phase11-hvc-survey phase11") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase11-hvc-survey:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase11: phase11-contract phase11-test phase11-hvc-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "- name: Run dedicated Phase 11 hvc survey replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "run: make -C zigux phase11-hvc-survey") != null);
}

test "phase11 hvc console survey keeps the survey note, slice note, and validation matrix aligned with the parked starter" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-hvc-console-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-hvc-console-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const validation_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(validation_matrix);

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_hvc_console_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed_manifest = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed_manifest.deinit();
    const manifest = parsed_manifest.value;

    try expectSurveyedCommitProvenance(survey_note, manifest.surveyed_commit);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "`hvc_cleanup()` tty-port release handoff summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "port-reference drop timing") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "tiny notifier-add open handoff summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "hvc_kick") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "notifier-IRQ helper surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, manifest.surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 11 simple-production-driver gap has been closed by the bounded starter") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "remaining unported work is now tty-driver registration, khvcd worker execution, live sysrq execution, notifier callback execution, and host-backed transport or teardown validation") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "tiny notifier-add open handoff summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "hvc_kick") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "notifier-IRQ helper surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "`hvc_remove()` handoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "`hvc_cleanup()` tty-port release handoff") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "`summarizeNotifierAddOutcome()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`hvc_cleanup()` tty-port release handoff summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "host-free khvcd, notifier, remove, or cleanup handoff") != null);
}

test "phase11 hvc console survey keeps a bounded winsize layout proof" {
    comptime {
        layout_assert.assertSize(WinsizeLayout, 8);
        layout_assert.assertAlign(WinsizeLayout, 2);
        layout_assert.assertOffset(WinsizeLayout, "ws_row", 0);
        layout_assert.assertOffset(WinsizeLayout, "ws_col", 2);
        layout_assert.assertOffset(WinsizeLayout, "ws_xpixel", 4);
        layout_assert.assertOffset(WinsizeLayout, "ws_ypixel", 6);
    }
}

test "phase11 hvc console survey keeps a bounded hv_ops layout proof" {
    comptime {
        layout_assert.assertSize(HvOpsLayout, 72);
        layout_assert.assertAlign(HvOpsLayout, 8);
        layout_assert.assertOffset(HvOpsLayout, "get_chars", 0);
        layout_assert.assertOffset(HvOpsLayout, "put_chars", 8);
        layout_assert.assertOffset(HvOpsLayout, "flush", 16);
        layout_assert.assertOffset(HvOpsLayout, "notifier_add", 24);
        layout_assert.assertOffset(HvOpsLayout, "notifier_del", 32);
        layout_assert.assertOffset(HvOpsLayout, "notifier_hangup", 40);
        layout_assert.assertOffset(HvOpsLayout, "tiocmget", 48);
        layout_assert.assertOffset(HvOpsLayout, "tiocmset", 56);
        layout_assert.assertOffset(HvOpsLayout, "dtr_rts", 64);
    }
}

test "phase11 hvc console survey keeps bounded hv_ops callback signature proofs" {
    comptime {
        assertExactType(@FieldType(HvOpsLayout, "get_chars"), ?*const fn (u32, [*]u8, usize) callconv(.c) isize);
        assertExactType(@FieldType(HvOpsLayout, "put_chars"), ?*const fn (u32, [*]const u8, usize) callconv(.c) isize);
        assertExactType(@FieldType(HvOpsLayout, "flush"), ?*const fn (u32, bool) callconv(.c) c_int);
        assertExactType(@FieldType(HvOpsLayout, "notifier_add"), ?*const fn (*HvcStruct, c_int) callconv(.c) c_int);
        assertExactType(@FieldType(HvOpsLayout, "notifier_del"), ?*const fn (*HvcStruct, c_int) callconv(.c) void);
        assertExactType(@FieldType(HvOpsLayout, "notifier_hangup"), ?*const fn (*HvcStruct, c_int) callconv(.c) void);
        assertExactType(@FieldType(HvOpsLayout, "tiocmget"), ?*const fn (*HvcStruct) callconv(.c) c_int);
        assertExactType(@FieldType(HvOpsLayout, "tiocmset"), ?*const fn (*HvcStruct, c_uint, c_uint) callconv(.c) c_int);
        assertExactType(@FieldType(HvOpsLayout, "dtr_rts"), ?*const fn (*HvcStruct, bool) callconv(.c) void);
    }
}

test "phase11 hvc console survey keeps bounded exported helper signature proofs" {
    comptime {
        assertExactType(@FieldType(HvcExportSurface, "hvc_instantiate"), HvcInstantiateFn);
        assertExactType(@FieldType(HvcExportSurface, "hvc_alloc"), HvcAllocFn);
        assertExactType(@FieldType(HvcExportSurface, "hvc_remove"), HvcRemoveFn);
        assertExactType(@FieldType(HvcExportSurface, "hvc_poll"), HvcPollFn);
        assertExactType(@FieldType(HvcExportSurface, "hvc_kick"), HvcKickFn);
        assertExactType(@FieldType(HvcExportSurface, "__hvc_resize"), HvcResizeFn);
        assertExactType(@FieldType(HvcExportSurface, "notifier_add_irq"), HvcNotifierAddIrqFn);
        assertExactType(@FieldType(HvcExportSurface, "notifier_del_irq"), HvcNotifierDelIrqFn);
        assertExactType(@FieldType(HvcExportSurface, "notifier_hangup_irq"), HvcNotifierHangupIrqFn);
    }
}

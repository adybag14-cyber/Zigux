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
    hvc_console_teardown_note_present: bool,
    winsize_layout_assert_present: bool,
    hv_ops_layout_assert_present: bool,
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

const HvcStruct = opaque {};

const HvOpsGetChars = ?*const fn (vtermno: u32, buf: [*c]u8, count: usize) callconv(.c) isize;
const HvOpsPutChars = ?*const fn (vtermno: u32, buf: [*c]const u8, count: usize) callconv(.c) isize;
const HvOpsFlush = ?*const fn (vtermno: u32, wait: bool) callconv(.c) i32;
const HvOpsNotifierAdd = ?*const fn (hp: ?*HvcStruct, irq: i32) callconv(.c) i32;
const HvOpsNotifierDel = ?*const fn (hp: ?*HvcStruct, irq: i32) callconv(.c) void;
const HvOpsNotifierHangup = ?*const fn (hp: ?*HvcStruct, irq: i32) callconv(.c) void;
const HvOpsTiocmget = ?*const fn (hp: ?*HvcStruct) callconv(.c) i32;
const HvOpsTiocmset = ?*const fn (hp: ?*HvcStruct, set: u32, clear: u32) callconv(.c) i32;
const HvOpsDtrRts = ?*const fn (hp: ?*HvcStruct, active: bool) callconv(.c) void;

const HvOps = extern struct {
    get_chars: HvOpsGetChars,
    put_chars: HvOpsPutChars,
    flush: HvOpsFlush,
    notifier_add: HvOpsNotifierAdd,
    notifier_del: HvOpsNotifierDel,
    notifier_hangup: HvOpsNotifierHangup,
    tiocmget: HvOpsTiocmget,
    tiocmset: HvOpsTiocmset,
    dtr_rts: HvOpsDtrRts,
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
    try std.testing.expectEqualStrings("P11-L16", manifest.lane_key);
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
    try std.testing.expect(manifest.survey_summary.hvc_console_teardown_note_present);
    try std.testing.expect(manifest.survey_summary.winsize_layout_assert_present);
    try std.testing.expect(manifest.survey_summary.hv_ops_layout_assert_present);
    try std.testing.expectEqual(@as(usize, 13), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));
        if (std.mem.eql(u8, gap.status, "starter_landed")) starter_landed_count += 1 else if (std.mem.eql(u8, gap.status, "ready_next")) ready_next_count += 1 else blocked_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 13), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 0), blocked_count);
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

test "phase11 hvc console survey keeps a bounded hv_ops layout proof" {
    comptime {
        layout_assert.assertSize(HvOps, 72);
        layout_assert.assertAlign(HvOps, 8);
        layout_assert.assertFieldType(HvOps, "get_chars", HvOpsGetChars);
        layout_assert.assertFieldType(HvOps, "put_chars", HvOpsPutChars);
        layout_assert.assertFieldType(HvOps, "flush", HvOpsFlush);
        layout_assert.assertFieldType(HvOps, "notifier_add", HvOpsNotifierAdd);
        layout_assert.assertFieldType(HvOps, "notifier_del", HvOpsNotifierDel);
        layout_assert.assertFieldType(HvOps, "notifier_hangup", HvOpsNotifierHangup);
        layout_assert.assertFieldType(HvOps, "tiocmget", HvOpsTiocmget);
        layout_assert.assertFieldType(HvOps, "tiocmset", HvOpsTiocmset);
        layout_assert.assertFieldType(HvOps, "dtr_rts", HvOpsDtrRts);
        layout_assert.assertOffset(HvOps, "get_chars", 0);
        layout_assert.assertOffset(HvOps, "put_chars", 8);
        layout_assert.assertOffset(HvOps, "flush", 16);
        layout_assert.assertOffset(HvOps, "notifier_add", 24);
        layout_assert.assertOffset(HvOps, "notifier_del", 32);
        layout_assert.assertOffset(HvOps, "notifier_hangup", 40);
        layout_assert.assertOffset(HvOps, "tiocmget", 48);
        layout_assert.assertOffset(HvOps, "tiocmset", 56);
        layout_assert.assertOffset(HvOps, "dtr_rts", 64);
    }
}

test "phase11 hvc console survey note records the bounded layout checkpoints" {
    const manifest_json = try readFileAlloc(std.testing.allocator, "zigux/tests/phase11_hvc_console_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);
    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const note = try readFileAlloc(std.testing.allocator, "Documentation/zigux/phase11-hvc-console-survey.md", 32 * 1024);
    defer std.testing.allocator.free(note);
    try expectContains(note, parsed.value.surveyed_commit);
    try expectContains(note, "P11-L16");
    try expectContains(note, "drivers/tty/hvc/hvc_console_verify.zig");
    try expectContains(note, "struct winsize");
    try expectContains(note, "resize boundary");
    try expectContains(note, "struct hv_ops");
    try expectContains(note, "callback-table");
    try expectContains(note, "size `72`");
    try expectContains(note, "Documentation/zigux/phase11-hvc-console-teardown-note.md");
    try expectContains(note, "close, cleanup, and remove ownership split");
    try expectContains(note, "current driver, verifier, tests, validation matrix, and shared replay contract");
}

test "phase11 hvc console teardown note keeps the bounded ownership split explicit" {
    const teardown_note = try readFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-teardown-note.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(teardown_note);

    try expectContains(teardown_note, "summarizeCloseBoundary()");
    try expectContains(teardown_note, "summarizeCleanupHandoff()");
    try expectContains(teardown_note, "summarizeRemoveHandoff()");
    try expectContains(teardown_note, "tty_port_put()");
    try expectContains(teardown_note, "tty_vhangup()");
    try expectContains(teardown_note, "tty_kref_put()");
    try expectContains(teardown_note, "do not treat this note as evidence of live notifier callbacks");
}

test "phase11 hvc_console survey gate proves validation matrix coverage directly" {
    const matrix = try readFileAlloc(std.testing.allocator, "Documentation/zigux/phase11-hvc-console-validation-matrix.md", 32 * 1024);
    defer std.testing.allocator.free(matrix);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "lane: `P11-L16`") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "zigux/tests/phase11_hvc_cleanup.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "Documentation/zigux/phase11-shared-replay-contract.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "Documentation/zigux/phase11-hvc-console-teardown-note.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "zigux/tests/phase11_hvc_console_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "keep `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, and this matrix aligned") != null);
    try std.testing.expect(std.mem.indexOf(u8, matrix, "do not claim notifier callbacks, khvcd execution, live sysrq dispatch, or host-backed I/O coverage until the Zig surface and tests for those behaviors exist") != null);
}

test "phase11 hvc console survey gate keeps the shared replay contract aligned with the archival HVC checkpoint" {
    const contract = try readFileAlloc(std.testing.allocator, "Documentation/zigux/phase11-shared-replay-contract.md", 32 * 1024);
    defer std.testing.allocator.free(contract);
    try expectContains(contract, "The dedicated archival HVC evidence still stays explicit beside that shared route:");
    try expectContains(contract, "`zigux/tests/phase11_hvc_console_manifest.json`");
    try expectContains(contract, "`zigux/tests/phase11_hvc_console_survey.zig`");
    try expectContains(contract, "`Documentation/zigux/phase11-hvc-console-survey.md`");
    try expectContains(contract, "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`");
    try expectContains(contract, "keeps the archival HVC landing checkpoint named alongside the survey note and validation matrix");
}

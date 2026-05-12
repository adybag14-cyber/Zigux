const std = @import("std");
const layout_assert = @import("layout_assert");

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

const HvcStruct = opaque {};

const HvOps = extern struct {
    get_chars: ?*const fn (vtermno: u32, buf: [*]u8, count: c_int) callconv(.c) c_int,
    put_chars: ?*const fn (vtermno: u32, buf: [*]const u8, count: c_int) callconv(.c) c_int,
    flush: ?*const fn (vtermno: u32, wait: bool) callconv(.c) c_int,
    notifier_add: ?*const fn (hp: *HvcStruct, irq: c_int) callconv(.c) c_int,
    notifier_del: ?*const fn (hp: *HvcStruct, irq: c_int) callconv(.c) void,
    notifier_hangup: ?*const fn (hp: *HvcStruct, irq: c_int) callconv(.c) void,
    tiocmget: ?*const fn (hp: *HvcStruct) callconv(.c) c_int,
    tiocmset: ?*const fn (hp: *HvcStruct, set: c_uint, clear: c_uint) callconv(.c) c_int,
    dtr_rts: ?*const fn (hp: *HvcStruct, active: bool) callconv(.c) void,
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

test "phase11 shared header parity survey manifest records the maintained packet cleanly" {
    const manifest_json = try readFileAlloc(std.testing.allocator, "zigux/tests/phase11_uapi_header_parity_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P11-L18", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839", manifest.surveyed_commit);
    try std.testing.expectEqualStrings(
        "include/uapi/linux/watchdog.h + include/uapi/asm-generic/termios.h + drivers/tty/hvc/hvc_console.h",
        manifest.anchor,
    );
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
            try expectContains(gap.why_now, "notifier_hangup_irq");
        }
    }

    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_watchdog_layout);
    try std.testing.expect(saw_winsize_layout);
    try std.testing.expect(saw_export_surface);
}

test "phase11 shared header parity survey keeps a bounded watchdog_info layout proof" {
    layout_assert.assertSize(WatchdogInfo, 40);
    layout_assert.assertAlign(WatchdogInfo, 4);
    layout_assert.assertFieldType(WatchdogInfo, "options", u32);
    layout_assert.assertFieldType(WatchdogInfo, "firmware_version", u32);
    layout_assert.assertFieldType(WatchdogInfo, "identity", [32]u8);
    layout_assert.assertOffset(WatchdogInfo, "options", 0);
    layout_assert.assertOffset(WatchdogInfo, "firmware_version", 4);
    layout_assert.assertOffset(WatchdogInfo, "identity", 8);
}

test "phase11 shared header parity survey keeps a bounded winsize layout proof" {
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

test "phase11 shared header parity survey keeps a bounded hv_ops callback-table layout proof" {
    layout_assert.assertSize(HvOps, 72);
    layout_assert.assertAlign(HvOps, 8);
    layout_assert.assertFieldType(HvOps, "get_chars", ?*const fn (vtermno: u32, buf: [*]u8, count: c_int) callconv(.c) c_int);
    layout_assert.assertFieldType(HvOps, "put_chars", ?*const fn (vtermno: u32, buf: [*]const u8, count: c_int) callconv(.c) c_int);
    layout_assert.assertFieldType(HvOps, "flush", ?*const fn (vtermno: u32, wait: bool) callconv(.c) c_int);
    layout_assert.assertFieldType(HvOps, "notifier_add", ?*const fn (hp: *HvcStruct, irq: c_int) callconv(.c) c_int);
    layout_assert.assertFieldType(HvOps, "notifier_del", ?*const fn (hp: *HvcStruct, irq: c_int) callconv(.c) void);
    layout_assert.assertFieldType(HvOps, "notifier_hangup", ?*const fn (hp: *HvcStruct, irq: c_int) callconv(.c) void);
    layout_assert.assertFieldType(HvOps, "tiocmget", ?*const fn (hp: *HvcStruct) callconv(.c) c_int);
    layout_assert.assertFieldType(HvOps, "tiocmset", ?*const fn (hp: *HvcStruct, set: c_uint, clear: c_uint) callconv(.c) c_int);
    layout_assert.assertFieldType(HvOps, "dtr_rts", ?*const fn (hp: *HvcStruct, active: bool) callconv(.c) void);
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

test "phase11 shared header parity survey keeps the note pinned to the manifest provenance" {
    const manifest_json = try readFileAlloc(std.testing.allocator, "zigux/tests/phase11_uapi_header_parity_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const note = try readFileAlloc(std.testing.allocator, "Documentation/zigux/phase11-uapi-header-parity-survey.md", 32 * 1024);
    defer std.testing.allocator.free(note);

    try expectContains(note, parsed.value.surveyed_commit);
    try expectContains(note, "PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_restored");
    try expectContains(note, "lane: `P11-L18`");
    try expectContains(note, "phase11-dw-wdt-watchdog-info-layout-assert");
    try expectContains(note, "phase11-hvc-console-winsize-layout-assert");
    try expectContains(note, "phase11-hvc-console-export-signature-assert");
    try expectContains(note, "phase11-uapi-header-parity-surface");
    try expectContains(note, "notifier_hangup_irq");
    try expectContains(note, "dedicated `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all` step");
    try expectContains(note, "rather than the shared `test` step");
}

test "phase11 shared header parity survey keeps shared replay markers explicit without reviving removed validator claims" {
    const contract = try readFileAlloc(std.testing.allocator, "Documentation/zigux/phase11-shared-replay-contract.md", 64 * 1024);
    defer std.testing.allocator.free(contract);

    try expectContains(contract, "PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful");
    try expectContains(contract, "zigux/tests/phase11_build.zig");
    try expectContains(contract, "zigux/tests/phase11_uapi_header_parity_survey.zig");
    try expectContains(contract, "zigux/tests/phase11_hvc_console_survey.zig");
    try expectContains(contract, "no shared `validate-phase11.py`");
    try expectContains(contract, "no shared `make -C zigux phase11-validate` target on `master`");
    try expectContains(contract, "The dedicated archival HVC evidence still stays explicit beside that shared route:");
}

test "phase11 shared header parity survey keeps the exported hvc header declarations explicit" {
    const hvc_header = try readFileAlloc(std.testing.allocator, "drivers/tty/hvc/hvc_console.h", 64 * 1024);
    defer std.testing.allocator.free(hvc_header);

    try expectContains(hvc_header, "struct hv_ops {");
    try expectContains(hvc_header, "int (*get_chars)(uint32_t vtermno, char *buf, int count);");
    try expectContains(hvc_header, "int (*put_chars)(uint32_t vtermno, const char *buf, int count);");
    try expectContains(hvc_header, "int (*flush)(uint32_t vtermno, bool wait);");
    try expectContains(hvc_header, "int (*notifier_add)(struct hvc_struct *hp, int irq);");
    try expectContains(hvc_header, "void (*notifier_del)(struct hvc_struct *hp, int irq);");
    try expectContains(hvc_header, "void (*notifier_hangup)(struct hvc_struct *hp, int irq);");
    try expectContains(hvc_header, "int (*tiocmget)(struct hvc_struct *hp);");
    try expectContains(hvc_header, "int (*tiocmset)(struct hvc_struct *hp, unsigned int set, unsigned int clear);");
    try expectContains(hvc_header, "void (*dtr_rts)(struct hvc_struct *hp, bool active);");
    try expectContains(hvc_header, "MAX_NR_HVC_CONSOLES");
    try expectContains(hvc_header, "HVC_ALLOC_TTY_ADAPTERS");
    try expectContains(hvc_header, "extern int hvc_instantiate(uint32_t vtermno, int index,");
    try expectContains(hvc_header, "extern struct hvc_struct * hvc_alloc(uint32_t vtermno, int data,");
    try expectContains(hvc_header, "extern void hvc_remove(struct hvc_struct *hp);");
    try expectContains(hvc_header, "int hvc_poll(struct hvc_struct *hp);");
    try expectContains(hvc_header, "void hvc_kick(void);");
    try expectContains(hvc_header, "extern void __hvc_resize(struct hvc_struct *hp, struct winsize ws);");
    try expectContains(hvc_header, "extern int notifier_add_irq(struct hvc_struct *hp, int data);");
    try expectContains(hvc_header, "extern void notifier_del_irq(struct hvc_struct *hp, int data);");
    try expectContains(hvc_header, "extern void notifier_hangup_irq(struct hvc_struct *hp, int data);");
}

test "phase11 shared header parity survey keeps the shared build hook explicit" {
    const build_file = try readFileAlloc(std.testing.allocator, "zigux/tests/phase11_build.zig", 64 * 1024);
    defer std.testing.allocator.free(build_file);

    try expectContains(build_file, "phase11_uapi_header_parity_survey.zig");
    try expectContains(build_file, "phase11-uapi-header-parity-survey-tests");
    try expectContains(build_file, "phase11-hvc-console-survey-tests");
    try expectContains(build_file, "test_step.dependOn(&run_phase11_uapi_header_parity_survey_tests.step);");
    try expectContains(build_file, "hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);");
    try expectContains(build_file, "phase11_uapi_header_parity_survey_module.addImport(\"layout_assert\", layout_assert_module);");
}

const std = @import("std");
const hvc_console = @import("hvc_console");
const layout_assert = @import("layout_assert");

const SurveySummary = struct {
    preexisting_phase11_build_present: bool,
    phase11_build_inventory_present: bool,
    watchdog_uapi_header_present: bool,
    watchdog_core_header_present: bool,
    termios_uapi_header_present: bool,
    hvc_console_header_present: bool,
    hvc_console_header_snapshot_present: bool,
    hvc_console_validation_matrix_present: bool,
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

const BuildInventory = struct {
    build_test_names: []const []const u8,
    shared_test_depend_steps: []const []const u8,
    module_root_source_files: []const ModuleRootSourceFile,
    module_imports: []const ModuleImport,
    test_root_modules: []const TestRootModule,
    forbidden_markers: []const []const u8,
    dedicated_survey_replays: []const []const u8,
    shared_split_replays: []const SharedSplitReplay,
    shared_adjunct_replays: []const SharedAdjunctReplay,
    shared_replay_markers: []const SharedReplayMarker,
};

const ModuleRootSourceFile = struct {
    module: []const u8,
    path: []const u8,
};

const ModuleImport = struct {
    module: []const u8,
    import_name: []const u8,
    imported_module: []const u8,
};

const TestRootModule = struct {
    @"test": []const u8,
    root_module: []const u8,
};

const SharedSplitReplay = struct {
    @"test": []const u8,
    path: []const u8,
};

const SharedAdjunctReplay = struct {
    @"test": []const u8,
    path: []const u8,
};

const SharedReplayMarker = struct {
    path: []const u8,
    marker: []const u8,
};

const WatchdogInfoLayout = extern struct {
    options: u32,
    firmware_version: u32,
    identity: [32]u8,
};

const WinsizeLayout = extern struct {
    ws_row: u16,
    ws_col: u16,
    ws_xpixel: u16,
    ws_ypixel: u16,
};

const HvcStruct = opaque {};

const HvcInstantiateFn = *const fn (u32, c_int, *const HvOpsLayout) callconv(.c) c_int;
const HvcAllocFn = *const fn (u32, c_int, *const HvOpsLayout, c_int) callconv(.c) ?*HvcStruct;
const HvcRemoveFn = *const fn (*HvcStruct) callconv(.c) void;
const HvcPollFn = *const fn (*HvcStruct) callconv(.c) c_int;
const HvcKickFn = *const fn () callconv(.c) void;
const HvcResizeFn = *const fn (*HvcStruct, WinsizeLayout) callconv(.c) void;
const HvcNotifierAddIrqFn = *const fn (*HvcStruct, c_int) callconv(.c) c_int;
const HvcNotifierDelIrqFn = *const fn (*HvcStruct, c_int) callconv(.c) void;
const HvcNotifierHangupIrqFn = *const fn (*HvcStruct, c_int) callconv(.c) void;

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
        std.mem.eql(u8, status, "ready_next");
}

fn countHvcHeaderExports(snapshot: hvc_console.HeaderParitySnapshot) usize {
    return @intFromBool(snapshot.exports_instantiate) +
        @intFromBool(snapshot.exports_alloc) +
        @intFromBool(snapshot.exports_remove) +
        @intFromBool(snapshot.exports_poll) +
        @intFromBool(snapshot.exports_resize) +
        @intFromBool(snapshot.exports_kick) +
        @intFromBool(snapshot.exports_notifier_add_irq) +
        @intFromBool(snapshot.exports_notifier_del_irq) +
        @intFromBool(snapshot.exports_notifier_hangup_irq);
}

fn countHvOpsHeaderSurface(surface: hvc_console.HvOpsHeaderSurface) usize {
    return @intFromBool(surface.has_get_chars) +
        @intFromBool(surface.has_put_chars) +
        @intFromBool(surface.has_flush) +
        @intFromBool(surface.has_notifier_add) +
        @intFromBool(surface.has_notifier_del) +
        @intFromBool(surface.has_notifier_hangup) +
        @intFromBool(surface.has_tiocmget) +
        @intFromBool(surface.has_tiocmset) +
        @intFromBool(surface.has_dtr_rts);
}

test "phase11 shared header parity manifest records the bounded layout checkpoints" {
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
    try std.testing.expectEqualStrings("P11-L17", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 11", manifest.phase);
    try std.testing.expectEqualStrings("1851d34766b4bc833344b3be89e4f079234212fa", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("include/uapi/linux/watchdog.h and include/uapi/asm-generic/termios.h", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_build_present);
    try std.testing.expect(manifest.survey_summary.phase11_build_inventory_present);
    try std.testing.expect(manifest.survey_summary.watchdog_uapi_header_present);
    try std.testing.expect(manifest.survey_summary.watchdog_core_header_present);
    try std.testing.expect(manifest.survey_summary.termios_uapi_header_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_header_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_header_snapshot_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_validation_matrix_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_survey_note_present);
    try std.testing.expect(manifest.survey_summary.dw_wdt_manifest_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_survey_note_present);
    try std.testing.expect(manifest.survey_summary.hvc_console_manifest_present);
    try std.testing.expectEqual(@as(usize, 9), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_note = false;
    var saw_gate = false;
    var saw_dw_boundary = false;
    var saw_hvc_boundary = false;
    var saw_hvc_snapshot_check = false;
    var saw_watchdog_layout_checkpoint = false;
    var saw_winsize_layout_checkpoint = false;
    var saw_hvc_export_signature_assert = false;
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_kick()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier_*_irq()") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-header-snapshot-check")) {
            saw_hvc_snapshot_check = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_uapi_header_parity_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_console.zig") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "default notifier_*_irq() helper exports") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hv_ops callback booleans") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "callback-signature proofs") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-dw-wdt-watchdog-info-layout-assert")) {
            saw_watchdog_layout_checkpoint = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_uapi_header_parity_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "layout_assert") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "size, alignment, exact field types, and field offsets") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-winsize-layout-assert")) {
            saw_winsize_layout_checkpoint = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_uapi_header_parity_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct winsize") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "exact field types") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "ws_row") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase11-hvc-console-export-signature-assert")) {
            saw_hvc_export_signature_assert = true;
            try std.testing.expectEqualStrings("zigux/tests/phase11_uapi_header_parity_survey.zig", gap.zigux_destination);
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hvc_instantiate()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "__hvc_resize()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "notifier_*_irq()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "C calling convention") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "struct winsize") != null);
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

    try std.testing.expectEqual(@as(usize, 8), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_gate);
    try std.testing.expect(saw_dw_boundary);
    try std.testing.expect(saw_hvc_boundary);
    try std.testing.expect(saw_hvc_snapshot_check);
    try std.testing.expect(saw_watchdog_layout_checkpoint);
    try std.testing.expect(saw_winsize_layout_checkpoint);
    try std.testing.expect(saw_hvc_export_signature_assert);
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

    const termios_uapi_header = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "include/uapi/asm-generic/termios.h",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(termios_uapi_header);

    const hvc_header = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/tty/hvc/hvc_console.h",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(hvc_header);
    const hvc_zig = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "drivers/tty/hvc/hvc_console.zig",
        std.testing.allocator,
        .limited(40 * 1024),
    );
    defer std.testing.allocator.free(hvc_zig);

    const hvc_validation_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(hvc_validation_matrix);

    const hvc_survey = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_hvc_console_survey.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(hvc_survey);

    const phase11_build_inventory = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase11_build_inventory.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase11_build_inventory);
    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase11_uapi_header_parity_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);
    const parsed_inventory = try std.json.parseFromSlice(
        BuildInventory,
        std.testing.allocator,
        phase11_build_inventory,
        .{},
    );
    defer parsed_inventory.deinit();
    const inventory = parsed_inventory.value;

    const parsed_manifest = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed_manifest.deinit();
    const manifest = parsed_manifest.value;

    try expectSurveyedCommitProvenance(survey_note, manifest.surveyed_commit);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "include/uapi/linux/watchdog.h") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "struct watchdog_info") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "layout_assert") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "size 40") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "alignment 4") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "exact `u32`, `u32`, and `[32]u8` field types") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "offsets 0, 4, and 8") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "watchdog_device") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "watchdog_ops") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "include/uapi/asm-generic/termios.h") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "struct winsize") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "size 8") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "alignment 2") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "exact `u16` field types") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "offsets 0, 2, 4, and 6") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "struct hvc_struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 3 interop substrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared struct layouts") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "hvc_console.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "hvc_kick()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "notifier_*_irq()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "backed by code instead of prose alone") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "exported-helper signature checkpoint") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`hvc_instantiate()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`__hvc_resize()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "four driver-local ABI checkpoints") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "bounded exported hvc helper signature proofs") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase11_hvc_console_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared-versus-dedicated replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "callback-signature proofs") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "struct watchdog_info") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "__u32 options") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "__u32 firmware_version") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "__u8  identity[32]") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "WDIOC_GETSUPPORT") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_uapi_header, "WDIOS_DISABLECARD") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_core_header, "struct watchdog_ops") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_core_header, "struct watchdog_device") != null);
    try std.testing.expect(std.mem.indexOf(u8, termios_uapi_header, "struct winsize") != null);
    try std.testing.expect(std.mem.indexOf(u8, termios_uapi_header, "unsigned short ws_row") != null);
    try std.testing.expect(std.mem.indexOf(u8, termios_uapi_header, "unsigned short ws_col") != null);
    try std.testing.expect(std.mem.indexOf(u8, termios_uapi_header, "unsigned short ws_xpixel") != null);
    try std.testing.expect(std.mem.indexOf(u8, termios_uapi_header, "unsigned short ws_ypixel") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "MAX_NR_HVC_CONSOLES") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "HVC_ALLOC_TTY_ADAPTERS") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "struct hv_ops") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "struct winsize ws;") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "int hvc_poll(struct hvc_struct *hp);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "void hvc_kick(void);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "__hvc_resize(struct hvc_struct *hp, struct winsize ws)") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "extern int notifier_add_irq(struct hvc_struct *hp, int data);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "extern void notifier_del_irq(struct hvc_struct *hp, int data);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header, "extern void notifier_hangup_irq(struct hvc_struct *hp, int data);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_zig, "pub const max_nr_hvc_consoles: usize = 16;") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_zig, "pub const alloc_tty_adapters: usize = 8;") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_zig, "pub const HeaderParitySnapshot = struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_zig, "pub fn headerParitySnapshot() HeaderParitySnapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_zig, ".anchor = \"drivers/tty/hvc/hvc_console.h\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_zig, ".exports_resize = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_zig, ".exports_kick = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_zig, ".exports_notifier_add_irq = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_zig, ".exports_notifier_del_irq = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_zig, ".exports_notifier_hangup_irq = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_zig, ".has_notifier_hangup = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_validation_matrix, "dedicated survey replay still passes separately") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "test \"phase11 hvc console survey keeps a bounded winsize layout proof\" {") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertSize(WinsizeLayout, 8);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertAlign(WinsizeLayout, 2);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(WinsizeLayout, \"ws_row\", 0);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(WinsizeLayout, \"ws_col\", 2);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(WinsizeLayout, \"ws_xpixel\", 4);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(WinsizeLayout, \"ws_ypixel\", 6);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "test \"phase11 hvc console survey keeps a bounded hv_ops layout proof\" {") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertSize(HvOpsLayout, 72);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertAlign(HvOpsLayout, 8);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(HvOpsLayout, \"get_chars\", 0);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(HvOpsLayout, \"put_chars\", 8);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(HvOpsLayout, \"flush\", 16);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(HvOpsLayout, \"notifier_add\", 24);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(HvOpsLayout, \"notifier_del\", 32);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(HvOpsLayout, \"notifier_hangup\", 40);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(HvOpsLayout, \"tiocmget\", 48);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(HvOpsLayout, \"tiocmset\", 56);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "layout_assert.assertOffset(HvOpsLayout, \"dtr_rts\", 64);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "test \"phase11 hvc console survey keeps bounded hv_ops callback signature proofs\" {") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "assertExactType(@FieldType(HvOpsLayout, \"get_chars\"), ?*const fn (u32, [*]u8, usize) callconv(.c) isize);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "assertExactType(@FieldType(HvOpsLayout, \"put_chars\"), ?*const fn (u32, [*]const u8, usize) callconv(.c) isize);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "assertExactType(@FieldType(HvOpsLayout, \"flush\"), ?*const fn (u32, bool) callconv(.c) c_int);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "assertExactType(@FieldType(HvOpsLayout, \"notifier_add\"), ?*const fn (*HvcStruct, c_int) callconv(.c) c_int);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "assertExactType(@FieldType(HvOpsLayout, \"notifier_del\"), ?*const fn (*HvcStruct, c_int) callconv(.c) void);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "assertExactType(@FieldType(HvOpsLayout, \"notifier_hangup\"), ?*const fn (*HvcStruct, c_int) callconv(.c) void);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "assertExactType(@FieldType(HvOpsLayout, \"tiocmget\"), ?*const fn (*HvcStruct) callconv(.c) c_int);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "assertExactType(@FieldType(HvOpsLayout, \"tiocmset\"), ?*const fn (*HvcStruct, c_uint, c_uint) callconv(.c) c_int);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "assertExactType(@FieldType(HvOpsLayout, \"dtr_rts\"), ?*const fn (*HvcStruct, bool) callconv(.c) void);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "test \"phase11 hvc console survey keeps bounded exported helper signature proofs\" {") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "assertExactType(@FieldType(HvcExportSurface, \"hvc_instantiate\"), HvcInstantiateFn);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_survey, "assertExactType(@FieldType(HvcExportSurface, \"notifier_hangup_irq\"), HvcNotifierHangupIrqFn);") != null);
    try std.testing.expectEqual(@as(usize, 13), inventory.build_test_names.len);
    try std.testing.expectEqual(@as(usize, 12), inventory.shared_test_depend_steps.len);
    try std.testing.expectEqual(@as(usize, 20), inventory.module_root_source_files.len);
    try std.testing.expectEqual(@as(usize, 13), inventory.module_imports.len);
    try std.testing.expectEqual(@as(usize, 13), inventory.test_root_modules.len);
    try std.testing.expectEqual(@as(usize, 1), inventory.forbidden_markers.len);
    try std.testing.expectEqual(@as(usize, 1), inventory.dedicated_survey_replays.len);
    try std.testing.expectEqualStrings("phase11-dw-wdt-survey-tests", inventory.build_test_names[7]);
    try std.testing.expectEqualStrings("phase11-uapi-header-parity-survey-tests", inventory.build_test_names[8]);
    try std.testing.expectEqualStrings("phase11-hvc-console-tests", inventory.build_test_names[9]);
    try std.testing.expectEqualStrings("phase11-hvc-console-modem-control-split-tests", inventory.build_test_names[10]);
    try std.testing.expectEqualStrings("phase11-hvc-console-poll-retry-split-tests", inventory.build_test_names[11]);
    try std.testing.expectEqualStrings("phase11-hvc-console-survey-tests", inventory.build_test_names[12]);
    try std.testing.expectEqualStrings("run_phase11_dw_wdt_survey_tests", inventory.shared_test_depend_steps[7]);
    try std.testing.expectEqualStrings("run_phase11_uapi_header_parity_survey_tests", inventory.shared_test_depend_steps[8]);
    try std.testing.expectEqualStrings("run_phase11_hvc_console_tests", inventory.shared_test_depend_steps[9]);
    try std.testing.expectEqualStrings("run_phase11_hvc_console_modem_control_split_tests", inventory.shared_test_depend_steps[10]);
    try std.testing.expectEqualStrings("run_phase11_hvc_console_poll_retry_split_tests", inventory.shared_test_depend_steps[11]);
    try std.testing.expectEqualStrings("phase11_uapi_header_parity_survey_module", inventory.module_root_source_files[13].module);
    try std.testing.expectEqualStrings("phase11_uapi_header_parity_survey.zig", inventory.module_root_source_files[13].path);
    try std.testing.expectEqualStrings("hvc_console_module", inventory.module_root_source_files[14].module);
    try std.testing.expectEqualStrings("../../drivers/tty/hvc/hvc_console.zig", inventory.module_root_source_files[14].path);
    try std.testing.expectEqualStrings("phase11_hvc_console_modem_control_split_module", inventory.module_root_source_files[17].module);
    try std.testing.expectEqualStrings("phase11_hvc_console_modem_control_split.zig", inventory.module_root_source_files[17].path);
    try std.testing.expectEqualStrings("phase11_hvc_console_poll_retry_split_module", inventory.module_root_source_files[18].module);
    try std.testing.expectEqualStrings("phase11_hvc_console_poll_retry_split.zig", inventory.module_root_source_files[18].path);
    try std.testing.expectEqualStrings("phase11_uapi_header_parity_survey_module", inventory.module_imports[6].module);
    try std.testing.expectEqualStrings("layout_assert", inventory.module_imports[6].import_name);
    try std.testing.expectEqualStrings("layout_assert_module", inventory.module_imports[6].imported_module);
    try std.testing.expectEqualStrings("phase11_uapi_header_parity_survey_module", inventory.module_imports[7].module);
    try std.testing.expectEqualStrings("hvc_console", inventory.module_imports[7].import_name);
    try std.testing.expectEqualStrings("hvc_console_module", inventory.module_imports[7].imported_module);
    try std.testing.expectEqualStrings("phase11_hvc_console_modem_control_split_module", inventory.module_imports[9].module);
    try std.testing.expectEqualStrings("hvc_console", inventory.module_imports[9].import_name);
    try std.testing.expectEqualStrings("hvc_console_module", inventory.module_imports[9].imported_module);
    try std.testing.expectEqualStrings("phase11_hvc_console_poll_retry_split_module", inventory.module_imports[10].module);
    try std.testing.expectEqualStrings("hvc_console", inventory.module_imports[10].import_name);
    try std.testing.expectEqualStrings("hvc_console_module", inventory.module_imports[10].imported_module);
    try std.testing.expectEqualStrings("phase11_hvc_console_poll_retry_split_module", inventory.module_imports[11].module);
    try std.testing.expectEqualStrings("hvc_console_sysrq", inventory.module_imports[11].import_name);
    try std.testing.expectEqualStrings("hvc_console_sysrq_module", inventory.module_imports[11].imported_module);
    try std.testing.expectEqualStrings("phase11-uapi-header-parity-survey-tests", inventory.test_root_modules[8].@"test");
    try std.testing.expectEqualStrings("phase11_uapi_header_parity_survey_module", inventory.test_root_modules[8].root_module);
    try std.testing.expectEqualStrings("phase11-hvc-console-tests", inventory.test_root_modules[9].@"test");
    try std.testing.expectEqualStrings("phase11_hvc_console_module", inventory.test_root_modules[9].root_module);
    try std.testing.expectEqualStrings("phase11-hvc-console-modem-control-split-tests", inventory.test_root_modules[10].@"test");
    try std.testing.expectEqualStrings("phase11_hvc_console_modem_control_split_module", inventory.test_root_modules[10].root_module);
    try std.testing.expectEqualStrings("phase11-hvc-console-poll-retry-split-tests", inventory.test_root_modules[11].@"test");
    try std.testing.expectEqualStrings("phase11_hvc_console_poll_retry_split_module", inventory.test_root_modules[11].root_module);
    try std.testing.expectEqualStrings("phase11-hvc-console-survey-tests", inventory.test_root_modules[12].@"test");
    try std.testing.expectEqualStrings("phase11_hvc_console_survey_module", inventory.test_root_modules[12].root_module);
    try std.testing.expectEqualStrings("test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);", inventory.forbidden_markers[0]);
    try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_survey.zig", inventory.dedicated_survey_replays[0]);
    try std.testing.expectEqual(@as(usize, 3), inventory.shared_split_replays.len);
    try std.testing.expectEqualStrings("phase11-dw-wdt-remove-idle-split-tests", inventory.shared_split_replays[0].@"test");
    try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt_remove_idle_split.zig", inventory.shared_split_replays[0].path);
    try std.testing.expectEqualStrings("phase11-hvc-console-modem-control-split-tests", inventory.shared_split_replays[1].@"test");
    try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_modem_control_split.zig", inventory.shared_split_replays[1].path);
    try std.testing.expectEqualStrings("phase11-hvc-console-poll-retry-split-tests", inventory.shared_split_replays[2].@"test");
    try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_poll_retry_split.zig", inventory.shared_split_replays[2].path);
    try std.testing.expectEqual(@as(usize, 1), inventory.shared_adjunct_replays.len);
    try std.testing.expectEqualStrings("phase11-dw-wdt-suspend-resume-tests", inventory.shared_adjunct_replays[0].@"test");
    try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt_suspend_resume.zig", inventory.shared_adjunct_replays[0].path);
    try std.testing.expectEqual(@as(usize, 4), inventory.shared_replay_markers.len);
    try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt_suspend_resume.zig", inventory.shared_replay_markers[0].path);
    try std.testing.expectEqualStrings("    try std.testing.expect(summary.resume_preserves_timeout_programming);", inventory.shared_replay_markers[0].marker);
    try std.testing.expectEqualStrings("zigux/tests/phase11_dw_wdt_remove_idle_split.zig", inventory.shared_replay_markers[1].path);
    try std.testing.expectEqualStrings("    try std.testing.expect(reset_available_summary.remove_clears_interrupt_status);", inventory.shared_replay_markers[1].marker);
    try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_modem_control_split.zig", inventory.shared_replay_markers[2].path);
    try std.testing.expectEqualStrings("    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);", inventory.shared_replay_markers[2].marker);
    try std.testing.expectEqualStrings("zigux/tests/phase11_hvc_console_poll_retry_split.zig", inventory.shared_replay_markers[3].path);
    try std.testing.expectEqualStrings("    try std.testing.expect(dispatch.invokes_sysrq_handler);", inventory.shared_replay_markers[3].marker);
}

test "phase11 shared header parity survey keeps the hvc snapshot aligned with the bounded header mirror" {
    const snapshot = hvc_console.headerParitySnapshot();

    try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.h", snapshot.anchor);
    try std.testing.expectEqual(@as(usize, 16), snapshot.max_nr_hvc_consoles);
    try std.testing.expectEqual(@as(usize, 8), snapshot.alloc_tty_adapters);
    try std.testing.expect(snapshot.exports_instantiate);
    try std.testing.expect(snapshot.exports_alloc);
    try std.testing.expect(snapshot.exports_remove);
    try std.testing.expect(snapshot.exports_poll);
    try std.testing.expect(snapshot.exports_resize);
    try std.testing.expect(snapshot.exports_kick);
    try std.testing.expect(snapshot.exports_notifier_add_irq);
    try std.testing.expect(snapshot.exports_notifier_del_irq);
    try std.testing.expect(snapshot.exports_notifier_hangup_irq);
    try std.testing.expect(snapshot.hv_ops.has_get_chars);
    try std.testing.expect(snapshot.hv_ops.has_put_chars);
    try std.testing.expect(snapshot.hv_ops.has_flush);
    try std.testing.expect(snapshot.hv_ops.has_notifier_add);
    try std.testing.expect(snapshot.hv_ops.has_notifier_del);
    try std.testing.expect(snapshot.hv_ops.has_notifier_hangup);
    try std.testing.expect(snapshot.hv_ops.has_tiocmget);
    try std.testing.expect(snapshot.hv_ops.has_tiocmset);
    try std.testing.expect(snapshot.hv_ops.has_dtr_rts);
    try std.testing.expect(snapshot.keeps_tty_registration_out_of_scope);
    try std.testing.expect(snapshot.keeps_live_hypervisor_io_out_of_scope);
}

test "phase11 shared header parity survey keeps exact hvc snapshot counts" {
    const snapshot = hvc_console.headerParitySnapshot();

    try std.testing.expectEqual(@as(usize, 9), countHvcHeaderExports(snapshot));
    try std.testing.expectEqual(@as(usize, 9), countHvOpsHeaderSurface(snapshot.hv_ops));
}

test "phase11 shared header parity survey keeps a bounded watchdog_info layout proof" {
    comptime {
        layout_assert.assertSize(WatchdogInfoLayout, 40);
        layout_assert.assertAlign(WatchdogInfoLayout, 4);
        layout_assert.assertFieldType(WatchdogInfoLayout, "options", u32);
        layout_assert.assertFieldType(WatchdogInfoLayout, "firmware_version", u32);
        layout_assert.assertFieldType(WatchdogInfoLayout, "identity", [32]u8);
        layout_assert.assertOffset(WatchdogInfoLayout, "options", 0);
        layout_assert.assertOffset(WatchdogInfoLayout, "firmware_version", 4);
        layout_assert.assertOffset(WatchdogInfoLayout, "identity", 8);
    }
}

test "phase11 shared header parity survey keeps a bounded winsize layout proof" {
    comptime {
        layout_assert.assertSize(WinsizeLayout, 8);
        layout_assert.assertAlign(WinsizeLayout, 2);
        layout_assert.assertFieldType(WinsizeLayout, "ws_row", u16);
        layout_assert.assertFieldType(WinsizeLayout, "ws_col", u16);
        layout_assert.assertFieldType(WinsizeLayout, "ws_xpixel", u16);
        layout_assert.assertFieldType(WinsizeLayout, "ws_ypixel", u16);
        layout_assert.assertOffset(WinsizeLayout, "ws_row", 0);
        layout_assert.assertOffset(WinsizeLayout, "ws_col", 2);
        layout_assert.assertOffset(WinsizeLayout, "ws_xpixel", 4);
        layout_assert.assertOffset(WinsizeLayout, "ws_ypixel", 6);
    }
}

test "phase11 shared header parity survey keeps bounded exported helper signature proofs" {
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

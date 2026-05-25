const std = @import("std");
const hvc_console = @import("hvc_console");

fn readCandidateAlloc(
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(limit));
}

fn readRepoFileAlloc(
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return readCandidateAlloc(allocator, path, limit) catch |err| switch (err) {
        error.FileNotFound => {
            const prefixed = try std.fmt.allocPrint(allocator, "../../{s}", .{path});
            defer allocator.free(prefixed);
            return readCandidateAlloc(allocator, prefixed, limit);
        },
        else => return err,
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase11 hvc cleanup packet proof keeps missing teardown anchors explicit" {
    const survey_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_doc);

    const companion_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(companion_doc);

    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    try expectContains(survey_doc, "`Documentation/zigux/phase11-hvc-console-teardown-note.md`");
    try expectContains(companion_doc, "`zigux/tests/phase11_hvc_console_manifest.json`");
    try expectContains(companion_doc, "proof-backed HVC continuity packet remains reviewable");
    try expectContains(matrix_doc, "repo-reality gaps instead of returned fallback evidence");
}

test "phase11 hvc cleanup packet proof keeps route boundaries explicit" {
    const survey_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_doc);

    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    try expectContains(survey_doc, "`make -C zigux phase11-validate`");
    try expectContains(survey_doc, "`make -C zigux phase11-hvc-survey`");
    try expectContains(matrix_doc, "`make -C zigux phase11-validate`");
    try expectContains(matrix_doc, "`make -C zigux phase11-hvc-survey`");
}

test "phase11 hvc cleanup packet proof keeps verify-boundary failure modes explicit" {
    const verify_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(verify_doc);

    try expectContains(verify_doc, "`error.CleanupRequiresFinalCloseOrHangup`");
    try expectContains(verify_doc, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`");
    try expectContains(verify_doc, "`targetless_dispatch_without_notifier`");
}

test "phase11 hvc cleanup packet proof keeps starter teardown helpers tied to matrix evidence" {
    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    const driver = try readRepoFileAlloc(
        std.testing.allocator,
        "drivers/tty/hvc/hvc_console.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(driver);

    try expectContains(matrix_doc, "flush intent");
    try expectContains(matrix_doc, "`hvc_install()` ownership");
    try expectContains(matrix_doc, "`hvc_cleanup()` tty-port");
    try expectContains(driver, "pub fn summarizeCleanupHandoff(request: CleanupHandoffRequest) CleanupHandoffSummary {");
    try expectContains(driver, "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {");
}

test "phase11 hvc cleanup packet proof keeps close teardown carryover details tied to matrix evidence" {
    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    const driver = try readRepoFileAlloc(
        std.testing.allocator,
        "drivers/tty/hvc/hvc_console.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(driver);

    try expectContains(matrix_doc, "DTR/RTS shutdown");
    try expectContains(matrix_doc, "`wait_until_sent()` carryover");
    try expectContains(matrix_doc, "`close_wait` ownership");
    try expectContains(matrix_doc, "`port_initialized` clearing");
    try expectContains(driver, "pub const CloseTeardownSummary = struct {");
    try expectContains(driver, "dtr_rts_shutdown: bool,");
    try expectContains(driver, "wait_until_sent_intent: bool,");
    try expectContains(driver, "close_wait_ownership: bool,");
    try expectContains(driver, "port_initialized_cleared: bool,");
    try expectContains(driver, "pub fn summarizeCloseTeardown(request: CloseTeardownRequest) CloseTeardownSummary {");
}

test "phase11 hvc cleanup packet proof executes install and console setup summaries" {
    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    try expectContains(matrix_doc, "`hvc_install()` ownership");
    try expectContains(matrix_doc, "`hvc_alloc()` slot");
    try expectContains(matrix_doc, "early console setup and device selection");

    const install = hvc_console.summarizeInstallOwnership(.{
        .index_lookup_found = true,
        .kref_acquired_from_lookup = true,
        .driver_data_bound = true,
        .tty_port_install_succeeded = true,
        .failure_put_releases_port_ref = true,
    });
    const slot = hvc_console.summarizeAllocSlotHandoff(.{
        .matched_registered_console = false,
        .empty_console_slot_available = true,
        .hvc_struct_list_linked = true,
        .rechecks_kernel_console = true,
    });
    const setup = hvc_console.summarizeConsoleSetup(.{
        .console_index = @as(c_int, @intCast(hvc_console.MAX_NR_HVC_CONSOLES)),
        .adapter_present = true,
    });
    const device = hvc_console.summarizeConsoleDeviceSelection(.{
        .console_index = 3,
        .adapter_present = true,
        .tty_driver_registered = false,
    });

    try std.testing.expect(install.install_reference_retained);
    try std.testing.expect(!install.tty_port_put_on_failure);
    try std.testing.expectEqual(hvc_console.AllocSlotSelection.empty_console_slot, slot.selection);
    try std.testing.expect(slot.claims_console_slot);
    try std.testing.expect(setup.returns_enodev);
    try std.testing.expect(!setup.setup_allowed);
    try std.testing.expectEqual(@as(?c_int, 3), device.selected_console_index);
    try std.testing.expect(device.returns_null_driver);
}

test "phase11 hvc cleanup packet proof executes resize handoff summaries" {
    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    try expectContains(matrix_doc, "`__hvc_resize()`");

    const visible = hvc_console.summarizeResizeHandoff(.{
        .tty_present = true,
        .winsize = .{
            .ws_row = 24,
            .ws_col = 80,
            .ws_xpixel = 640,
            .ws_ypixel = 480,
        },
    });
    const zeroed = hvc_console.summarizeResizeHandoff(.{
        .tty_present = false,
        .winsize = .{
            .ws_row = 0,
            .ws_col = 0,
            .ws_xpixel = 0,
            .ws_ypixel = 0,
        },
    });

    try std.testing.expect(visible.tty_present);
    try std.testing.expect(visible.geometry_visible);
    try std.testing.expect(visible.keeps_live_resize_execution_out_of_scope);
    try std.testing.expect(!zeroed.tty_present);
    try std.testing.expect(!zeroed.geometry_visible);
    try std.testing.expect(zeroed.keeps_live_resize_execution_out_of_scope);
}

test "phase11 hvc cleanup packet proof keeps newer failure-mode helpers tied to matrix evidence" {
    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    const driver = try readRepoFileAlloc(
        std.testing.allocator,
        "drivers/tty/hvc/hvc_console.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(driver);

    try expectContains(matrix_doc, "`hvc_kick()` wakeup-cue");
    try expectContains(matrix_doc, "notifier-irq");
    try expectContains(matrix_doc, "modem-control helper summaries reviewable on current `master`");
    try expectContains(driver, "pub fn summarizeCleanupPrerequisite(");
    try expectContains(driver, ") error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary {");
    try expectContains(driver, "pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {");
    try expectContains(driver, "pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {");
    try expectContains(driver, "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {");
    try expectContains(driver, "const targetless_hangup_short_circuit = request.notifier_registered and");
    try expectContains(driver, ".targetless_hangup_short_circuit = targetless_hangup_short_circuit,");
    try expectContains(driver, "try std.testing.expect(!active.targetless_hangup_short_circuit);");
    try expectContains(driver, "try std.testing.expect(targetless.targetless_hangup_short_circuit);");
    try expectContains(driver, "try std.testing.expect(!invalid.targetless_hangup_short_circuit);");
}

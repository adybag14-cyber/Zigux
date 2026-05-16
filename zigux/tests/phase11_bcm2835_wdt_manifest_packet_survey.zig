const std = @import("std");

fn readFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

fn expectContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn expectNotContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) == null);
}

test "phase11 bcm2835 manifest packet survey keeps direct handoff and lifecycle helpers explicit" {
    const driver = try readFile(std.testing.allocator, "drivers/watchdog/bcm2835_wdt.zig", 24 * 1024);
    defer std.testing.allocator.free(driver);

    try expectContains(driver, "pub const anchor_path = \"drivers/watchdog/bcm2835_wdt.c\";");
    try expectContains(driver, "pub const restart_priority: i32 = 128;");
    try expectContains(driver, "pub fn maxTimeoutSeconds() u32");
    try expectContains(driver, "pub fn secondsToWatchdogTicks(seconds: u32) !u32");
    try expectContains(driver, "pub fn summarizeProbe(request: ProbeRequest) !ProbeSummary");
    try expectContains(driver, "pub fn summarizePlatformHandoff(request: PlatformHandoffRequest) !PlatformHandoffSummary");
    try expectContains(driver, "pub const Bcm2835WdtLab = struct {");
    try expectContains(driver, "pub fn importBootloaderRunning(self: *Bcm2835WdtLab) !void");
    try expectContains(driver, "pub fn poweroff(self: *Bcm2835WdtLab, handler_claimed: bool) PoweroffSummary");
    try expectContains(driver, ".blocked_on_live_platform_registration = true,");
    try expectContains(driver, ".poweroff_handler_claimed = probe.poweroff_handler_claimed,");
    try expectContains(driver, ".poweroff_handler_conflict = probe.poweroff_handler_conflict,");
}

test "phase11 bcm2835 manifest packet survey keeps manifest, slice, teardown, and matrix notes aligned with the direct packet" {
    const survey_note = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_note);
    const slice_note = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-slice.md", 16 * 1024);
    defer std.testing.allocator.free(slice_note);
    const teardown_note = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md", 16 * 1024);
    defer std.testing.allocator.free(teardown_note);
    const validation_matrix = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md", 16 * 1024);
    defer std.testing.allocator.free(validation_matrix);
    const manifest = try readFile(std.testing.allocator, "zigux/tests/phase11_bcm2835_wdt_manifest.json", 24 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(survey_note, "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed");
    try expectContains(survey_note, "zigux/tests/phase11_bcm2835_wdt_survey.zig");
    try expectContains(survey_note, "drivers/watchdog/bcm2835_wdt_verify.zig");
    try expectContains(survey_note, "zigux/tests/phase11_bcm2835_wdt_manifest.json");
    try expectContains(survey_note, "one bcm2835-only manifest or slice-note extension");
    try expectNotContains(survey_note, "P11-L12");

    try expectContains(slice_note, "Phase 11 BCM2835 Watchdog Slice");
    try expectContains(slice_note, "drivers/watchdog/bcm2835_wdt.c");
    try expectContains(slice_note, "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md");
    try expectContains(slice_note, "The next honest bounded step inside the same Phase 11 family is no longer another note-only handoff.");
    try expectNotContains(slice_note, "P11-L12");

    try expectContains(teardown_note, "PHASE11_BCM2835_WDT_TEARDOWN_STATUS=driver_teardown_truthful");
    try expectContains(teardown_note, "drivers/watchdog/bcm2835_wdt_verify.zig");
    try expectContains(teardown_note, "zigux/tests/phase11_bcm2835_wdt_survey.zig");
    try expectContains(teardown_note, "compile-local verify helper");
    try expectContains(teardown_note, "dedicated survey gate");
    try expectContains(teardown_note, "one manifest-backed extension");

    try expectContains(validation_matrix, "PHASE11_BCM2835_WDT_STATUS=survey_gate_truthful");
    try expectContains(validation_matrix, "zigux/tests/phase11_bcm2835_wdt_survey.zig");
    try expectContains(validation_matrix, "drivers/watchdog/bcm2835_wdt_verify.zig");
    try expectContains(validation_matrix, "survey-gate coverage");
    try expectContains(validation_matrix, "zigux/tests/phase11_bcm2835_wdt_manifest.json");
    try expectNotContains(validation_matrix, "P11-L12");

    try expectContains(manifest, "\"lane_key\": \"P11-L08\"");
    try expectContains(manifest, "\"zigux_destination\": \"Documentation/zigux/phase11-bcm2835-wdt-slice.md\"");
    try expectContains(manifest, "\"id\": \"phase11-bcm2835-wdt-survey-gate\"");
}

test "phase11 bcm2835 manifest packet survey keeps the replay and verify helpers reviewable" {
    const replay = try readFile(std.testing.allocator, "zigux/tests/phase11_bcm2835_wdt.zig", 16 * 1024);
    defer std.testing.allocator.free(replay);
    const verify = try readFile(std.testing.allocator, "drivers/watchdog/bcm2835_wdt_verify.zig", 16 * 1024);
    defer std.testing.allocator.free(verify);

    try expectContains(replay, "phase11 bcm2835 watchdog replay keeps timeout helpers explicit");
    try expectContains(replay, "phase11 bcm2835 watchdog replay keeps probe ownership and poweroff conflict distinct");
    try expectContains(replay, "phase11 bcm2835 watchdog replay keeps platform handoff readiness and poweroff claim blocking explicit");
    try expectContains(replay, "phase11 bcm2835 watchdog replay keeps start stop restart and poweroff lifecycle explicit");
    try expectContains(verify, "phase11 bcm2835 watchdog verify keeps PM-base readiness and ownership explicit");
    try expectContains(verify, "phase11 bcm2835 watchdog verify keeps poweroff ownership distinct");
}

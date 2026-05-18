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

test "phase11 bcm2835 survey keeps direct handoff and lifecycle helpers explicit" {
    const driver = try readFile(std.testing.allocator, "drivers/watchdog/bcm2835_wdt.zig", 24 * 1024);
    defer std.testing.allocator.free(driver);

    try std.testing.expect(std.mem.indexOf(u8, driver, "pub const anchor_path = \"drivers/watchdog/bcm2835_wdt.c\";") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver, "pub const restart_priority: i32 = 128;") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver, "pub fn maxTimeoutSeconds() u32") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver, "pub fn secondsToWatchdogTicks(seconds: u32) !u32") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver, "pub fn summarizeProbe(request: ProbeRequest) !ProbeSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver, "pub fn summarizePlatformHandoff(request: PlatformHandoffRequest) !PlatformHandoffSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver, "pub const Bcm2835WdtLab = struct {") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver, "pub fn importBootloaderRunning(self: *Bcm2835WdtLab) !void") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver, "pub fn poweroff(self: *Bcm2835WdtLab, handler_claimed: bool) PoweroffSummary") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver, ".blocked_on_live_platform_registration = true,") != null);
    try std.testing.expect(std.mem.indexOf(u8, driver, ".poweroff_handler_claimed = probe.poweroff_handler_claimed and pm_base_handoff_ready,") != null);
}

test "phase11 bcm2835 survey keeps survey, teardown, manifest, and matrix notes aligned" {
    const survey_note = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_note);
    const teardown_note = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md", 16 * 1024);
    defer std.testing.allocator.free(teardown_note);
    const validation_matrix = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md", 16 * 1024);
    defer std.testing.allocator.free(validation_matrix);
    const manifest = try readFile(std.testing.allocator, "zigux/tests/phase11_bcm2835_wdt_manifest.json", 16 * 1024);
    defer std.testing.allocator.free(manifest);

    try std.testing.expect(std.mem.indexOf(u8, manifest, "\"lane_key\": \"P11-L08\"") != null);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase11_bcm2835_wdt_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "drivers/watchdog/bcm2835_wdt_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase11_bcm2835_wdt_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "manifest-backed archival reminder packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "explicit validation plan") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "P11-L10") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "one bcm2835-only manifest or slice-note extension") == null);

    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "PHASE11_BCM2835_WDT_TEARDOWN_STATUS=driver_teardown_truthful") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "drivers/watchdog/bcm2835_wdt_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "zigux/tests/phase11_bcm2835_wdt_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "archival manifest-backed reminder packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "explicit validation plan") != null);
    try std.testing.expect(std.mem.indexOf(u8, teardown_note, "one manifest-backed extension") == null);

    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "PHASE11_BCM2835_WDT_STATUS=survey_gate_truthful") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "zigux/tests/phase11_bcm2835_wdt_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "drivers/watchdog/bcm2835_wdt_verify.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "zigux/tests/phase11_bcm2835_wdt_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "explicit validation plan") != null);
    try std.testing.expect(std.mem.indexOf(u8, validation_matrix, "P11-L10") == null);
}

test "phase11 bcm2835 survey keeps the replay and verify helpers reviewable" {
    const replay = try readFile(std.testing.allocator, "zigux/tests/phase11_bcm2835_wdt.zig", 16 * 1024);
    defer std.testing.allocator.free(replay);
    const verify = try readFile(std.testing.allocator, "drivers/watchdog/bcm2835_wdt_verify.zig", 16 * 1024);
    defer std.testing.allocator.free(verify);

    try std.testing.expect(std.mem.indexOf(u8, replay, "phase11 bcm2835 watchdog replay keeps timeout helpers explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, replay, "phase11 bcm2835 watchdog replay keeps probe ownership and poweroff conflict distinct") != null);
    try std.testing.expect(std.mem.indexOf(u8, replay, "phase11 bcm2835 watchdog replay keeps platform handoff readiness and poweroff claim blocking explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, replay, "phase11 bcm2835 watchdog replay keeps start stop restart and poweroff lifecycle explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify, "phase11 bcm2835 watchdog verify keeps PM-base readiness and ownership explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify, "phase11 bcm2835 watchdog verify keeps poweroff ownership distinct") != null);
}

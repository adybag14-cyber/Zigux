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

test "phase11 bcm2835 manifest packet survey keeps the surviving reminder packet truthful" {
    const survey_note = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed");
    try expectContains(survey_note, "Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md");
    try expectContains(survey_note, "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig");
    try expectContains(survey_note, "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig");
    try expectContains(survey_note, "does not return `drivers/watchdog/bcm2835_wdt.zig`");
    try expectContains(survey_note, "`drivers/watchdog/bcm2835_wdt_verify.zig`");
    try expectContains(survey_note, "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`");
    try expectContains(survey_note, "reminder surface plus an explicit blocker plan");
    try expectNotContains(survey_note, "one bcm2835-only manifest or slice-note extension");
    try expectNotContains(survey_note, "P11-L12");
}

test "phase11 bcm2835 manifest packet survey keeps the blocker plan aligned with current master" {
    const validation_plan = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md", 16 * 1024);
    defer std.testing.allocator.free(validation_plan);

    try expectContains(validation_plan, "PHASE11_BCM2835_WDT_PLATFORM_VALIDATION_PLAN=starter_boundary_recorded");
    try expectContains(validation_plan, "current directly readable packet remains `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`, and `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`");
    try expectContains(validation_plan, "Do not fabricate current-head proof for a driver, verify helper, direct replay, slice note, teardown note, validation matrix");
    try expectContains(validation_plan, "The next honest bcm2835-only follow-through is one explicit driver-return or platform-registration planning step");
    try expectNotContains(validation_plan, "drivers/watchdog/bcm2835_wdt_verify.zig");
    try expectNotContains(validation_plan, "zigux/tests/phase11_bcm2835_wdt.zig");
}

test "phase11 bcm2835 manifest packet survey keeps the dedicated build route pointed at the current reminder packet" {
    const build_file = try readFile(std.testing.allocator, "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig", 8 * 1024);
    defer std.testing.allocator.free(build_file);

    try expectContains(build_file, ".root_source_file = b.path(\"phase11_bcm2835_wdt_manifest_packet_survey.zig\")");
    try expectContains(build_file, ".name = \"phase11-bcm2835-wdt-manifest-packet-survey-tests\"");
    try expectContains(build_file, "Run the focused Phase 11 bcm2835 watchdog manifest packet survey");
}
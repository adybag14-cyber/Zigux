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

test "phase11 bcm2835 manifest packet survey keeps the returned driver proof truthful" {
    const survey_note = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed");
    try expectContains(survey_note, "archival packet identity remains `P11-L08`");
    try expectContains(survey_note, "Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md");
    try expectContains(survey_note, "Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md");
    try expectContains(survey_note, "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md");
    try expectContains(survey_note, "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig");
    try expectContains(survey_note, "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig");
    try expectContains(survey_note, "`zigux/tests/phase11_bcm2835_wdt_manifest.json`");
    try expectContains(survey_note, "`drivers/watchdog/bcm2835_wdt.zig`");
    try expectContains(survey_note, "`drivers/watchdog/bcm2835_wdt_verify.zig`");
    try expectContains(survey_note, "`zigux/tests/phase11_bcm2835_wdt.zig`");
    try expectContains(survey_note, "driver proof, coupled verify helper, manifest-backed closure, teardown note, validation plan, validation matrix, focused replay, and dedicated reminder-packet survey route are directly readable together");
    try expectContains(survey_note, "direct current `master` readback still does not return `Documentation/zigux/phase11-bcm2835-wdt-slice.md`");
    try expectContains(survey_note, "wider platform behavior and the slice surface remain intentionally blocked");
    try expectContains(survey_note, "platform-registration or callback-ownership proof step");
    try expectNotContains(survey_note, "direct current `master` readback still does not return `Documentation/zigux/phase11-bcm2835-wdt-slice.md` or `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`");
}

test "phase11 bcm2835 manifest packet survey keeps the blocker plan aligned with current master" {
    const validation_plan = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md", 16 * 1024);
    defer std.testing.allocator.free(validation_plan);

    try expectContains(validation_plan, "PHASE11_BCM2835_WDT_PLATFORM_VALIDATION_PLAN=starter_boundary_recorded");
    try expectContains(validation_plan, "`Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`");
    try expectContains(validation_plan, "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`");
    try expectContains(validation_plan, "`drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `zigux/tests/phase11_bcm2835_wdt.zig`");
    try expectContains(validation_plan, "manifest-backed closure, one teardown note, and one validation matrix");
    try expectContains(validation_plan, "Do not fabricate current-head proof for a slice note, live platform registration");
    try expectContains(validation_plan, "Do not use it to reopen `gpio_wdt`, `dw_wdt`, HVC, or shared Phase 11 wording.");
    try expectContains(validation_plan, "Treat this as a validation-governance document, not proof that wider platform behavior is already implemented.");
    try expectContains(validation_plan, "If a later lane cannot produce the required proof for one stage, keep that stage blocked and leave the current reminder-plus-driver-plus-verify-plus-manifest-plus-teardown-plus-matrix packet as the published boundary.");
    try expectContains(validation_plan, "The next honest bcm2835-only follow-through is one platform-registration or shared-callback ownership step");
    try expectNotContains(validation_plan, "Do not fabricate current-head proof for a slice note, teardown note");
}

test "phase11 bcm2835 manifest packet survey keeps the validation matrix aligned with the current driver packet" {
    const matrix = try readFile(std.testing.allocator, "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md", 16 * 1024);
    defer std.testing.allocator.free(matrix);

    try expectContains(matrix, "PHASE11_BCM2835_WDT_STATUS=driver_proof_and_matrix_packet_truthful");
    try expectContains(matrix, "`drivers/watchdog/bcm2835_wdt.zig`");
    try expectContains(matrix, "`drivers/watchdog/bcm2835_wdt_verify.zig`");
    try expectContains(matrix, "`zigux/tests/phase11_bcm2835_wdt.zig`");
    try expectContains(matrix, "`Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`");
    try expectContains(matrix, "`Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`");
    try expectContains(matrix, "`pm_base_present` is false");
    try expectContains(matrix, "`full_reset_armed_after_stop`");
    try expectContains(matrix, "teardown-note anchor");
    try expectContains(matrix, "absent wider replay or slice files");
    try expectContains(matrix, "platform-registration or shared");
}

test "phase11 bcm2835 manifest packet survey keeps the dedicated build route pointed at the current reminder packet" {
    const build_file = try readFile(std.testing.allocator, "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig", 8 * 1024);
    defer std.testing.allocator.free(build_file);

    try expectContains(build_file, ".root_source_file = b.path(\"phase11_bcm2835_wdt_manifest_packet_survey.zig\")");
    try expectContains(build_file, ".name = \"phase11-bcm2835-wdt-manifest-packet-survey-tests\"");
    try expectContains(build_file, "Run the focused Phase 11 bcm2835 watchdog manifest packet survey");
}

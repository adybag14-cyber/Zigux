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

test "phase11 gpio current-head manifest survey keeps the note packet aligned" {
    const survey_note = try readFile(std.testing.allocator, "Documentation/zigux/phase11-gpio-wdt-survey.md", 24 * 1024);
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "PHASE11_GPIO_WDT_SURVEY_STATUS=current_head_driver_docs_and_proof_packet_truthful");
    try expectContains(survey_note, "zigux/tests/phase11_gpio_wdt_current_head_manifest.json");
    try expectContains(survey_note, "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig");
    try expectContains(survey_note, "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig");
    try expectContains(survey_note, "older wider replay and manifest route surfaces such as");
    try expectContains(survey_note, "`zigux/tests/phase11_gpio_wdt_manifest.json`");
    try expectContains(survey_note, "machine-readable");
    try expectContains(survey_note, "current-head manifest");
    try expectNotContains(survey_note, "current authenticated contents readback still does not rematerialize the older wider replay and manifest route surfaces such as");
}

test "phase11 gpio current-head manifest survey keeps the module slice aligned" {
    const module_slice = try readFile(std.testing.allocator, "Documentation/zigux/phase11-gpio-wdt-module-slice.md", 24 * 1024);
    defer std.testing.allocator.free(module_slice);

    try expectContains(module_slice, "drivers/watchdog/gpio_wdt_verify.zig");
    try expectContains(module_slice, "registrationIntentCheckpointSummary()");
    try expectContains(module_slice, "zigux/tests/phase11_gpio_wdt_registration_intent_review.zig");
    try expectContains(module_slice, "platformCleanupCheckpointSummary()");
    try expectContains(module_slice, "zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig");
    try expectContains(module_slice, "zigux/tests/phase11_gpio_wdt_current_head_manifest.json");
    try expectContains(module_slice, "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig");
    try expectContains(module_slice, "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig");
}

test "phase11 gpio current-head manifest survey keeps the validation matrix aligned" {
    const matrix = try readFile(std.testing.allocator, "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md", 24 * 1024);
    defer std.testing.allocator.free(matrix);

    try expectContains(matrix, "PHASE11_GPIO_WDT_STATUS=driver_docs_proof_and_current_head_manifest_truthful");
    try expectContains(matrix, "zigux/tests/phase11_gpio_wdt_current_head_manifest.json");
    try expectContains(matrix, "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig");
    try expectContains(matrix, "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig");
    try expectContains(matrix, "The older wider replay and route surfaces");
    try expectContains(matrix, "`zigux/tests/phase11_gpio_wdt_manifest.json`");
    try expectContains(matrix, "machine-readable current-head manifest");
}

test "phase11 gpio current-head manifest survey keeps the recovered manifest explicit" {
    const manifest = try readFile(std.testing.allocator, "zigux/tests/phase11_gpio_wdt_current_head_manifest.json", 24 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"lane_key\": \"P11-L04\"");
    try expectContains(manifest, "\"phase\": \"Phase 11\"");
    try expectContains(manifest, "\"anchor\": \"drivers/watchdog/gpio_wdt.c\"");
    try expectContains(manifest, "\"phase11-gpio-wdt-current-head-manifest\"");
    try expectContains(manifest, "\"phase11-gpio-wdt-current-head-manifest-survey\"");
    try expectContains(manifest, "\"phase11-gpio-wdt-older-manifest-return\"");
}

test "phase11 gpio current-head manifest survey build route stays dedicated" {
    const build_file = try readFile(std.testing.allocator, "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig", 8 * 1024);
    defer std.testing.allocator.free(build_file);

    try expectContains(build_file, ".root_source_file = b.path(\"phase11_gpio_wdt_current_head_manifest_survey.zig\")");
    try expectContains(build_file, ".name = \"phase11-gpio-wdt-current-head-manifest-survey-tests\"");
    try expectContains(build_file, "Run the focused Phase 11 gpio watchdog current-head manifest survey");
}

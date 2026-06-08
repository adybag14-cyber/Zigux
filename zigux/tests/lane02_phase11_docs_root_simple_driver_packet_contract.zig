const std = @import("std");

const allocator = std.testing.allocator;

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "docs root keeps Phase 11 simple-driver packet bounded and discoverable" {
    const docs_root = try readFile("Documentation/zigux/README.md");
    defer allocator.free(docs_root);

    try expectContains(docs_root, "Phase 11");
    try expectContains(docs_root, "simple-production-driver");
    try expectContains(docs_root, "drivers/watchdog/gpio_wdt_verify.zig");
    try expectContains(docs_root, "drivers/tty/hvc/hvc_console_verify.zig");
    try expectContains(docs_root, "zigux/tests/phase11_build.zig");
    try expectContains(docs_root, "make -C zigux phase11-validate");
    try expectContains(docs_root, "live tty-driver registration");
    try expectContains(docs_root, "host-backed teardown parity");
}

test "review checklist keeps Phase 11 reviewer prompts below live driver execution" {
    const checklist = try readFile("Documentation/zigux/review-checklist.md");
    defer allocator.free(checklist);

    try expectContains(checklist, "Phase 11");
    try expectContains(checklist, "gpio_wdt");
    try expectContains(checklist, "hvc_console");
    try expectContains(checklist, "drivers/watchdog/gpio_wdt_verify.zig");
    try expectContains(checklist, "drivers/tty/hvc/hvc_console_verify.zig");
    try expectContains(checklist, "phase11-validate");
    try expectContains(checklist, "bounded simple-driver");
    try expectContains(checklist, "live notifier");
    try expectContains(checklist, "khvcd");
}

test "HVC survey and shared Phase 11 route keep focused direct builds explicit" {
    const hvc_survey = try readFile("Documentation/zigux/phase11-hvc-console-survey.md");
    defer allocator.free(hvc_survey);
    const build_file = try readFile("zigux/tests/phase11_build.zig");
    defer allocator.free(build_file);

    try expectContains(hvc_survey, "PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful");
    try expectContains(hvc_survey, "drivers/tty/hvc/hvc_console_verify.zig");
    try expectContains(hvc_survey, "zigux/tests/phase11_hvc_hv_ops_layout_build.zig");
    try expectContains(hvc_survey, "zigux/tests/phase11_hvc_export_surface_layout_build.zig");
    try expectContains(hvc_survey, "zigux/tests/phase11_hvc_cleanup_packet_build.zig");
    try expectContains(hvc_survey, "zigux/tests/phase11_hvc_modem_control_proof_build.zig");
    try expectContains(hvc_survey, "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig");
    try expectContains(hvc_survey, "no dedicated `make -C zigux phase11-hvc-survey` wrapper");

    try expectContains(build_file, "phase11-gpio-wdt-verify");
    try expectContains(build_file, "phase11-hvc-console-verify");
    try expectContains(build_file, "phase11-simple-drivers");
    try expectBefore(build_file, "phase11-gpio-wdt-verify", "phase11-simple-drivers");
    try expectBefore(build_file, "phase11-hvc-console-verify", "phase11-simple-drivers");
}

test "watchdog and HVC verify helpers keep blocker boundaries reviewable" {
    const gpio_verify = try readFile("drivers/watchdog/gpio_wdt_verify.zig");
    defer allocator.free(gpio_verify);
    const hvc_verify = try readFile("drivers/tty/hvc/hvc_console_verify.zig");
    defer allocator.free(hvc_verify);

    try expectContains(gpio_verify, "drivers/watchdog/gpio_wdt.c");
    try expectContains(gpio_verify, "blocked_on_live_gpio_lookup");
    try expectContains(gpio_verify, "blocked_on_platform_registration");
    try expectContains(gpio_verify, "blocked_on_reboot_glue");
    try expectContains(gpio_verify, "keeps_runtime_reviewable");

    try expectContains(hvc_verify, "summarizeRemoveHandoffWithoutBinding");
    try expectContains(hvc_verify, "summarizeNotifierUnregisterTiming");
    try expectContains(hvc_verify, "keeps_live_notifier_execution_out_of_scope");
    try expectContains(hvc_verify, "SysrqLiteralFallbackRequest");
}

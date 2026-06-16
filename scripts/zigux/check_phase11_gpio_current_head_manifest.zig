const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_GPIO_CURRENT_HEAD_MANIFEST_SELF_TEST=pass";

const EXPECTED_CURRENT_HEAD_SURFACES = [_][]const u8{
    "drivers/watchdog/gpio_wdt.zig",
    "drivers/watchdog/gpio_wdt_verify.zig",
    "zigux/tests/phase11_gpio_wdt_verify_helper_build.zig",
    "zigux/tests/phase11_gpio_wdt_preflight_review.zig",
    "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_registration_intent_review.zig",
    "zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_current_head_manifest.json",
    "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig",
    "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig",
    "Documentation/zigux/phase11-gpio-wdt-survey.md",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-gpio-wdt-module-slice.md",
    "Documentation/zigux/phase11-gpio-wdt-teardown-note.md",
    "Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md",
};

const EXPECTED_GAP_SUMMARY = [_][]const u8{
    "(phase11-gpio-wdt-driver-starter",
    "starter_landed)",
    "(phase11-gpio-wdt-verify-helper",
    "starter_landed)",
    "(phase11-gpio-wdt-preflight-proof",
    "starter_landed)",
    "(phase11-gpio-wdt-registration-intent-proof",
    "starter_landed)",
    "(phase11-gpio-wdt-register-device-glue-proof",
    "starter_landed)",
    "(phase11-gpio-wdt-nowayout-proof",
    "starter_landed)",
    "(phase11-gpio-wdt-remove-handoff-proof",
    "starter_landed)",
    "(phase11-gpio-wdt-current-head-manifest",
    "starter_landed)",
    "(phase11-gpio-wdt-current-head-manifest-survey",
    "starter_landed)",
    "(phase11-gpio-wdt-shared-build-route",
    "shared_gap_current_head)",
    "(phase11-gpio-wdt-older-manifest-return",
    "shared_gap_current_head)",
    "(phase11-gpio-wdt-live-platform-validation",
    "ready_next)",
};

const SURVEY_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_gpio_wdt_registration_intent_review.zig`",
    "`zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest.json`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig`",
    "`zig run scripts/zigux/check_phase11_gpio_current_head_manifest.zig -- --self-test`",
    "`zig run scripts/zigux/check_phase11_gpio_current_head_manifest.zig --`",
    "registration-intent route",
    "dedicated build route",
};

const MATRIX_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_gpio_wdt_registration_intent_review.zig`",
    "`zigux/tests/phase11_gpio_wdt_registration_intent_review_build.zig`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest.json`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig`",
    "`zig run scripts/zigux/check_phase11_gpio_current_head_manifest.zig -- --self-test`",
    "`zig run scripts/zigux/check_phase11_gpio_current_head_manifest.zig --`",
    "focused registration-intent proof",
    "packet aligned through",
};

const MODULE_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest.json`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey.zig`",
    "`zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig`",
    "does not promote absent wider replay, manifest, survey-gate",
};

const TEARDOWN_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_gpio_wdt_verify_helper_build.zig`",
    "`zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig`",
    "`zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`",
    "without promoting absent wider replay, survey, manifest, or shared-build files",
};

const REMOVE_HANDOFF_MARKERS = [_][]const u8{
    "`zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig`",
    "`zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`",
    "`zigux/tests/phase11_build.zig`",
    "instead of treating absent wider replay, manifest, or shared-build files",
};

const BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"phase11_gpio_wdt_current_head_manifest_survey.zig\")",
    ".name = \"phase11-gpio-wdt-current-head-manifest-survey-tests\"",
    "Run the focused Phase 11 gpio watchdog current-head manifest survey",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase11_gpio_wdt_current_head_manifest.json",
};

const SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase11-gpio-wdt-survey.md",
};

const MATRIX_PATH = [_][]const u8{
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
};

const MODULE_PATH = [_][]const u8{
    "Documentation/zigux/phase11-gpio-wdt-module-slice.md",
};

const TEARDOWN_PATH = [_][]const u8{
    "Documentation/zigux/phase11-gpio-wdt-teardown-note.md",
};

const REMOVE_HANDOFF_PATH = [_][]const u8{
    "Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md",
};

const BUILD_PATH = [_][]const u8{
    "zigux/tests/phase11_gpio_wdt_current_head_manifest_survey_build.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_CURRENT_HEAD_SURFACES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GAP_SUMMARY) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MODULE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TEARDOWN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REMOVE_HANDOFF_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
    for (MODULE_PATH) |marker| try guard.requireMarker(text, marker);
    for (TEARDOWN_PATH) |marker| try guard.requireMarker(text, marker);
    for (REMOVE_HANDOFF_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_PATH) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}

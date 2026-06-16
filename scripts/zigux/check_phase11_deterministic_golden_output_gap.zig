const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_DETERMINISTIC_GOLDEN_OUTPUT_GAP_SELF_TEST=pass";

const EXPECTED_FIXTURE_SURFACES = [_][]const u8{
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
};

const EXPECTED_FOCUSED_BUILDS = [_][]const u8{
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
};

const EXPECTED_GAP = [_][]const u8{
    "phase11-validate now carries the dedicated golden-output fixture roster `zigux/tests/fixtures/phase11_validate_checks.json` plus fail-closed `scripts/zigux/check_phase11_validate_check_roster.zig` and `scripts/zigux/check_phase11_validate_route_alignment.zig` guards; keep future deterministic output drift inside that validator packet",
};

const SURVEY_MARKERS = [_][]const u8{
    "`PHASE11_DETERMINISTIC_TOOLING_GAP_STATUS=refresh_route_and_artifact_diff_guard_missing`",
    "lane: `P11-L07`",
    "Current `master` already ships the narrower machine-readable deterministic surfaces through:",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/fixtures/phase11_validate_checks.json`",
    "`zigux/tests/phase11_dw_wdt_manifest.json`",
    "`scripts\zigux/validate_phase11.zig`",
    "`make -C zigux phase11-validate`",
    "`scripts/zigux/check_phase11_validate_check_roster.zig`",
    "`scripts/zigux/check_phase11_validate_route_alignment.zig`",
    "Current `master` still does not ship:",
    "a dedicated refresh helper route for shared Phase 11 expected outputs",
    "an artifact-diff-style deterministic output guard for the driver-local proof builds",
    "inventory-backed and build-proof-first, yet it cannot refresh and diff stable golden outputs",
};

const MATRIX_MARKERS = [_][]const u8{
    "deterministic tooling survey lane: `P11-L07`",
    "It still does not rematerialize a refresh helper route or an artifact-diff-style deterministic output guard for the driver-local proof builds.",
    "That leaves a narrower roadmap-facing deterministic tooling gap",
};

const REQUIRED_VALIDATE_CHECK_NAMES = [_][]const u8{
    "phase11-validate-check-roster-self-test",
    "phase11-validate-check-roster",
    "phase11-validate-route-alignment-self-test",
    "phase11-validate-route-alignment",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_FIXTURE_SURFACES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_FOCUSED_BUILDS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GAP) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_VALIDATE_CHECK_NAMES) |marker| try guard.requireMarker(text, marker);
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

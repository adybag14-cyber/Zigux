const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_DETERMINISTIC_FIXTURE_GOLDEN_OUTPUT=pass";

const DEFAULT_ROOT = [_][]const u8{
    "Path.resolve.parents[2]iflen>3elsePath.cwd",
};

const EXPECTED_DETERMINISTIC_FIXTURE_SURFACES = [_][]const u8{
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
};

const EXPECTED_GOLDEN_OUTPUT_MARKERS = [_][]const u8{
    "phase11-validate now carries the dedicated golden-output fixture roster",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
    "scripts/zigux/check_phase11_validate_check_roster.zig",
    "scripts/zigux/check_phase11_validate_route_alignment.zig",
    "scripts/zigux/check_phase11_deterministic_fixture_golden_output.zig",
    "scripts/zigux/check_phase11_dw_wdt_build_route.zig",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "inside the deterministic validator packet",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (DEFAULT_ROOT) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_DETERMINISTIC_FIXTURE_SURFACES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GOLDEN_OUTPUT_MARKERS) |marker| try guard.requireMarker(text, marker);
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

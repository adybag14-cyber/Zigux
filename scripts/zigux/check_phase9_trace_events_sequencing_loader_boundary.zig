const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_TRACE_EVENTS_SEQUENCING_LOADER_BOUNDARY_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "Trusted GitHub rereads on 2026-05-25 directly recover the still-live shared loader packet through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the still-returned `samples/zigux/runtime_bitmap_loader.zig` scaffold, and the bounded `zigux/tests/phase9_build.zig` shard.",
    "`zigux/tests/phase9_build.zig` still exposes `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, and `phase9-runtime-trace-events-loader-substrate-drift-tests`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig` keeps the command/environment guard reviewable on current `master` by fail-closing when argv or environment control markers bleed into `zigux/kernel/runtime_loader.zig` or `zigux/kernel/runtime_loader_contract.zig`",
    "the review-first shared packet still stays neighboring shared-owner evidence through the aligned docs-root, scripts-root, and tests-root reminders, the bounded loader shard, and the direct command/environment boundary guard",
    "that broader bitmap-side visibility still must not be used to imply that the broader shared runtime-loader or blocked publication boundaries returned",
    "3. the bitmap side keeps a broader direct packet on trusted rereads, so current `master` supports a bounded runtime bitmap reminder packet plus the returned shared allocator/init-flow and command/environment boundary packet, not proof that the broader bitmap family returned",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "the broader runtime-loader packet is absent",
    "does not currently expose the broader shared runtime-loader packet",
    "full publication completion",
};

const SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
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

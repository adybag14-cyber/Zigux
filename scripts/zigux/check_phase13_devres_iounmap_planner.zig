const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_IOUNMAP_PLANNER_SELF_TEST=pass";

const FORBIDDEN_HELPER_MARKERS = [_][]const u8{
    "devm_iounmap(",
    "devm_ioremap_np(",
    "devm_of_iomap(",
    "devm_arch_phys_wc_add(",
    "devm_arch_io_reserve_memtype_wc(",
};

const REQUIRED_MARKERS = [_][]const u8{
    ".provides_iounmap_cleanup_planning = true",
    ".touches_live_mmio = false",
    "pub fn planManagedIounmapCleanup",
    "pure `devm_iounmap()` cleanup planning surface",
    "records whether a tracked mapping owner generates cleanup work",
    "warn-on-release-miss outcome",
    "devm_ioremap_np()",
    "devm_of_iomap()",
    "\"packet\": \"phase13-devres-iounmap-planner\"",
    "\"status\": \"starter_landed\"",
    "\"iounmap_cleanup_owner\": \"zigux/tests/phase13_devres_iounmap_planner.zig\"",
    "\"id\": \"phase13-devres-live-mmio-mapping-state\"",
    "phase13 devres descriptor records helper-first iounmap cleanup planning",
    "phase13 devres iounmap planner note keeps the helper-first mmio slice bounded",
    "phase13 devres iounmap planner checker stays packet-local",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (FORBIDDEN_HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
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

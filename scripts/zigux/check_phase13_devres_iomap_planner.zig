const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_IOMAP_PLANNER_SELF_TEST=pass";

const FORBIDDEN_HELPER_MARKERS = [_][]const u8{
    "devm_ioremap_np(",
    "devm_iounmap(",
    "devm_of_iomap(",
    "devm_arch_phys_wc_add(",
    "devm_arch_io_reserve_memtype_wc(",
};

const REQUIRED_MARKERS = [_][]const u8{
    ".provides_of_iomap_planning = true",
    ".provides_of_iomap_cleanup_handoff_planning = true",
    ".touches_live_mmio = false",
    "requires_nonposted_ioremap",
    "pub fn planDeviceTreeIomap",
    "pub fn planDeviceTreeIomapCleanupHandoff",
    "pure `devm_of_iomap()` planning surface",
    "translated size is preserved when a requested region is denied as busy",
    "requested region is released again when remap later fails",
    "requested non-posted mapping type stays attached to the planning surface",
    "translated helper-first remap would require the still-blocked `devm_ioremap_np()` wrapper",
    "successful helper-first remap hands off to `devm_iounmap()` cleanup planning",
    "cleanup handoff consumes the matching release record or still warns when the release record is missing",
    "devm_ioremap_np()",
    "devm_iounmap()",
    "devm_arch_phys_wc_add()",
    "devm_arch_io_reserve_memtype_wc()",
    "\"lane_key\": \"P13-L02\"",
    "\"phase\": \"Phase 13\"",
    "\"packet\": \"phase13-devres-iomap-planner\"",
    "\"status\": \"starter_landed\"",
    "\"translation_miss_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"request_region_denial_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"nonposted_wrapper_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"remap_failure_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"cleanup_handoff_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"cleanup_release_miss_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "planDeviceTreeIomapCleanupHandoff",
    "requires_nonposted_ioremap",
    "\"id\": \"phase13-devres-missing-devm-ioremap-np-surface\"",
    "\"id\": \"phase13-devres-missing-devm-arch-phys-wc-add-surface\"",
    "\"id\": \"phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface\"",
    "\"id\": \"phase13-devres-live-mmio-mapping-state\"",
    "\"id\": \"phase13-devres-live-device-tree-walks\"",
    "\"id\": \"phase13-devres-live-arch-memtype-mutation\"",
    "phase13 devres descriptor records helper-first iomap planning",
    "phase13 devres iomap planning keeps the blocked non-posted wrapper requirement explicit",
    "phase13 devres iomap cleanup handoff materializes helper-first iounmap cleanup after successful remap",
    "phase13 devres iomap cleanup handoff keeps missing release records warnable",
    "phase13 devres iomap cleanup handoff stays inert before remap readiness",
    "phase13 devres iomap planner manifest records the landed helper-first mmio scope",
    "phase13 devres iomap planner note keeps the helper-first mmio slice bounded",
    "phase13 devres iomap planner checker stays packet-local",
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

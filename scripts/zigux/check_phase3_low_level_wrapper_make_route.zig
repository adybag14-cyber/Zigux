const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_LOW_LEVEL_WRAPPER_MAKE_ROUTE=pass";
pub const self_test_pass_marker = "PHASE3_LOW_LEVEL_WRAPPER_MAKE_ROUTE_SELF_TEST=pass";

const REQUIRED_PHASE3_AGGREGATE = [_][]const u8{
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
};

const REQUIRED_SHARED_ROUTE = [_][]const u8{
    "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
};

const REQUIRED_FOCUSED_ROUTE = [_][]const u8{
    "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
};

const STALE_PHASE3_AGGREGATES = [_][]const u8{
    "phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-dump",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_phase3_aggregate_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_phase3_aggregate_path);
    const text_required_phase3_aggregate = try guard.readUtf8File(io, allocator, text_required_phase3_aggregate_path);
    defer allocator.free(text_required_phase3_aggregate);
    for (REQUIRED_PHASE3_AGGREGATE) |marker| try guard.requireMarker(text_required_phase3_aggregate, marker);
    const text_required_shared_route_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_shared_route_path);
    const text_required_shared_route = try guard.readUtf8File(io, allocator, text_required_shared_route_path);
    defer allocator.free(text_required_shared_route);
    for (REQUIRED_SHARED_ROUTE) |marker| try guard.requireMarker(text_required_shared_route, marker);
    const text_required_focused_route_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_focused_route_path);
    const text_required_focused_route = try guard.readUtf8File(io, allocator, text_required_focused_route_path);
    defer allocator.free(text_required_focused_route);
    for (REQUIRED_FOCUSED_ROUTE) |marker| try guard.requireMarker(text_required_focused_route, marker);
    const text_stale_phase3_aggregates_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_stale_phase3_aggregates_path);
    const text_stale_phase3_aggregates = try guard.readUtf8File(io, allocator, text_stale_phase3_aggregates_path);
    defer allocator.free(text_stale_phase3_aggregates);
    for (STALE_PHASE3_AGGREGATES) |marker| try guard.requireMarker(text_stale_phase3_aggregates, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

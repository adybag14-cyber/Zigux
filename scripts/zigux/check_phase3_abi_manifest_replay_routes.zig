const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ABI_MANIFEST_REPLAY_ROUTES=pass";
pub const self_test_pass_marker = "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass",
    "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST_CASE_COUNT=",
};

const live_output_markers = [_][]const u8{
    "PHASE3_ABI_MANIFEST_REPLAY_ROUTES=pass",
};

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "keep the shared Phase 3 policy, export/UAPI, low-level wrapper packet, and retired generated-packet guard aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again",
};

const markers_1 = [_][]const u8{
    "zigux/tests/phase3_abi_dump.zig",
    "These retired generated paths are historical markers only; the live export/UAPI-adjacent ABI packet must keep the dump_current replay as its only generated dump surface.",
    "The live Phase 3 ABI evidence packet is the dump_current-era manifest replay; the older generated dump name and expected snapshot fixture are intentionally retired.",
    "\"phase\": \"Phase 3\"",
    "\"replay_routes\"",
    "zig run scripts/zigux/check_phase3_abi_manifest_replay_routes.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_abi_manifest_replay_routes.zig",
};

const markers_2 = [_][]const u8{
    "zigux/tests/fixtures/phase3_abi/expected.json",
};

const markers_3 = [_][]const u8{
    "zigux/tests/phase3_abi_dump_current.zig",
};

const markers_4 = [_][]const u8{
    "zig run scripts/zigux/check_phase3_abi.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_abi.zig",
};

const contracts = [_]FileContract{
    .{ .rel = "scripts/zigux/validate_phase3.zig", .markers = &markers_0 },
    .{ .rel = "zigux/tests/fixtures/phase3_abi_manifest.json", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase3-roadmap-interop-gap-survey.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase3-abi-h-boundary-next-step.md", .markers = &markers_3 },
    .{ .rel = "scripts/zigux/run_phase3_checks.zig", .markers = &markers_4 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "="))
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len })
        else
            try guard.printLine(io, "{s}", .{marker});
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const owner_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(owner_path);
        const text = try guard.readUtf8File(io, allocator, owner_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try printOutputMarkers(io, &self_test_output_markers);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}

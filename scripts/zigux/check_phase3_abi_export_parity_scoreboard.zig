const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ABI_EXPORT_PARITY_SCOREBOARD=pass";
pub const self_test_pass_marker = "PHASE3_ABI_EXPORT_PARITY_SCOREBOARD_SELF_TEST=pass";

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig",
    "zig run scripts\\zigux/validate_phase3_export_uapi_survey.zig -- --self-test",
    "zig run scripts\\zigux/validate_phase3_export_uapi_survey.zig",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "make -C zigux phase3-export-shim-test",
    "make -C zigux phase3-export-uapi-layout",
    "make -C zigux phase3-export-uapi-layout-test",
    "zig build phase3-abi-export --build-file zigux/tests/build.zig",
    "make -C zigux phase3-abi-export",
};

const CURRENT_GENERATED_DUMP = [_][]const u8{
    "zigux/tests/phase3_abi_dump_current.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3_abi_manifest.json");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
    const text_current_generated_dump_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3_abi_manifest.json");
    defer allocator.free(text_current_generated_dump_path);
    const text_current_generated_dump = try guard.readUtf8File(io, allocator, text_current_generated_dump_path);
    defer allocator.free(text_current_generated_dump);
    for (CURRENT_GENERATED_DUMP) |marker| try guard.requireMarker(text_current_generated_dump, marker);
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

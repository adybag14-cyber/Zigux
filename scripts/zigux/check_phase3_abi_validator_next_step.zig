const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ABI_VALIDATOR_NEXT_STEP=pass";
pub const self_test_pass_marker = "PHASE3_ABI_VALIDATOR_NEXT_STEP_SELF_TEST=pass";

const CURRENT_DUMP = [_][]const u8{
    "zigux/tests/phase3_abi_dump_current.zig",
};

const RETIRED_DUMP = [_][]const u8{
    "zigux/tests/phase3_abi_dump.zig",
};

const RETIRED_EXPECTED = [_][]const u8{
    "zigux/tests/fixtures/phase3_abi/expected.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_current_dump_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase3.zig");
    defer allocator.free(text_current_dump_path);
    const text_current_dump = try guard.readUtf8File(io, allocator, text_current_dump_path);
    defer allocator.free(text_current_dump);
    for (CURRENT_DUMP) |marker| try guard.requireMarker(text_current_dump, marker);
    const text_retired_dump_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase3.zig");
    defer allocator.free(text_retired_dump_path);
    const text_retired_dump = try guard.readUtf8File(io, allocator, text_retired_dump_path);
    defer allocator.free(text_retired_dump);
    for (RETIRED_DUMP) |marker| try guard.requireMarker(text_retired_dump, marker);
    const text_retired_expected_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase3.zig");
    defer allocator.free(text_retired_expected_path);
    const text_retired_expected = try guard.readUtf8File(io, allocator, text_retired_expected_path);
    defer allocator.free(text_retired_expected);
    for (RETIRED_EXPECTED) |marker| try guard.requireMarker(text_retired_expected, marker);
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

const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ABI_MANIFEST_REPLAY_ROUTES=pass";
pub const self_test_pass_marker = "PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass";

const CURRENT_NEXT_SAFE_STEP = [_][]const u8{
    "keep the shared Phase 3 policy, export/UAPI, low-level wrapper packet, and retired generated-packet guard aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again",
};

const RETIRED_DUMP = [_][]const u8{
    "zigux/tests/phase3_abi_dump.zig",
};

const RETIRED_EXPECTED = [_][]const u8{
    "zigux/tests/fixtures/phase3_abi/expected.json",
};

const CURRENT_DUMP = [_][]const u8{
    "zigux/tests/phase3_abi_dump_current.zig",
};

const RETIRED_GUARD_NOTE = [_][]const u8{
    "These retired generated paths are historical markers only; the live export/UAPI-adjacent ABI packet must keep the dump_current replay as its only generated dump surface.",
};

const GENERATED_PACKET_NOTE = [_][]const u8{
    "The live Phase 3 ABI evidence packet is the dump_current-era manifest replay; the older generated dump name and expected snapshot fixture are intentionally retired.",
};

const SELFTEST_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_abi.zig --self-test",
    "zig run scripts\\zigux/check_phase3_abi.zig",
    "zig run scripts\\zigux/validate_phase3.zig --self-test",
    "zig run scripts\\zigux/validate_phase3.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_current_next_safe_step_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase3.zig");
    defer allocator.free(text_current_next_safe_step_path);
    const text_current_next_safe_step = try guard.readUtf8File(io, allocator, text_current_next_safe_step_path);
    defer allocator.free(text_current_next_safe_step);
    for (CURRENT_NEXT_SAFE_STEP) |marker| try guard.requireMarker(text_current_next_safe_step, marker);
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
    const text_current_dump_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase3.zig");
    defer allocator.free(text_current_dump_path);
    const text_current_dump = try guard.readUtf8File(io, allocator, text_current_dump_path);
    defer allocator.free(text_current_dump);
    for (CURRENT_DUMP) |marker| try guard.requireMarker(text_current_dump, marker);
    const text_retired_guard_note_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase3.zig");
    defer allocator.free(text_retired_guard_note_path);
    const text_retired_guard_note = try guard.readUtf8File(io, allocator, text_retired_guard_note_path);
    defer allocator.free(text_retired_guard_note);
    for (RETIRED_GUARD_NOTE) |marker| try guard.requireMarker(text_retired_guard_note, marker);
    const text_generated_packet_note_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase3.zig");
    defer allocator.free(text_generated_packet_note_path);
    const text_generated_packet_note = try guard.readUtf8File(io, allocator, text_generated_packet_note_path);
    defer allocator.free(text_generated_packet_note);
    for (GENERATED_PACKET_NOTE) |marker| try guard.requireMarker(text_generated_packet_note, marker);
    const text_selftest_replay_routes_path = try guard.joinPath(allocator, root, "scripts\zigux/validate_phase3.zig");
    defer allocator.free(text_selftest_replay_routes_path);
    const text_selftest_replay_routes = try guard.readUtf8File(io, allocator, text_selftest_replay_routes_path);
    defer allocator.free(text_selftest_replay_routes);
    for (SELFTEST_REPLAY_ROUTES) |marker| try guard.requireMarker(text_selftest_replay_routes, marker);
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

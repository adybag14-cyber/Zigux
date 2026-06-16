const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_RBTREE_FIXTURE_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE7_RBTREE_FIXTURE_ALIGNMENT_SELF_TEST=pass";

const JSON_PATH = [_][]const u8{
    "zigux/tests/fixtures/phase7_rbtree.json",
};

const HARNESS_PATH = [_][]const u8{
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
};

const EXPECTED_PACKET = [_][]const u8{
    "phase7-rbtree-parity-fixture",
};

const EXPECTED_ANCHOR = [_][]const u8{
    "lib/rbtree.c",
};

const EXPECTED_JSON_STATE = [_][]const u8{
    "ordered-duplicate-cached-postorder-reverse",
};

const EXPECTED_HARNESS_STATE = [_][]const u8{
    "ordered-duplicate-cached-postorder-reverse-c-harness",
};

const EXPECTED_SCENARIOS = [_][]const u8{
    "ordered_duplicate_range",
    "cached_leftmost_promotion",
    "postorder_null_stop",
    "reverse_alias_detached",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_json_path_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase7_rbtree.json");
    defer allocator.free(text_json_path_path);
    const text_json_path = try guard.readUtf8File(io, allocator, text_json_path_path);
    defer allocator.free(text_json_path);
    for (JSON_PATH) |marker| try guard.requireMarker(text_json_path, marker);
    const text_harness_path_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase7_rbtree.json");
    defer allocator.free(text_harness_path_path);
    const text_harness_path = try guard.readUtf8File(io, allocator, text_harness_path_path);
    defer allocator.free(text_harness_path);
    for (HARNESS_PATH) |marker| try guard.requireMarker(text_harness_path, marker);
    const text_expected_packet_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase7_rbtree.json");
    defer allocator.free(text_expected_packet_path);
    const text_expected_packet = try guard.readUtf8File(io, allocator, text_expected_packet_path);
    defer allocator.free(text_expected_packet);
    for (EXPECTED_PACKET) |marker| try guard.requireMarker(text_expected_packet, marker);
    const text_expected_anchor_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase7_rbtree.json");
    defer allocator.free(text_expected_anchor_path);
    const text_expected_anchor = try guard.readUtf8File(io, allocator, text_expected_anchor_path);
    defer allocator.free(text_expected_anchor);
    for (EXPECTED_ANCHOR) |marker| try guard.requireMarker(text_expected_anchor, marker);
    const text_expected_json_state_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase7_rbtree.json");
    defer allocator.free(text_expected_json_state_path);
    const text_expected_json_state = try guard.readUtf8File(io, allocator, text_expected_json_state_path);
    defer allocator.free(text_expected_json_state);
    for (EXPECTED_JSON_STATE) |marker| try guard.requireMarker(text_expected_json_state, marker);
    const text_expected_harness_state_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase7_rbtree.json");
    defer allocator.free(text_expected_harness_state_path);
    const text_expected_harness_state = try guard.readUtf8File(io, allocator, text_expected_harness_state_path);
    defer allocator.free(text_expected_harness_state);
    for (EXPECTED_HARNESS_STATE) |marker| try guard.requireMarker(text_expected_harness_state, marker);
    const text_expected_scenarios_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase7_rbtree.json");
    defer allocator.free(text_expected_scenarios_path);
    const text_expected_scenarios = try guard.readUtf8File(io, allocator, text_expected_scenarios_path);
    defer allocator.free(text_expected_scenarios);
    for (EXPECTED_SCENARIOS) |marker| try guard.requireMarker(text_expected_scenarios, marker);
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

const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_NOTIFIER_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_NOTIFIER_STARTER_PACKET_SELF_TEST=pass";

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_notifier_starter_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_notifier_starter_packet.zig -- --repo-root .",
    "zig build phase3-notifier-starter-packet-test --build-file zigux/tests/phase3_notifier_starter_packet_build.zig",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-notifier-slice_md = [_][]const u8{
    "# Phase 3 notifier Slice",
    "- `Documentation/zigux/phase3-notifier-slice.md`",
    "- `zigux/bindings/notifier_abi.zig`",
    "- `zigux/tests/phase3_notifier_starter_packet.zig`",
    "This packet stays intentionally small:",
    "The landed packet only closes the bounded notifier ABI replay slice.",
};

const REQUIRED_MARKERS__zigux_bindings_notifier_abi_zig = [_][]const u8{
    "pub const NotifierResult = enum(u32) {",
    "pub const NotifierBlock = extern struct {",
    "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
    "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?NotifierChainPriorityIncrease {",
    "pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {",
    "pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {",
    "test \"notifier priority helper rejects increasing priority\" {",
    "test \"hlist helper rejects a broken prev-link\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_notifier_starter_packet_zig = [_][]const u8{
    "test \"notifier starter packet keeps result bytes explicit\" {",
    "test \"notifier starter packet keeps layout anchors explicit\" {",
    "test \"notifier starter packet keeps nonincreasing priority chains accepted\" {",
    "test \"notifier starter packet reports the first priority increase\" {",
    "test \"notifier starter packet keeps list backlink drift explicit\" {",
    "test \"notifier starter packet keeps hlist prev-link drift explicit\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_notifier_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../bindings/notifier_abi.zig\"),",
    ".root_source_file = b.path(\"phase3_notifier_starter_packet.zig\"),",
    "root_module.addImport(\"notifier_abi\", notifier_abi);",
    "\"phase3-notifier-starter-packet-test\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-notifier-slice.md");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
    const text_required_markers__documentation_zigux_phase3-notifier-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-notifier-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-notifier-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-notifier-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-notifier-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-notifier-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-notifier-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-notifier-slice_md, marker);
    const text_required_markers__zigux_bindings_notifier_abi_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/notifier/abi/zig");
    defer allocator.free(text_required_markers__zigux_bindings_notifier_abi_zig_path);
    const text_required_markers__zigux_bindings_notifier_abi_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_notifier_abi_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_notifier_abi_zig);
    for (REQUIRED_MARKERS__zigux_bindings_notifier_abi_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_notifier_abi_zig, marker);
    const text_required_markers__zigux_tests_phase3_notifier_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/notifier/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_notifier_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_notifier_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_notifier_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_notifier_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_notifier_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_notifier_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_notifier_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/notifier/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_notifier_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_notifier_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_notifier_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_notifier_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_notifier_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_notifier_starter_packet_build_zig, marker);
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

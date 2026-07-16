const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_LIST_HLIST_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST=pass",
    "PHASE3_LIST_HLIST_STARTER_PACKET_SELF_TEST_CASE_COUNT=",
};

const live_output_markers = [_][]const u8{
    "validated zigux/helpers/list_view.zig",
    "validated zigux/helpers/hlist_view.zig",
    "validated zigux/tests/phase3_list_hlist_starter_packet.zig",
    "validated zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "validated zigux/tests/fixtures/phase3_list_hlist_manifest.json",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "This note records one bounded shared-helper starter-plus-dump packet for the existing Phase 3 `list_head` and `hlist` helpers on current `master`.",
    "`zigux/helpers/list_view.zig`",
    "`zigux/helpers/hlist_view.zig`",
    "`zigux/tests/phase3_list_hlist_starter_packet.zig`",
    "`zigux/tests/phase3_list_hlist_starter_packet_build.zig`",
    "`zigux/tests/phase3_list_hlist_dump.zig`",
    "`zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`",
    "`zigux/tests/fixtures/phase3_list_hlist_manifest.json`",
    "`scripts\\zigux/check_phase3_list_hlist_starter_packet.zig`",
    "`scripts\\zigux/check_phase3_list_hlist.zig`",
    "`zigux/Makefile`",
    "make -C zigux phase3-list-hlist-starter-packet",
    "make -C zigux phase3-list-hlist-dump",
    "It does not claim exported ABI structs, intrusive container recovery helpers, list mutation semantics, or wider subsystem-specific list ownership behavior.",
};

const markers_1 = [_][]const u8{
    "pub const ListView = struct {",
    "pub fn first(self: ListView) ?*const ListHead {",
    "pub fn last(self: ListView) ?*const ListHead {",
    "pub fn hasConsistentBacklinks(self: ListView) bool {",
    "pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak {",
};

const markers_2 = [_][]const u8{
    "pub const HListView = struct {",
    "pub fn first(self: HListView) ?*const HListNode {",
    "pub fn firstPprevMatchesHead(self: HListView) bool {",
    "pub fn hasConsistentPrevLinks(self: HListView) bool {",
    "pub fn tailNextIsNull(self: HListView) bool {",
};

const markers_3 = [_][]const u8{
    "test \"list starter packet keeps a sentinel-only list empty and reviewable\" {",
    "test \"list starter packet keeps circular ordering and broken backlinks explicit\" {",
    "test \"hlist starter packet keeps empty heads and bounded chains explicit\" {",
    "test \"hlist starter packet reports the first broken prev-link witness\" {",
};

const markers_4 = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/list_view.zig\"),",
    ".root_source_file = b.path(\"../helpers/hlist_view.zig\"),",
    ".root_source_file = b.path(\"phase3_list_hlist_starter_packet.zig\"),",
    "root_module.addImport(\"list_view\", list_view);",
    "root_module.addImport(\"hlist_view\", hlist_view);",
    "\"phase3-list-hlist-starter-packet\"",
    "\"Run the shared Phase 3 list/hlist starter packet\"",
};

const markers_5 = [_][]const u8{
    "phase3-list-hlist-starter-packet:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "phase3-list-hlist-dump:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig",
};

const markers_6 = [_][]const u8{
    "\"slug\": \"phase3-list-hlist\"",
    "\"status\": \"starter_and_dump_packet_present\"",
    "\"zigux/tests/phase3_list_hlist_starter_packet.zig\"",
    "\"zigux/tests/phase3_list_hlist_dump.zig\"",
    "\"scripts\\zigux/check_phase3_list_hlist_starter_packet.zig\"",
    "\"scripts\\zigux/check_phase3_list_hlist.zig\"",
    "\"zigux/Makefile\"",
    "\"make -C zigux phase3-list-hlist-starter-packet\"",
    "\"make -C zigux phase3-list-hlist-dump\"",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-list-hlist-slice.md", .markers = &markers_0 },
    .{ .rel = "zigux/helpers/list_view.zig", .markers = &markers_1 },
    .{ .rel = "zigux/helpers/hlist_view.zig", .markers = &markers_2 },
    .{ .rel = "zigux/tests/phase3_list_hlist_starter_packet.zig", .markers = &markers_3 },
    .{ .rel = "zigux/tests/phase3_list_hlist_starter_packet_build.zig", .markers = &markers_4 },
    .{ .rel = "zigux/Makefile", .markers = &markers_5 },
    .{ .rel = "zigux/tests/fixtures/phase3_list_hlist_manifest.json", .markers = &markers_6 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "=")) {
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len });
        } else {
            try guard.printLine(io, "{s}", .{marker});
        }
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
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
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) std.process.exit(try runSelfTest(io, allocator));

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}

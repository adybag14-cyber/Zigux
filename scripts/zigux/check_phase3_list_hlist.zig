const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_LIST_HLIST=pass";
pub const self_test_pass_marker = "PHASE3_LIST_HLIST_SELF_TEST=pass";

const REQUIRED_MARKERS__Documentation_zigux_phase3-list-hlist-slice_md = [_][]const u8{
    "This note records one bounded shared-helper starter-plus-dump packet for the existing Phase 3 `list_head` and `hlist` helpers on current `master`.",
    "`zigux/tests/phase3_list_hlist_dump.zig`",
    "`zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`",
    "`scripts\\zigux/check_phase3_list_hlist.zig`",
    "`zigux/Makefile`",
    "`zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig`",
    "`make -C zigux phase3-list-hlist-starter-packet`",
    "`make -C zigux phase3-list-hlist-dump`",
};

const REQUIRED_MARKERS__zigux_helpers_list_view_zig = [_][]const u8{
    "pub const ListView = struct {",
    "pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak {",
};

const REQUIRED_MARKERS__zigux_helpers_hlist_view_zig = [_][]const u8{
    "pub const HListView = struct {",
    "pub fn firstBrokenPrevLink(self: HListView) ?PrevLinkBreak {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_list_hlist_starter_packet_zig = [_][]const u8{
    "test \"list starter packet keeps circular ordering and broken backlinks explicit\" {",
    "test \"hlist starter packet reports the first broken prev-link witness\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_list_hlist_starter_packet_build_zig = [_][]const u8{
    "\"phase3-list-hlist-starter-packet\"",
    "root_module.addImport(\"list_view\", list_view);",
    "root_module.addImport(\"hlist_view\", hlist_view);",
};

const REQUIRED_MARKERS__zigux_tests_phase3_list_hlist_dump_zig = [_][]const u8{
    "const list_view = @import(\"list_view\");",
    "const hlist_view = @import(\"hlist_view\");",
    "try writeListCase(writer, \"broken_backlink\", &list_broken_head, &list_broken_first, &list_broken_second, false);",
    "try writeHListCase(writer, \"broken_prev_link\", &hlist_broken_head, &hlist_broken_first, &hlist_broken_second, false);",
};

const REQUIRED_MARKERS__zigux_tests_phase3_list_hlist_dump_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"phase3_list_hlist_dump.zig\"),",
    "\"phase3-list-hlist-dump\"",
};

const REQUIRED_MARKERS__zigux_Makefile = [_][]const u8{
    "phase3-list-hlist-starter-packet:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "phase3-list-hlist-dump:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_list_hlist_phase3_list_hlist_c_harness_c = [_][]const u8{
    "write_list_case(\"broken_backlink\", &list_broken_head, &list_broken_first, &list_broken_second, false);",
    "write_hlist_case(\"broken_prev_link\", &hlist_broken_head, &hlist_broken_first, &hlist_broken_second, false);",
    "if (raw == ptr_of(&head->first)) return \"head.first\";",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_list_hlist_expected_json = [_][]const u8{
    "\"word_bits\": 64",
    "\"name\": \"broken_backlink\"",
    "\"expected_prev_label\": \"node0\"",
    "\"name\": \"broken_prev_link\"",
    "\"expected_pprev_label\": \"node0.next\"",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_list_hlist_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-list-hlist\"",
    "\"status\": \"starter_and_dump_packet_present\"",
    "\"zigux/tests/phase3_list_hlist_dump.zig\"",
    "\"scripts\\zigux/check_phase3_list_hlist.zig\"",
    "\"zigux/Makefile\"",
    "\"make -C zigux phase3-list-hlist-starter-packet\"",
    "\"make -C zigux phase3-list-hlist-dump\"",
};

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_list_hlist_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_list_hlist_starter_packet.zig",
    "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "make -C zigux phase3-list-hlist-starter-packet",
    "zig run scripts\\zigux/check_phase3_list_hlist.zig --self-test",
    "zig run scripts\\zigux/check_phase3_list_hlist.zig --repo-root . --zig zig --cc gcc",
    "zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig",
    "make -C zigux phase3-list-hlist-dump",
};

const SELF_TEST_CASES = [_][]const u8{
    "This note records one bounded shared-helper starter-plus-dump packet for the existing Phase 3 `list_head` and `hlist` helpers on current `master`.",
    "try writeListCase(writer, \"broken_backlink\", &list_broken_head, &list_broken_first, &list_broken_second, false);",
    "phase3-list-hlist-dump:",
    "write_hlist_case(\"broken_prev_link\", &hlist_broken_head, &hlist_broken_first, &hlist_broken_second, false);",
    "\"expected_pprev_label\": \"node0.next\"",
    "\"status\": \"starter_and_dump_packet_present\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__documentation_zigux_phase3-list-hlist-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-list-hlist-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-list-hlist-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-list-hlist-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-list-hlist-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-list-hlist-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-list-hlist-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-list-hlist-slice_md, marker);
    const text_required_markers__zigux_helpers_list_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/list/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_list_view_zig_path);
    const text_required_markers__zigux_helpers_list_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_list_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_list_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_list_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_list_view_zig, marker);
    const text_required_markers__zigux_helpers_hlist_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/hlist/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_hlist_view_zig_path);
    const text_required_markers__zigux_helpers_hlist_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_hlist_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_hlist_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_hlist_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_hlist_view_zig, marker);
    const text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/list/hlist/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_list_hlist_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/list/hlist/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_list_hlist_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_list_hlist_starter_packet_build_zig, marker);
    const text_required_markers__zigux_tests_phase3_list_hlist_dump_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/list/hlist/dump/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_list_hlist_dump_zig_path);
    const text_required_markers__zigux_tests_phase3_list_hlist_dump_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_list_hlist_dump_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_list_hlist_dump_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_list_hlist_dump_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_list_hlist_dump_zig, marker);
    const text_required_markers__zigux_tests_phase3_list_hlist_dump_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/list/hlist/dump/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_list_hlist_dump_build_zig_path);
    const text_required_markers__zigux_tests_phase3_list_hlist_dump_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_list_hlist_dump_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_list_hlist_dump_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_list_hlist_dump_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_list_hlist_dump_build_zig, marker);
    const text_required_markers__zigux_makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_markers__zigux_makefile_path);
    const text_required_markers__zigux_makefile = try guard.readUtf8File(io, allocator, text_required_markers__zigux_makefile_path);
    defer allocator.free(text_required_markers__zigux_makefile);
    for (REQUIRED_MARKERS__zigux_Makefile) |marker| try guard.requireMarker(text_required_markers__zigux_makefile, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_list_hlist_phase3_list_hlist_c_harness_c_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/list/hlist/phase3/list/hlist/c/harness/c");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_list_hlist_phase3_list_hlist_c_harness_c_path);
    const text_required_markers__zigux_tests_fixtures_phase3_list_hlist_phase3_list_hlist_c_harness_c = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_list_hlist_phase3_list_hlist_c_harness_c_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_list_hlist_phase3_list_hlist_c_harness_c);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_list_hlist_phase3_list_hlist_c_harness_c) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_list_hlist_phase3_list_hlist_c_harness_c, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_list_hlist_expected_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/list/hlist/expected/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_list_hlist_expected_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_list_hlist_expected_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_list_hlist_expected_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_list_hlist_expected_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_list_hlist_expected_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_list_hlist_expected_json, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_list_hlist_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/list/hlist/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_list_hlist_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_list_hlist_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_list_hlist_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_list_hlist_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_list_hlist_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_list_hlist_manifest_json, marker);
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-list-hlist-slice.md");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
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

const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_RBTREE_ROOT_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_RBTREE_ROOT_PACKET_SELF_TEST=pass";

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_rbtree_root_starter_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_rbtree_root_starter_packet.zig",
    "zig build phase3-rbtree-root-starter-packet --build-file zigux/tests/phase3_rbtree_root_starter_packet_build.zig",
};

const REQUIRED_REPO_REALITY_GAPS = [_][]const u8{
    "zigux/tests/fixtures/phase3_rbtree_root/phase3_rbtree_root_c_harness.c",
    "zigux/tests/fixtures/phase3_rbtree_root/expected.json",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-rbtree-root-slice_md = [_][]const u8{
    "# Phase 3 rbtree root Slice",
    "`zigux/bindings/rbtree_root.zig`",
    "`zigux/helpers/rbtree_root_view.zig`",
    "`zigux/tests/phase3_rbtree_root_starter_packet.zig`",
    "`zigux/tests/phase3_rbtree_root_starter_packet_build.zig`",
    "`zigux/tests/fixtures/phase3_rbtree_root_manifest.json`",
    "`scripts\\zigux/check_phase3_rbtree_root_starter_packet.zig`",
    "zig build phase3-rbtree-root-starter-packet --build-file zigux/tests/phase3_rbtree_root_starter_packet_build.zig",
};

const REQUIRED_MARKERS__zigux_bindings_rbtree_root_zig = [_][]const u8{
    "const abi = @import(\"abi_bindings\");",
    "pub const RootView = abi.RbtreeRootView;",
    "pub fn empty() RootView {",
    "pub fn cached(root: usize, cached_leftmost: usize) RootView {",
    "pub fn canonicalize(view: RootView) ?RootView {",
};

const REQUIRED_MARKERS__zigux_helpers_rbtree_root_view_zig = [_][]const u8{
    "const rbtree = @import(\"rbtree_bindings\");",
    "pub const RootView = rbtree.RootView;",
    "pub fn cached(root: usize, cached_leftmost: usize) RootView {",
    "pub fn canonicalize(view: RootView) ?RootView {",
    "test \"phase3 rbtree root view helper rejects unknown flags and rootless payloads\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_rbtree_root_starter_packet_zig = [_][]const u8{
    "test \"rbtree root starter packet keeps the empty helper lane explicit\" {",
    "test \"rbtree root starter packet keeps uncached rooted views canonical\" {",
    "test \"rbtree root starter packet keeps cached leftmost relays explicit\" {",
    "test \"rbtree root starter packet keeps cached flag drift narrow\" {",
    "test \"rbtree root starter packet rejects unknown flags and rootless payloads\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_rbtree_root_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../bindings/rbtree_root.zig\"),",
    ".root_source_file = b.path(\"../helpers/rbtree_root_view.zig\"),",
    ".root_source_file = b.path(\"phase3_rbtree_root_starter_packet.zig\"),",
    "root_module.addImport(\"rbtree_bindings\", rbtree_bindings);",
    "\"phase3-rbtree-root-starter-packet\"",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_rbtree_root_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-rbtree-root-starter-packet\"",
    "\"status\": \"helper_local_rbtree_root_slice_present\"",
    "\"scripts\\zigux/check_phase3_rbtree_root_starter_packet.zig\"",
    "\"zigux/tests/fixtures/phase3_rbtree_root/phase3_rbtree_root_c_harness.c\"",
    "\"zigux/tests/fixtures/phase3_rbtree_root/expected.json\"",
};

const SELF_TEST_CASES = [_][]const u8{
    "`zigux/bindings/rbtree_root.zig`",
    "pub fn canonicalize(view: RootView) ?RootView {",
    "pub fn canonicalize(view: RootView) ?RootView {",
    "test \"rbtree root starter packet keeps cached flag drift narrow\" {",
    "\"phase3-rbtree-root-starter-packet\"",
    "\"status\": \"helper_local_rbtree_root_slice_present\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-rbtree-root-slice.md");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
    const text_required_repo_reality_gaps_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-rbtree-root-slice.md");
    defer allocator.free(text_required_repo_reality_gaps_path);
    const text_required_repo_reality_gaps = try guard.readUtf8File(io, allocator, text_required_repo_reality_gaps_path);
    defer allocator.free(text_required_repo_reality_gaps);
    for (REQUIRED_REPO_REALITY_GAPS) |marker| try guard.requireMarker(text_required_repo_reality_gaps, marker);
    const text_required_markers__documentation_zigux_phase3-rbtree-root-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-rbtree-root-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-rbtree-root-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-rbtree-root-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-rbtree-root-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-rbtree-root-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-rbtree-root-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-rbtree-root-slice_md, marker);
    const text_required_markers__zigux_bindings_rbtree_root_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/rbtree/root/zig");
    defer allocator.free(text_required_markers__zigux_bindings_rbtree_root_zig_path);
    const text_required_markers__zigux_bindings_rbtree_root_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_rbtree_root_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_rbtree_root_zig);
    for (REQUIRED_MARKERS__zigux_bindings_rbtree_root_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_rbtree_root_zig, marker);
    const text_required_markers__zigux_helpers_rbtree_root_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/rbtree/root/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_rbtree_root_view_zig_path);
    const text_required_markers__zigux_helpers_rbtree_root_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_rbtree_root_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_rbtree_root_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_rbtree_root_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_rbtree_root_view_zig, marker);
    const text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/rbtree/root/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_rbtree_root_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/rbtree/root/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_rbtree_root_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_rbtree_root_starter_packet_build_zig, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_rbtree_root_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/rbtree/root/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_rbtree_root_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_rbtree_root_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_rbtree_root_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_rbtree_root_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_rbtree_root_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_rbtree_root_manifest_json, marker);
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

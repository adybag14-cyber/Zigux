const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_LEAF_LIBRARIES_PACKET=pass";
pub const self_test_pass_marker = "PHASE7_LEAF_LIBRARIES_PACKET_SELF_TEST=pass";

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts/zigux/check_phase7_leaf_libraries.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_leaf_libraries.zig -- --repo-root . --skip-exec",
    "zig build phase7-leaf-libraries-starter-packet --build-file zigux/tests/phase7_leaf_libraries_starter_packet_build.zig",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-leaf-libraries_md = [_][]const u8{
    "This note records one bounded validation packet for the existing Phase 7 in-kernel leaf-library ports.",
    "`lib/string_helpers.zig`",
    "`lib/cmdline.zig`",
    "`lib/argv_split.zig`",
    "`lib/rbtree.zig`",
    "`zigux/tests/phase7_leaf_libraries_starter_packet.zig`",
    "`zigux/tests/phase7_leaf_libraries_starter_packet_build.zig`",
    "`zigux/tests/fixtures/phase7_leaf_libraries_manifest.json`",
    "`scripts\\zigux/check_phase7_leaf_libraries.zig`",
    "duplicate-key match iteration",
};

const REQUIRED_MARKERS__zigux_tests_phase7_leaf_libraries_starter_packet_zig = [_][]const u8{
    "test \"phase7 packet keeps borrowed cmdline parsing aligned with owned argv splitting\" {",
    "test \"phase7 packet keeps string helper replacement and cmdline quoting reviewable\" {",
    "test \"phase7 packet keeps memparse and integer option expansion explicit\" {",
    "test \"phase7 packet keeps cached rbtree ordering stable for parsed values\" {",
    "test \"phase7 packet keeps duplicate mode values queryable across argv split cmdline parsing and rbtree matching\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase7_leaf_libraries_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../../lib/string_helpers.zig\"),",
    ".root_source_file = b.path(\"../../lib/cmdline.zig\"),",
    ".root_source_file = b.path(\"../../lib/argv_split.zig\"),",
    ".root_source_file = b.path(\"../../lib/rbtree.zig\"),",
    "\"phase7-leaf-libraries-starter-packet\"",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase7_leaf_libraries_manifest_json = [_][]const u8{
    "\"slug\": \"phase7-leaf-libraries-starter-packet\"",
    "\"lane\": \"kernel-leaf-libraries\"",
    "\"lib/string_helpers.zig\"",
    "\"lib/cmdline.zig\"",
    "\"lib/argv_split.zig\"",
    "\"lib/rbtree.zig\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-libraries.md");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
    const text_required_markers__documentation_zigux_phase7-leaf-libraries_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-libraries/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-leaf-libraries_md_path);
    const text_required_markers__documentation_zigux_phase7-leaf-libraries_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-leaf-libraries_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-leaf-libraries_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-leaf-libraries_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-leaf-libraries_md, marker);
    const text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7/leaf/libraries/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_leaf_libraries_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7/leaf/libraries/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_leaf_libraries_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_leaf_libraries_starter_packet_build_zig, marker);
    const text_required_markers__zigux_tests_fixtures_phase7_leaf_libraries_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase7/leaf/libraries/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase7_leaf_libraries_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase7_leaf_libraries_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase7_leaf_libraries_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase7_leaf_libraries_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase7_leaf_libraries_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase7_leaf_libraries_manifest_json, marker);
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

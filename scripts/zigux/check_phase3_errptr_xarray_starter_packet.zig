const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ERRPTR_XARRAY_STARTER_PACKET=pass";
pub const self_test_pass_marker = "PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=pass";

const STARTER_BUILD_ROUTE = [_][]const u8{
    "zig build phase3-errptr-xarray-starter-packet-test --build-file zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-errptr-xarray-slice_md = [_][]const u8{
    "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
    "scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "the highest tagged inline boundary still stays below the `err_ptr` floor",
    "It is one helper-local interop proof layered beside the existing `dev_t` starter packet.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-validator-support-surface_md = [_][]const u8{
    "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
    "scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "the manifest-backed starter packet",
};

const REQUIRED_MARKERS__zigux_helpers_err_ptr_zig = [_][]const u8{
    "pub const max_errno: usize = 4095;",
    "pub const err_floor: usize = @bitCast(-@as(isize, @intCast(max_errno)));",
    "pub fn fromErrorCode(code: isize) usize {",
    "pub fn isErrValue(raw: usize) bool {",
    "pub fn toErrorCode(raw: usize) isize {",
    "test \"err_ptr encodes the Linux error band as a tagged pointer-sized value\" {",
    "test \"err_ptr keeps the floor boundary explicit\" {",
    "test \"non-error values stay outside the err_ptr band\" {",
};

const REQUIRED_MARKERS__zigux_helpers_xa_value_zig = [_][]const u8{
    "const err_ptr = @import(\"err_ptr\");",
    "pub const value_tag_mask: usize = 0x1;",
    "pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;",
    "ValueWouldOverlapErrPtr",
    "return (value << 1) | value_tag_mask;",
    "return (raw & value_tag_mask) == value_tag_mask and !err_ptr.isErrValue(raw);",
};

const REQUIRED_MARKERS__zigux_tests_phase3_errptr_xarray_starter_packet_zig = [_][]const u8{
    "test \"err_ptr encodes the Linux error band as a tagged pointer-sized value\" {",
    "test \"xa_value round-trips a bounded inline value without entering the err_ptr band\" {",
    "test \"xa_value rejects inline values that would overlap err_ptr encodings\" {",
    "test \"safe inline limit stays the highest tagged value below the err_ptr floor\" {",
    "try testing.expectEqual(err_ptr.err_floor, raw + 2);",
};

const REQUIRED_MARKERS__zigux_tests_phase3_errptr_xarray_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/err_ptr.zig\"),",
    ".root_source_file = b.path(\"../helpers/xa_value.zig\"),",
    ".root_source_file = b.path(\"phase3_errptr_xarray_starter_packet.zig\"),",
    "xa_value.addImport(\"err_ptr\", err_ptr);",
    "\"phase3-errptr-xarray-starter-packet-test\"",
};

const REQUIRED_MARKERS__zigux_tests_phase3_errptr_xarray_starter_packet_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-errptr-xarray-starter-packet\"",
    "\"status\": \"starter_packet_present\"",
    "\"Documentation/zigux/phase3-errptr-xarray-slice.md\"",
    "\"Documentation/zigux/phase3-validator-support-surface.md\"",
    "\"zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json\"",
    "\"zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig\"",
    "\"repo_reality_gaps\": []",
    "\"next_safe_step\": \"keep the helper-local err_ptr/xarray packet honest with manifest-backed replay before widening into broader Phase 3 validator or export-boundary claims\"",
};

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
};

const SELF_TEST_CASES = [_][]const u8{
    "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
    "the manifest-backed starter packet",
    "pub fn isErrValue(raw: usize) bool {",
    "test \"err_ptr encodes the Linux error band as a tagged pointer-sized value\" {",
    "ValueWouldOverlapErrPtr",
    "try testing.expectEqual(err_ptr.err_floor, raw + 2);",
    "\"phase3-errptr-xarray-starter-packet-test\"",
    "\"status\": \"starter_packet_present\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_starter_build_route_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-errptr-xarray-slice.md");
    defer allocator.free(text_starter_build_route_path);
    const text_starter_build_route = try guard.readUtf8File(io, allocator, text_starter_build_route_path);
    defer allocator.free(text_starter_build_route);
    for (STARTER_BUILD_ROUTE) |marker| try guard.requireMarker(text_starter_build_route, marker);
    const text_required_markers__documentation_zigux_phase3-errptr-xarray-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-errptr-xarray-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-errptr-xarray-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-errptr-xarray-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-errptr-xarray-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-errptr-xarray-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-errptr-xarray-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-errptr-xarray-slice_md, marker);
    const text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-validator-support-surface/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path);
    const text_required_markers__documentation_zigux_phase3-validator-support-surface_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-validator-support-surface_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-validator-support-surface_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-validator-support-surface_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-validator-support-surface_md, marker);
    const text_required_markers__zigux_helpers_err_ptr_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/err/ptr/zig");
    defer allocator.free(text_required_markers__zigux_helpers_err_ptr_zig_path);
    const text_required_markers__zigux_helpers_err_ptr_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_err_ptr_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_err_ptr_zig);
    for (REQUIRED_MARKERS__zigux_helpers_err_ptr_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_err_ptr_zig, marker);
    const text_required_markers__zigux_helpers_xa_value_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/xa/value/zig");
    defer allocator.free(text_required_markers__zigux_helpers_xa_value_zig_path);
    const text_required_markers__zigux_helpers_xa_value_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_xa_value_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_xa_value_zig);
    for (REQUIRED_MARKERS__zigux_helpers_xa_value_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_xa_value_zig, marker);
    const text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/errptr/xarray/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_errptr_xarray_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/errptr/xarray/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_errptr_xarray_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_build_zig, marker);
    const text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/errptr/xarray/starter/packet/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_manifest_json_path);
    const text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase3_errptr_xarray_starter_packet_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_errptr_xarray_starter_packet_manifest_json, marker);
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-errptr-xarray-slice.md");
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

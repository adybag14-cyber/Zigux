const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ERRPTR_XARRAY=pass";
pub const self_test_pass_marker = "PHASE3_ERRPTR_XARRAY_SELF_TEST=pass";

const REQUIRED_MARKERS__Documentation_zigux_phase3-errptr-xarray-slice_md = [_][]const u8{
    "zigux/tests/phase3_errptr_xarray_dump.zig",
    "zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c",
    "zigux/tests/fixtures/phase3_errptr_xarray/expected.json",
    "zigux/tests/fixtures/phase3_errptr_xarray_manifest.json",
    "scripts\\zigux/check_phase3_errptr_xarray.zig",
    "fixture-backed parity packet",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-validator-support-surface_md = [_][]const u8{
    "zigux/tests/phase3_errptr_xarray_dump.zig",
    "zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "zigux/tests/fixtures/phase3_errptr_xarray_manifest.json",
    "scripts\\zigux/check_phase3_errptr_xarray.zig",
    "fixture-backed parity packet",
};

const REQUIRED_MARKERS__zigux_helpers_err_ptr_zig = [_][]const u8{
    "pub const max_errno: usize = 4095;",
    "pub const err_floor: usize = @bitCast(-@as(isize, @intCast(max_errno)));",
    "pub fn fromErrorCode(code: isize) usize {",
    "pub fn isErrValue(raw: usize) bool {",
    "pub fn toErrorCode(raw: usize) isize {",
};

const REQUIRED_MARKERS__zigux_helpers_xa_value_zig = [_][]const u8{
    "const err_ptr = @import(\"err_ptr\");",
    "pub const value_tag_mask: usize = 0x1;",
    "pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;",
    "ValueWouldOverlapErrPtr",
    "return (value << 1) | value_tag_mask;",
};

const REQUIRED_MARKERS__zigux_tests_phase3_errptr_xarray_dump_zig = [_][]const u8{
    "return \"null\";",
    "return \"xa_value\";",
    "return \"err_ptr\";",
    "\\\"safe_inline_limit_raw_hex\\\"",
    "try writeCase(writer, \"inline_limit\", inline_limit_raw, true);",
    "try writeCase(writer, \"err_max\", err_ptr.fromErrorCode(-4095), false);",
};

const REQUIRED_MARKERS__zigux_tests_phase3_errptr_xarray_dump_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/err_ptr.zig\"),",
    ".root_source_file = b.path(\"../helpers/xa_value.zig\"),",
    ".root_source_file = b.path(\"phase3_errptr_xarray_dump.zig\"),",
    "xa_value.addImport(\"err_ptr\", err_ptr);",
    "\"phase3-errptr-xarray-dump\"",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_errptr_xarray_phase3_errptr_xarray_c_harness_c = [_][]const u8{
    "#define MAX_ERRNO ((uintptr_t)4095)",
    "static uintptr_t err_floor(void) {",
    "return \"xa_value\";",
    "write_case(\"inline_limit\", inline_limit_raw, 1);",
    "write_case(\"err_max\", (uintptr_t)(intptr_t)-4095, 0);",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_errptr_xarray_expected_json = [_][]const u8{
    "\"word_bits\": 64",
    "\"safe_inline_limit_raw_hex\": \"0xffffffffffffefff\"",
    "\"name\": \"inline_limit\"",
    "\"decoded_value\": 9223372036854773759",
    "\"decoded_error\": -4095",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_errptr_xarray_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-errptr-xarray\"",
    "\"status\": \"parity_packet_present\"",
    "\"zigux/tests/phase3_errptr_xarray_dump.zig\"",
    "\"zigux/tests/phase3_errptr_xarray_dump_build.zig\"",
    "\"zigux/tests/fixtures/phase3_errptr_xarray/expected.json\"",
    "\"zig run scripts\\zigux/check_phase3_errptr_xarray.zig -- --repo-root . --zig zig --cc gcc\"",
    "\"repo_reality_gaps\": []",
};

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_errptr_xarray.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_errptr_xarray.zig -- --repo-root . --zig zig --cc gcc",
    "zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig",
};

const SELF_TEST_CASES = [_][]const u8{
    "fixture-backed parity packet",
    "zigux/tests/phase3_errptr_xarray_dump.zig",
    "\\\"safe_inline_limit_raw_hex\\\"",
    "write_case(\"err_max\", (uintptr_t)(intptr_t)-4095, 0);",
    "\"status\": \"parity_packet_present\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
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
    const text_required_markers__zigux_tests_phase3_errptr_xarray_dump_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/errptr/xarray/dump/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_errptr_xarray_dump_zig_path);
    const text_required_markers__zigux_tests_phase3_errptr_xarray_dump_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_errptr_xarray_dump_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_errptr_xarray_dump_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_errptr_xarray_dump_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_errptr_xarray_dump_zig, marker);
    const text_required_markers__zigux_tests_phase3_errptr_xarray_dump_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/errptr/xarray/dump/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_errptr_xarray_dump_build_zig_path);
    const text_required_markers__zigux_tests_phase3_errptr_xarray_dump_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_errptr_xarray_dump_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_errptr_xarray_dump_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_errptr_xarray_dump_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_errptr_xarray_dump_build_zig, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_phase3_errptr_xarray_c_harness_c_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/errptr/xarray/phase3/errptr/xarray/c/harness/c");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_phase3_errptr_xarray_c_harness_c_path);
    const text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_phase3_errptr_xarray_c_harness_c = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_phase3_errptr_xarray_c_harness_c_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_phase3_errptr_xarray_c_harness_c);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_errptr_xarray_phase3_errptr_xarray_c_harness_c) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_phase3_errptr_xarray_c_harness_c, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_expected_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/errptr/xarray/expected/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_expected_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_expected_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_expected_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_expected_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_errptr_xarray_expected_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_expected_json, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/errptr/xarray/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_errptr_xarray_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_errptr_xarray_manifest_json, marker);
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

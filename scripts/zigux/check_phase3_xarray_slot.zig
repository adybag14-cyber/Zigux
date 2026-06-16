const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_XARRAY_SLOT=pass";
pub const self_test_pass_marker = "PHASE3_XARRAY_SLOT_SELF_TEST=pass";

const REQUIRED_MARKERS__scripts_zigux_check-phase3-xarray-slot-starter-packet_py = [_][]const u8{
    "PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST=pass",
    "Validate the current Phase 3 xarray slot starter packet.",
};

const REQUIRED_MARKERS__zigux_tests_phase3_xarray_slot_dump_zig = [_][]const u8{
    "const xarray_slot_view = @import(\"xarray_slot_view\");",
    ".pointer => \"pointer_like\",",
    "\\\"is_tagged_internal\\\": {s}",
    "try writeCase(writer, \"inline_zero\", inline_zero_raw, true);",
    "try writeCase(writer, \"inline_limit\", inline_limit_raw, true);",
    "try writeCase(writer, \"err_top\", err_ptr.fromErrorCode(-1), true);",
    "try writeCase(writer, \"err_max\", err_ptr.fromErrorCode(-4095), false);",
};

const REQUIRED_MARKERS__zigux_tests_phase3_xarray_slot_dump_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/xarray_slot_view.zig\"),",
    ".root_source_file = b.path(\"phase3_xarray_slot_dump.zig\"),",
    "xarray_slot_view.addImport(\"err_ptr\", err_ptr);",
    "xarray_slot_view.addImport(\"xa_value\", xa_value);",
    "\"phase3-xarray-slot-dump\"",
};

const REQUIRED_MARKERS__zigux_Makefile = [_][]const u8{
    "phase3-xarray-slot-starter-packet:",
    "phase3-xarray-slot-starter-packet-test:",
    "phase3-xarray-slot-dump:",
    "$(ZIG_REPO_ROOT) build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
    "$(ZIG_REPO_ROOT) build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "$(ZIG_REPO_ROOT) build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_xarray_slot_phase3_xarray_slot_c_harness_c = [_][]const u8{
    "#define MAX_ERRNO ((uintptr_t)4095)",
    "static const char *kind_name(uintptr_t raw) {",
    "return \"pointer_like\";",
    "write_case(\"inline_zero\", make_value(0), 1);",
    "write_case(\"err_top\", (uintptr_t)(intptr_t)-1, 1);",
    "write_case(\"err_max\", (uintptr_t)(intptr_t)-4095, 0);",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_xarray_slot_expected_json = [_][]const u8{
    "\"word_bits\": 64",
    "\"safe_inline_limit_raw_hex\": \"0xffffffffffffefff\"",
    "\"name\": \"inline_zero\"",
    "\"decoded_value\": 0",
    "\"name\": \"err_top\"",
    "\"decoded_error\": -1",
    "\"decoded_error\": -4095",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_xarray_slot_manifest_json = [_][]const u8{
    "\"slug\": \"phase3-xarray-slot\"",
    "\"status\": \"starter_and_dump_packet_present\"",
    "\"zigux/Makefile\"",
    "\"zigux/tests/phase3_xarray_slot_dump.zig\"",
    "\"zigux/tests/phase3_xarray_slot_dump_build.zig\"",
    "\"zigux/tests/fixtures/phase3_xarray_slot/expected.json\"",
    "\"make -C zigux phase3-xarray-slot-starter-packet\"",
    "\"make -C zigux phase3-xarray-slot-starter-packet-test\"",
    "\"make -C zigux phase3-xarray-slot-dump\"",
    "\"zig run scripts\\zigux/check_phase3_xarray_slot.zig --repo-root . --zig zig --cc gcc\"",
};

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig --self-test",
    "zig run scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig --repo-root .",
    "zig run scripts\\zigux/check_phase3_xarray_slot.zig --self-test",
    "zig run scripts\\zigux/check_phase3_xarray_slot.zig --repo-root . --zig zig --cc gcc",
    "zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
    "make -C zigux phase3-xarray-slot-starter-packet",
    "make -C zigux phase3-xarray-slot-starter-packet-test",
    "make -C zigux phase3-xarray-slot-dump",
};

const SELF_TEST_CASES = [_][]const u8{
    "PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST=pass",
    "try writeCase(writer, \"inline_zero\", inline_zero_raw, true);",
    "phase3-xarray-slot-dump:",
    "write_case(\"err_max\", (uintptr_t)(intptr_t)-4095, 0);",
    "\"decoded_error\": -4095",
    "\"status\": \"starter_and_dump_packet_present\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__scripts_zigux_check-phase3-xarray-slot-starter-packet_py_path = try guard.joinPath(allocator, root, "scripts/zigux/check-phase3-xarray-slot-starter-packet/py");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-xarray-slot-starter-packet_py_path);
    const text_required_markers__scripts_zigux_check-phase3-xarray-slot-starter-packet_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase3-xarray-slot-starter-packet_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase3-xarray-slot-starter-packet_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase3-xarray-slot-starter-packet_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase3-xarray-slot-starter-packet_py, marker);
    const text_required_markers__zigux_tests_phase3_xarray_slot_dump_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/xarray/slot/dump/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_xarray_slot_dump_zig_path);
    const text_required_markers__zigux_tests_phase3_xarray_slot_dump_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_xarray_slot_dump_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_xarray_slot_dump_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_xarray_slot_dump_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_xarray_slot_dump_zig, marker);
    const text_required_markers__zigux_tests_phase3_xarray_slot_dump_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/xarray/slot/dump/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_xarray_slot_dump_build_zig_path);
    const text_required_markers__zigux_tests_phase3_xarray_slot_dump_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_xarray_slot_dump_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_xarray_slot_dump_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_xarray_slot_dump_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_xarray_slot_dump_build_zig, marker);
    const text_required_markers__zigux_makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_markers__zigux_makefile_path);
    const text_required_markers__zigux_makefile = try guard.readUtf8File(io, allocator, text_required_markers__zigux_makefile_path);
    defer allocator.free(text_required_markers__zigux_makefile);
    for (REQUIRED_MARKERS__zigux_Makefile) |marker| try guard.requireMarker(text_required_markers__zigux_makefile, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_phase3_xarray_slot_c_harness_c_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/xarray/slot/phase3/xarray/slot/c/harness/c");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_phase3_xarray_slot_c_harness_c_path);
    const text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_phase3_xarray_slot_c_harness_c = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_phase3_xarray_slot_c_harness_c_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_phase3_xarray_slot_c_harness_c);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_xarray_slot_phase3_xarray_slot_c_harness_c) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_phase3_xarray_slot_c_harness_c, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_expected_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/xarray/slot/expected/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_expected_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_expected_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_expected_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_expected_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_xarray_slot_expected_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_expected_json, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/xarray/slot/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_xarray_slot_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_xarray_slot_manifest_json, marker);
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "zigux/helpers/err_ptr.zig");
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

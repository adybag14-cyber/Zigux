const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_BASE64_PACKET=pass";
pub const self_test_pass_marker = "PHASE7_BASE64_PACKET_SELF_TEST=pass";

const EXPECTED_REVIEW_SURFACES = [_][]const u8{
    "Documentation/zigux/phase7-base64-slice.md",
    "scripts\\zigux/check_phase7_base64_packet.zig",
    "lib/base64.zig",
    "zigux/tests/phase7_base64.zig",
    "zigux/tests/phase7_base64_build.zig",
    "zigux/tests/phase7_base64_survey.zig",
    "zigux/tests/phase7_base64_manifest.json",
};

const EXPECTED_COVERED_HELPERS = [_][]const u8{
    "chars",
    "bytesStd",
    "bytesUrlsafe",
    "bytesImap",
    "encodeStd",
    "encodeUrlsafe",
    "encodeImap",
    "decodeStd",
    "decodeUrlsafe",
    "decodeImap",
    "encodeStdSlice",
    "encodeStdAlloc",
    "decodeStdSlice",
    "decodeStdAlloc",
};

const EXPECTED_OWNERSHIP_FOCUS = [_][]const u8{
    "variant-pinned convenience wrappers keep the standard, urlsafe, and IMAP alphabets explicit without widening into shared streaming ownership",
    "short-tail packet checks keep one-byte and two-byte replay cases bounded to foreign-alphabet rejection and exact decoded lengths",
    "slice and allocator companions keep exact-span ownership reviewable for the same bounded standard packet",
    "the helper-local base64 packet stays separate from the broader shared Phase 7 docs-root, tests-root, Makefile, and workflow reminder surfaces",
};

const EXPECTED_NEXT_STEP = [_][]const u8{
    "Keep same-lane follow-through limited to this helper-local base64 packet and only reopen it when a fresh reread finds checker, manifest, replay, build-entrypoint, or slice-note drift inside these returned packet members before widening into any broader Phase 7 shared reminder work.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-base64-slice_md = [_][]const u8{
    "`PHASE7_STATUS=helper_local_slice_note_test_build_survey_manifest_checker_anchor`",
    "`PHASE7_SLICE=base64-runtime-leaf`",
    "`PHASE7_LANE_KEY=P7-L14`",
    "`lib/base64.zig`",
    "`zigux/tests/phase7_base64_build.zig`",
    "urlsafe short tails stay inside the urlsafe alphabet and reject standard `+`-prefixed foreign tails",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase7-base64-packet_py = [_][]const u8{
    "--self-test",
    "PHASE7_BASE64_PACKET_SELF_TEST=pass",
    "PHASE7_BASE64_PACKET=pass",
    "PHASE7_BASE64_PACKET=fail",
    "MISSING_PHASE7_BASE64_FILES_START",
    "MISSING_PHASE7_BASE64_FILES_END",
    "MISSING_PHASE7_BASE64_MARKERS_START",
    "MISSING_PHASE7_BASE64_MARKERS_END",
    "MISMATCHED_PHASE7_BASE64_MANIFEST_START",
    "MISMATCHED_PHASE7_BASE64_MANIFEST_END",
    "\"lane_key\": \"P7-L14\"",
    "\"anchor\": \"lib/base64.c\"",
};

const REQUIRED_MARKERS__lib_base64_zig = [_][]const u8{
    "pub const Variant = enum {",
    "pub fn bytesStd(src: []const u8, padding: bool) DecodeError!usize {",
    "pub fn encodeStd(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {",
    "pub fn decodeStd(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {",
    "pub fn encodeUrlsafe(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {",
    "pub fn decodeUrlsafe(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {",
    "pub fn encodeImap(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {",
    "pub fn decodeImap(dst: []u8, src: []const u8, padding: bool) DecodeError!usize {",
    "test \"variant-pinned convenience helpers mirror the generic api\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase7_base64_zig = [_][]const u8{
    "const base64 = @import(\"base64\");",
    "test \"phase 7 base64 companion replays standard padded convenience wrappers\" {",
    "test \"phase 7 base64 companion replays urlsafe short-tail wrappers without crossing into standard tails\" {",
    "test \"phase 7 base64 companion replays IMAP short-tail wrappers without slash-backed standard tails\" {",
    "test \"phase 7 base64 companion replays exact-span slice and allocator companions\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase7_base64_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../../lib/base64.zig\"),",
    ".root_source_file = b.path(\"phase7_base64.zig\"),",
    "root_module.addImport(\"base64\", base64_module);",
    "\"phase7-base64-test\"",
};

const REQUIRED_MARKERS__zigux_tests_phase7_base64_survey_zig = [_][]const u8{
    "test \"phase 7 base64 survey keeps the returned helper-local packet truthful\" {",
    "try std.testing.expectEqualStrings(\"P7-L14\", manifest.lane_key);",
    "try expectContains(checker, \"PHASE7_BASE64_PACKET=pass\");",
    "try expectContains(helper, \"pub fn encodeStd(dst: []u8, src: []const u8, padding: bool) EncodeError!usize {\");",
    "try expectContains(helper_companion, \"phase 7 base64 companion replays exact-span slice and allocator companions\");",
    "try expectContains(build_file, \"\\\"phase7-base64-test\\\"\");",
};

const REQUIRED_MARKERS__zigux_tests_phase7_base64_manifest_json = [_][]const u8{
    "\"lane_key\": \"P7-L14\"",
    "\"phase\": \"Phase 7\"",
    "\"anchor\": \"lib/base64.c\"",
    "\"current_master_state\": \"helper_slice_test_build_survey_manifest_checker_anchor\"",
    "\"Documentation/zigux/phase7-base64-slice.md\"",
    "\"zigux/tests/phase7_base64_build.zig\"",
    "\"encodeStd\"",
    "\"decodeStdAlloc\"",
    "\"the helper-local base64 packet stays separate from the broader shared Phase 7 docs-root, tests-root, Makefile, and workflow reminder surfaces\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_review_surfaces_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_review_surfaces_path);
    const text_expected_review_surfaces = try guard.readUtf8File(io, allocator, text_expected_review_surfaces_path);
    defer allocator.free(text_expected_review_surfaces);
    for (EXPECTED_REVIEW_SURFACES) |marker| try guard.requireMarker(text_expected_review_surfaces, marker);
    const text_expected_covered_helpers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_covered_helpers_path);
    const text_expected_covered_helpers = try guard.readUtf8File(io, allocator, text_expected_covered_helpers_path);
    defer allocator.free(text_expected_covered_helpers);
    for (EXPECTED_COVERED_HELPERS) |marker| try guard.requireMarker(text_expected_covered_helpers, marker);
    const text_expected_ownership_focus_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_ownership_focus_path);
    const text_expected_ownership_focus = try guard.readUtf8File(io, allocator, text_expected_ownership_focus_path);
    defer allocator.free(text_expected_ownership_focus);
    for (EXPECTED_OWNERSHIP_FOCUS) |marker| try guard.requireMarker(text_expected_ownership_focus, marker);
    const text_expected_next_step_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_next_step_path);
    const text_expected_next_step = try guard.readUtf8File(io, allocator, text_expected_next_step_path);
    defer allocator.free(text_expected_next_step);
    for (EXPECTED_NEXT_STEP) |marker| try guard.requireMarker(text_expected_next_step, marker);
    const text_required_markers__documentation_zigux_phase7-base64-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-base64-slice.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-base64-slice_md_path);
    const text_required_markers__documentation_zigux_phase7-base64-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-base64-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-base64-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-base64-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-base64-slice_md, marker);
    const text_required_markers__scripts_zigux_check-phase7-base64-packet_py_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase7_base64_packet.zig");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-base64-packet_py_path);
    const text_required_markers__scripts_zigux_check-phase7-base64-packet_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase7-base64-packet_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-base64-packet_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase7-base64-packet_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase7-base64-packet_py, marker);
    const text_required_markers__lib_base64_zig_path = try guard.joinPath(allocator, root, "lib/base64.zig");
    defer allocator.free(text_required_markers__lib_base64_zig_path);
    const text_required_markers__lib_base64_zig = try guard.readUtf8File(io, allocator, text_required_markers__lib_base64_zig_path);
    defer allocator.free(text_required_markers__lib_base64_zig);
    for (REQUIRED_MARKERS__lib_base64_zig) |marker| try guard.requireMarker(text_required_markers__lib_base64_zig, marker);
    const text_required_markers__zigux_tests_phase7_base64_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_base64.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_base64_zig_path);
    const text_required_markers__zigux_tests_phase7_base64_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_base64_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_base64_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_base64_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_base64_zig, marker);
    const text_required_markers__zigux_tests_phase7_base64_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_base64_build.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_base64_build_zig_path);
    const text_required_markers__zigux_tests_phase7_base64_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_base64_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_base64_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_base64_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_base64_build_zig, marker);
    const text_required_markers__zigux_tests_phase7_base64_survey_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_base64_survey.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_base64_survey_zig_path);
    const text_required_markers__zigux_tests_phase7_base64_survey_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_base64_survey_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_base64_survey_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_base64_survey_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_base64_survey_zig, marker);
    const text_required_markers__zigux_tests_phase7_base64_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_base64_manifest.json");
    defer allocator.free(text_required_markers__zigux_tests_phase7_base64_manifest_json_path);
    const text_required_markers__zigux_tests_phase7_base64_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_base64_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_base64_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase7_base64_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_base64_manifest_json, marker);
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

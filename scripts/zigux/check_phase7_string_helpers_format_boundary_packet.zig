const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=pass";
pub const self_test_pass_marker = "PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=pass";

const FOLLOW_ON_MARKER = [_][]const u8{
    "Keep the dedicated checkers, survey, sample-boundary, and format-boundary replays fail-closed on the still-parked `parse_int_array_user()` and `devm_kasprintf_strarray()` follow-ons",
};

const FORMAT_BOUNDARY_FOCUS = [_][]const u8{
    "dedicated format-boundary replay for the trace-events formatting companion and broad-format exclusion",
};

const FORMAT_BOUNDARY_SENTENCE = [_][]const u8{
    "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.",
};

const SLICE_BOUNDARY_REPLAY_MARKER = [_][]const u8{
    "The dedicated sample-boundary and format-boundary replays should keep that distinction explicit while the expanded starter packet advances through helper-local review surfaces only.",
};

const REQUIRED_MARKERS__Documentation_zigux_phase7-string-helpers-slice_md = [_][]const u8{
    "`zigux/tests/phase7_string_helpers_format_boundary.zig`",
    "`scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig`",
};

const REQUIRED_MARKERS__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py = [_][]const u8{
    "--self-test",
    "PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=pass",
    "print(\"PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=pass\")",
    "print(\"PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=fail\")",
    "\"zigux/tests/phase7_string_helpers_format_boundary.zig\",",
    "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_FILES_START",
    "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_FILES_END",
    "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_MARKERS_START",
    "MISSING_PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_MARKERS_END",
};

const REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_format_boundary_zig = [_][]const u8{
    "test \"phase 7 string helper format boundary keeps the trace-events formatting companion as the only sample-root exception\" {",
    "test \"phase 7 string helper format boundary stays on sample-boundary review surfaces only\" {",
    "* `*printf*`",
    "* `*vsprintf*`",
};

const REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_survey_zig = [_][]const u8{
    "const format_boundary_checker = try readRepoFile(allocator, \"scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig\");",
    "try expectContains(format_boundary_checker, \"PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=pass\");",
    "const format_boundary = try readRepoFile(allocator, \"zigux/tests/phase7_string_helpers_format_boundary.zig\");",
    "try expectContains(format_boundary, \"phase 7 string helper format boundary keeps the trace-events formatting companion as the only sample-root exception\");",
    "try expectContains(format_boundary, \"Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.\");",
};

const REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_manifest_json = [_][]const u8{
    "\"scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig\"",
    "\"zigux/tests/phase7_string_helpers_format_boundary.zig\"",
};

const REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_sample_boundary_zig = [_][]const u8{
    "* `*printf*`",
    "* `*vsprintf*`",
};

const REQUIRED_MARKERS__samples_zigux_README_md = [_][]const u8{
    "Current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`",
    "* `*printf*`",
    "* `*vsprintf*`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_follow_on_marker_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_follow_on_marker_path);
    const text_follow_on_marker = try guard.readUtf8File(io, allocator, text_follow_on_marker_path);
    defer allocator.free(text_follow_on_marker);
    for (FOLLOW_ON_MARKER) |marker| try guard.requireMarker(text_follow_on_marker, marker);
    const text_format_boundary_focus_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_format_boundary_focus_path);
    const text_format_boundary_focus = try guard.readUtf8File(io, allocator, text_format_boundary_focus_path);
    defer allocator.free(text_format_boundary_focus);
    for (FORMAT_BOUNDARY_FOCUS) |marker| try guard.requireMarker(text_format_boundary_focus, marker);
    const text_format_boundary_sentence_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_format_boundary_sentence_path);
    const text_format_boundary_sentence = try guard.readUtf8File(io, allocator, text_format_boundary_sentence_path);
    defer allocator.free(text_format_boundary_sentence);
    for (FORMAT_BOUNDARY_SENTENCE) |marker| try guard.requireMarker(text_format_boundary_sentence, marker);
    const text_slice_boundary_replay_marker_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_slice_boundary_replay_marker_path);
    const text_slice_boundary_replay_marker = try guard.readUtf8File(io, allocator, text_slice_boundary_replay_marker_path);
    defer allocator.free(text_slice_boundary_replay_marker);
    for (SLICE_BOUNDARY_REPLAY_MARKER) |marker| try guard.requireMarker(text_slice_boundary_replay_marker, marker);
    const text_required_markers__documentation_zigux_phase7-string-helpers-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-string-helpers-slice.md");
    defer allocator.free(text_required_markers__documentation_zigux_phase7-string-helpers-slice_md_path);
    const text_required_markers__documentation_zigux_phase7-string-helpers-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase7-string-helpers-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase7-string-helpers-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase7-string-helpers-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase7-string-helpers-slice_md, marker);
    const text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase7_string_helpers_format_boundary_packet.zig");
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py_path);
    const text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py);
    for (REQUIRED_MARKERS__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_check-phase7-string-helpers-format-boundary-packet_py, marker);
    const text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_string_helpers_format_boundary.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig_path);
    const text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_format_boundary_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_string_helpers_format_boundary_zig, marker);
    const text_required_markers__zigux_tests_phase7_string_helpers_survey_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_string_helpers_survey.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_survey_zig_path);
    const text_required_markers__zigux_tests_phase7_string_helpers_survey_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_string_helpers_survey_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_survey_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_survey_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_string_helpers_survey_zig, marker);
    const text_required_markers__zigux_tests_phase7_string_helpers_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_manifest_json_path);
    const text_required_markers__zigux_tests_phase7_string_helpers_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_string_helpers_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_string_helpers_manifest_json, marker);
    const text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase7_string_helpers_sample_boundary.zig");
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig_path);
    const text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase7_string_helpers_sample_boundary_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase7_string_helpers_sample_boundary_zig, marker);
    const text_required_markers__samples_zigux_readme_md_path = try guard.joinPath(allocator, root, "samples/zigux/README.md");
    defer allocator.free(text_required_markers__samples_zigux_readme_md_path);
    const text_required_markers__samples_zigux_readme_md = try guard.readUtf8File(io, allocator, text_required_markers__samples_zigux_readme_md_path);
    defer allocator.free(text_required_markers__samples_zigux_readme_md);
    for (REQUIRED_MARKERS__samples_zigux_README_md) |marker| try guard.requireMarker(text_required_markers__samples_zigux_readme_md, marker);
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

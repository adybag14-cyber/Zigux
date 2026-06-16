const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_TRACE_EVENTS_STRING_CYCLE_SURFACE=pass";
pub const self_test_pass_marker = "PHASE5_TRACE_EVENTS_STRING_CYCLE_SURFACE_SELF_TEST=pass";

const STRING_CYCLE = [_][]const u8{
    "Mother Goose",
    "Snoopy",
    "Gandalf",
    "Frodo",
    "One ring to rule them all",
};

const SURVEY_REQUIRED_TEXT = [_][]const u8{
    "`runStringFormattingCycleReplay()` still keeps the full modulo-selected string cycle explicit across counts `0` through `4`",
    "`iter=%d`",
    "selected-string plus `iter=%d` replay",
};

const MANIFEST_REQUIRED_TEXT = [_][]const u8{
    "`runStringFormattingCycleReplay()` summary still keep the array payload, the full modulo-selected string cycle, selected-string slot cues, and iter-format messages reviewable",
};

const FOCUSED_TEST_REQUIRED_TEXT = [_][]const u8{
    "test \"phase 5 trace-events sample keeps the full string and formatting cycle explicit\"",
    "runStringFormattingCycleReplay()",
    "review_contract.modulo_selected_strings.len",
    "\"iter={d}\"",
};

const SAMPLE_REQUIRED_TEXT = [_][]const u8{
    "pub fn runStringFormattingCycleReplay(self: *Self) !StringFormattingCycleSummary",
    ".modulo_selected_strings = &random_strings",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_string_cycle_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-trace-events-sample-survey.md");
    defer allocator.free(text_string_cycle_path);
    const text_string_cycle = try guard.readUtf8File(io, allocator, text_string_cycle_path);
    defer allocator.free(text_string_cycle);
    for (STRING_CYCLE) |marker| try guard.requireMarker(text_string_cycle, marker);
    const text_survey_required_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-trace-events-sample-survey.md");
    defer allocator.free(text_survey_required_text_path);
    const text_survey_required_text = try guard.readUtf8File(io, allocator, text_survey_required_text_path);
    defer allocator.free(text_survey_required_text);
    for (SURVEY_REQUIRED_TEXT) |marker| try guard.requireMarker(text_survey_required_text, marker);
    const text_manifest_required_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-trace-events-sample-survey.md");
    defer allocator.free(text_manifest_required_text_path);
    const text_manifest_required_text = try guard.readUtf8File(io, allocator, text_manifest_required_text_path);
    defer allocator.free(text_manifest_required_text);
    for (MANIFEST_REQUIRED_TEXT) |marker| try guard.requireMarker(text_manifest_required_text, marker);
    const text_focused_test_required_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-trace-events-sample-survey.md");
    defer allocator.free(text_focused_test_required_text_path);
    const text_focused_test_required_text = try guard.readUtf8File(io, allocator, text_focused_test_required_text_path);
    defer allocator.free(text_focused_test_required_text);
    for (FOCUSED_TEST_REQUIRED_TEXT) |marker| try guard.requireMarker(text_focused_test_required_text, marker);
    const text_sample_required_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-trace-events-sample-survey.md");
    defer allocator.free(text_sample_required_text_path);
    const text_sample_required_text = try guard.readUtf8File(io, allocator, text_sample_required_text_path);
    defer allocator.free(text_sample_required_text);
    for (SAMPLE_REQUIRED_TEXT) |marker| try guard.requireMarker(text_sample_required_text, marker);
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

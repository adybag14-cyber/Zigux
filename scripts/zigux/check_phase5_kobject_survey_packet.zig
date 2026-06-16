const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_KOBJECT_SURVEY_PACKET=pass";
pub const self_test_pass_marker = "PHASE5_KOBJECT_SURVEY_PACKET_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "`samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` together keep the bounded `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, NULL-terminated attribute-list slot, and shared build-route linkage explicit rather than turning that companion into a fifth Phase 5 sample",
    "`zig test samples/zigux/kobject_example.zig` stays the sample-owned self-check for the ownership-and-lifetime packet",
    "`zig test --dep kobject_example_sample -Mroot=zigux/tests/phase5_kobject_example.zig -Mkobject_example_sample=samples/zigux/kobject_example.zig` stays the focused replay route for the same packet",
    "`zig test zigux/tests/phase5_kobject_example_survey.zig` stays the survey-packet guard for the sample-owned replay, the public-tree-backed manifest-and-survey split, and the shared build-route companion in this runtime",
    "`zig test samples/zigux/kobject_example_attr_group_contract.zig` stays the sample-owned self-check for the bounded attr-group companion",
    "`zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` stays the focused replay route for the same attr-group packet",
    "`zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` stays the survey-guard route that checks the companion, focused replay, and shared build-route markers together",
    "does the note still treat `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` as current public-tree-backed companions instead of direct readback proof in this runtime?",
    "- sysfs file creation parity",
    "- `kernel_kobj` integration",
    "- uevent delivery",
    "- loadable module registration",
};

const COMPANION_MARKERS = [_][]const u8{
    "pub const linux_anchor = \"samples/kobject/kobject-example.c\";",
    "pub const directory_name = \"kobject_example\";",
    ".{ .name = \"foo\", .mode = 0o664, .uses_shared_b_handlers = false }",
    ".{ .name = \"baz\", .mode = 0o664, .uses_shared_b_handlers = true }",
    ".{ .name = \"bar\", .mode = 0o664, .uses_shared_b_handlers = true }",
    ".attr_slots_including_null_terminator = specs.len + 1",
    ".group_is_named = false",
};

const REPLAY_MARKERS = [_][]const u8{
    "const companion = @import(\"kobject_attr_group_contract\");",
    "phase 5 kobject attr-group companion keeps the anchor-local contract reviewable through a focused test surface",
    "phase 5 kobject attr-group companion keeps the foo/baz/bar ownership-facing shape explicit",
    "const expected_names = [_][]const u8{ \"foo\", \"baz\", \"bar\" };",
    "contract.all_modes_match_reference",
    "contract.shared_b_handler_pair_consistent",
};

const SURVEY_GUARD_MARKERS = [_][]const u8{
    "readFileAlloc(",
    "\"samples/zigux/kobject_example_attr_group_contract.zig\"",
    "\"zigux/tests/phase5_kobject_attr_group_contract.zig\"",
    "\"zigux/tests/phase5_build.zig\"",
    "\"phase5-kobject-attr-group-contract-survey-tests\"",
    "test_step.dependOn(&run_phase5_kobject_attr_group_contract_tests.step);",
    "test_step.dependOn(&run_phase5_kobject_attr_group_contract_survey_tests.step);",
};

const BUILD_MARKERS = [_][]const u8{
    "\"../../samples/zigux/kobject_example_attr_group_contract.zig\"",
    "\"phase5_kobject_attr_group_contract.zig\"",
    "\"phase5_kobject_attr_group_contract_survey.zig\"",
    "\"phase5-kobject-attr-group-contract-tests\"",
    "\"phase5-kobject-attr-group-contract-survey-tests\"",
    "\"phase5-kobject-attr-group-contract\"",
    "\"phase5-kobject-attr-group-contract-survey\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_survey_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kobject-sample-survey.md");
    defer allocator.free(text_survey_markers_path);
    const text_survey_markers = try guard.readUtf8File(io, allocator, text_survey_markers_path);
    defer allocator.free(text_survey_markers);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text_survey_markers, marker);
    const text_companion_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kobject-sample-survey.md");
    defer allocator.free(text_companion_markers_path);
    const text_companion_markers = try guard.readUtf8File(io, allocator, text_companion_markers_path);
    defer allocator.free(text_companion_markers);
    for (COMPANION_MARKERS) |marker| try guard.requireMarker(text_companion_markers, marker);
    const text_replay_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kobject-sample-survey.md");
    defer allocator.free(text_replay_markers_path);
    const text_replay_markers = try guard.readUtf8File(io, allocator, text_replay_markers_path);
    defer allocator.free(text_replay_markers);
    for (REPLAY_MARKERS) |marker| try guard.requireMarker(text_replay_markers, marker);
    const text_survey_guard_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kobject-sample-survey.md");
    defer allocator.free(text_survey_guard_markers_path);
    const text_survey_guard_markers = try guard.readUtf8File(io, allocator, text_survey_guard_markers_path);
    defer allocator.free(text_survey_guard_markers);
    for (SURVEY_GUARD_MARKERS) |marker| try guard.requireMarker(text_survey_guard_markers, marker);
    const text_build_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kobject-sample-survey.md");
    defer allocator.free(text_build_markers_path);
    const text_build_markers = try guard.readUtf8File(io, allocator, text_build_markers_path);
    defer allocator.free(text_build_markers);
    for (BUILD_MARKERS) |marker| try guard.requireMarker(text_build_markers, marker);
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

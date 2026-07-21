const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_GENKSYMS_ACTION_PATH=pass";
pub const self_test_pass_marker = "PHASE2_GENKSYMS_ACTION_PATH_SELF_TEST=pass";

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_genksyms_bridge.zig -- --self-test",
    "run: zig run scripts\\zigux/check_genksyms_bridge.zig",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: zig run scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig",
    "run: make -C zigux phase2-genksyms",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "phase2-genksyms: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig -- --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_genksyms_selftest_alignment.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_genksyms_selftest_alignment.zig",
};

const REQUIRED_DOCS_README_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-genksyms`",
};

const REQUIRED_SURVEY_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`zig test scripts/zigux/genksyms.zig`",
    "`zigux/Makefile`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`make -C zigux phase2-genksyms`",
};

const REQUIRED_CLOSURE_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`zig test scripts/zigux/genksyms.zig`",
    "`make -C zigux phase2-genksyms`",
};

const REQUIRED_REVIEW_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`make -C zigux phase2-genksyms`",
};

const REQUIRED_SCRIPTS_README_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`make -C zigux phase2-genksyms`",
};

const REQUIRED_TESTS_README_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_genksyms_bridge.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`make -C zigux phase2-genksyms`",
};

const EXPECTED_CHECKERS = [_][]const u8{
    "scripts\\zigux/check_genksyms_bridge.zig",
    "scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig",
};

const EXPECTED_BRIDGE_HELPERS = [_][]const u8{
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
};

const EXPECTED_MAKE_WRAPPERS = [_][]const u8{
    "make -C zigux phase2-genksyms",
};

const EXPECTED_FIXTURE_ROSTER = [_][]const u8{
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_workflow_lines_path);
    const text_required_workflow_lines = try guard.readUtf8File(io, allocator, text_required_workflow_lines_path);
    defer allocator.free(text_required_workflow_lines);
    for (REQUIRED_WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_required_workflow_lines, marker, 1);
    const text_required_makefile_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_makefile_lines_path);
    const text_required_makefile_lines = try guard.readUtf8File(io, allocator, text_required_makefile_lines_path);
    defer allocator.free(text_required_makefile_lines);
    for (REQUIRED_MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_required_makefile_lines, marker, 1);
    const text_required_docs_readme_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_docs_readme_markers_path);
    const text_required_docs_readme_markers = try guard.readUtf8File(io, allocator, text_required_docs_readme_markers_path);
    defer allocator.free(text_required_docs_readme_markers);
    for (REQUIRED_DOCS_README_MARKERS) |marker| try guard.requireMarker(text_required_docs_readme_markers, marker);
    const text_required_survey_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_survey_markers_path);
    const text_required_survey_markers = try guard.readUtf8File(io, allocator, text_required_survey_markers_path);
    defer allocator.free(text_required_survey_markers);
    for (REQUIRED_SURVEY_MARKERS) |marker| try guard.requireMarker(text_required_survey_markers, marker);
    const text_required_closure_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_closure_markers_path);
    const text_required_closure_markers = try guard.readUtf8File(io, allocator, text_required_closure_markers_path);
    defer allocator.free(text_required_closure_markers);
    for (REQUIRED_CLOSURE_MARKERS) |marker| try guard.requireMarker(text_required_closure_markers, marker);
    const text_required_review_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_review_markers_path);
    const text_required_review_markers = try guard.readUtf8File(io, allocator, text_required_review_markers_path);
    defer allocator.free(text_required_review_markers);
    for (REQUIRED_REVIEW_MARKERS) |marker| try guard.requireMarker(text_required_review_markers, marker);
    const text_required_scripts_readme_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_scripts_readme_markers_path);
    const text_required_scripts_readme_markers = try guard.readUtf8File(io, allocator, text_required_scripts_readme_markers_path);
    defer allocator.free(text_required_scripts_readme_markers);
    for (REQUIRED_SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text_required_scripts_readme_markers, marker);
    const text_required_tests_readme_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_tests_readme_markers_path);
    const text_required_tests_readme_markers = try guard.readUtf8File(io, allocator, text_required_tests_readme_markers_path);
    defer allocator.free(text_required_tests_readme_markers);
    for (REQUIRED_TESTS_README_MARKERS) |marker| try guard.requireMarker(text_required_tests_readme_markers, marker);
    const text_expected_checkers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_checkers_path);
    const text_expected_checkers = try guard.readUtf8File(io, allocator, text_expected_checkers_path);
    defer allocator.free(text_expected_checkers);
    for (EXPECTED_CHECKERS) |marker| try guard.requireMarker(text_expected_checkers, marker);
    const text_expected_bridge_helpers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_bridge_helpers_path);
    const text_expected_bridge_helpers = try guard.readUtf8File(io, allocator, text_expected_bridge_helpers_path);
    defer allocator.free(text_expected_bridge_helpers);
    for (EXPECTED_BRIDGE_HELPERS) |marker| try guard.requireMarker(text_expected_bridge_helpers, marker);
    const text_expected_make_wrappers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_make_wrappers_path);
    const text_expected_make_wrappers = try guard.readUtf8File(io, allocator, text_expected_make_wrappers_path);
    defer allocator.free(text_expected_make_wrappers);
    for (EXPECTED_MAKE_WRAPPERS) |marker| try guard.requireMarker(text_expected_make_wrappers, marker);
    const text_expected_fixture_roster_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_fixture_roster_path);
    const text_expected_fixture_roster = try guard.readUtf8File(io, allocator, text_expected_fixture_roster_path);
    defer allocator.free(text_expected_fixture_roster);
    for (EXPECTED_FIXTURE_ROSTER) |marker| try guard.requireMarker(text_expected_fixture_roster, marker);
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

const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_CLOSURE_VALIDATOR_ACTION_PATH=pass";
pub const self_test_pass_marker = "PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_SELF_TEST=pass";

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: make -C zigux phase2-validate",
    "run: zig run scripts\\zigux/validate_phase2.zig",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tests_readme_alignment.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tool_manifest.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/validate_phase2_closure.zig",
    "phase2: phase2-validate",
};

const REQUIRED_DOCS_README_MARKERS = [_][]const u8{
    "`scripts\\zigux/validate_phase2.zig`",
    "`scripts\\zigux/validate_phase2_closure.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
};

const REQUIRED_BOOTSTRAP_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts\\zigux/validate_phase2.zig`",
    "`scripts\\zigux/validate_phase2_closure.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
};

const REQUIRED_CLOSURE_MARKERS = [_][]const u8{
    "`scripts\\zigux/validate_phase2.zig`",
    "`scripts\\zigux/validate_phase2_closure.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "PHASE2_CLOSURE_VALIDATORS=",
};

const REQUIRED_REVIEW_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts\\zigux/validate_phase2.zig`",
    "`scripts\\zigux/validate_phase2_closure.zig`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
};

const REQUIRED_SCRIPTS_README_MARKERS = [_][]const u8{
    "`scripts\\zigux/validate_phase2.zig`",
    "`scripts\\zigux/validate_phase2_closure.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
};

const REQUIRED_TESTS_README_MARKERS = [_][]const u8{
    "`scripts\\zigux/validate_phase2.zig`",
    "`scripts\\zigux/validate_phase2_closure.zig`",
    "`scripts\\zigux/check_phase2_tool_manifest.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
};

const EXPECTED_VALIDATORS = [_][]const u8{
    "scripts\\zigux/validate_phase2.zig",
    "scripts\\zigux/validate_phase2_closure.zig",
};

const EXPECTED_MAKE_WRAPPERS = [_][]const u8{
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

const EXPECTED_REVIEW_SURFACES = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
};

const REQUIRED_PHASE2_PHONY_TARGETS = [_][]const u8{
    "phase2-validate",
    "phase2",
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
    const text_required_bootstrap_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_bootstrap_markers_path);
    const text_required_bootstrap_markers = try guard.readUtf8File(io, allocator, text_required_bootstrap_markers_path);
    defer allocator.free(text_required_bootstrap_markers);
    for (REQUIRED_BOOTSTRAP_MARKERS) |marker| try guard.requireMarker(text_required_bootstrap_markers, marker);
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
    const text_expected_validators_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_validators_path);
    const text_expected_validators = try guard.readUtf8File(io, allocator, text_expected_validators_path);
    defer allocator.free(text_expected_validators);
    for (EXPECTED_VALIDATORS) |marker| try guard.requireMarker(text_expected_validators, marker);
    const text_expected_make_wrappers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_make_wrappers_path);
    const text_expected_make_wrappers = try guard.readUtf8File(io, allocator, text_expected_make_wrappers_path);
    defer allocator.free(text_expected_make_wrappers);
    for (EXPECTED_MAKE_WRAPPERS) |marker| try guard.requireMarker(text_expected_make_wrappers, marker);
    const text_expected_review_surfaces_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_review_surfaces_path);
    const text_expected_review_surfaces = try guard.readUtf8File(io, allocator, text_expected_review_surfaces_path);
    defer allocator.free(text_expected_review_surfaces);
    for (EXPECTED_REVIEW_SURFACES) |marker| try guard.requireMarker(text_expected_review_surfaces, marker);
    const text_required_phase2_phony_targets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_phase2_phony_targets_path);
    const text_required_phase2_phony_targets = try guard.readUtf8File(io, allocator, text_required_phase2_phony_targets_path);
    defer allocator.free(text_required_phase2_phony_targets);
    for (REQUIRED_PHASE2_PHONY_TARGETS) |marker| try guard.requireMarker(text_required_phase2_phony_targets, marker);
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

const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_TOOLS_PACKET=pass";
pub const self_test_pass_marker = "PHASE2_TOOLS_PACKET_SELF_TEST=pass";

const WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig",
    "run: zig run scripts\\zigux/check_phase2_required_make_routes.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_required_make_routes.zig",
    "run: zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig",
    "run: zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig -- --self-test",
    "run: zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig",
    "run: make -C zigux phase2-tools",
};

const MAKEFILE_LINES = [_][]const u8{
    "phase2-tools:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kbuild_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_docs_shared_reminder.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_required_make_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_artifact_tools_manifest.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
};

const DOCS_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase2_kbuild_routes.zig`",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`",
    "`scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`make -C zigux phase2-tools`",
};

const BOOTSTRAP_MARKERS = [_][]const u8{
    "`zig run scripts\\zigux/check_phase2_kbuild_routes.zig -- --self-test`",
    "`zig run scripts\\zigux/check_phase2_kbuild_routes.zig`",
    "`zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig -- --self-test`",
    "`zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig`",
    "`zig run scripts\\zigux/check_phase2_required_make_routes.zig -- --self-test`",
    "`zig run scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig -- --self-test`",
    "`zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`make -C zigux phase2-tools`",
};

const REVIEW_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase2_kbuild_routes.zig`",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`",
    "`scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`make -C zigux phase2-tools`",
};

const SCRIPTS_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase2_kbuild_routes.zig`",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`",
    "`scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`make -C zigux phase2-tools`",
};

const TESTS_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase2_kbuild_routes.zig`",
    "`scripts\\zigux/check_phase2_docs_shared_reminder.zig`",
    "`scripts\\zigux/check_phase2_required_make_routes.zig`",
    "`scripts\\zigux/check_phase2_artifact_tools_manifest.zig`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`make -C zigux phase2-tools`",
};

const TEXT_SURFACES = [_][]const u8{
    "DOCS_README",
    "BOOTSTRAP_NOTES",
    "REVIEW_CHECKLIST",
    "SCRIPTS_README",
    "TESTS_README",
};

const SURFACE_PATHS = [_][]const u8{
    "ROOT/scripts\\zigux/check_phase2_kbuild_routes.zig",
    "ROOT/scripts\\zigux/check_phase2_docs_shared_reminder.zig",
    "ROOT/scripts\\zigux/check_phase2_required_make_routes.zig",
    "ROOT/scripts\\zigux/check_phase2_artifact_tools_manifest.zig",
    "ROOT/zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_lines_path);
    const text_workflow_lines = try guard.readUtf8File(io, allocator, text_workflow_lines_path);
    defer allocator.free(text_workflow_lines);
    for (WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_workflow_lines, marker, 1);
    const text_makefile_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_lines_path);
    const text_makefile_lines = try guard.readUtf8File(io, allocator, text_makefile_lines_path);
    defer allocator.free(text_makefile_lines);
    for (MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_makefile_lines, marker, 1);
    const text_docs_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_docs_markers_path);
    const text_docs_markers = try guard.readUtf8File(io, allocator, text_docs_markers_path);
    defer allocator.free(text_docs_markers);
    for (DOCS_MARKERS) |marker| try guard.requireMarker(text_docs_markers, marker);
    const text_bootstrap_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bootstrap_markers_path);
    const text_bootstrap_markers = try guard.readUtf8File(io, allocator, text_bootstrap_markers_path);
    defer allocator.free(text_bootstrap_markers);
    for (BOOTSTRAP_MARKERS) |marker| try guard.requireMarker(text_bootstrap_markers, marker);
    const text_review_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_review_markers_path);
    const text_review_markers = try guard.readUtf8File(io, allocator, text_review_markers_path);
    defer allocator.free(text_review_markers);
    for (REVIEW_MARKERS) |marker| try guard.requireMarker(text_review_markers, marker);
    const text_scripts_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_scripts_markers_path);
    const text_scripts_markers = try guard.readUtf8File(io, allocator, text_scripts_markers_path);
    defer allocator.free(text_scripts_markers);
    for (SCRIPTS_MARKERS) |marker| try guard.requireMarker(text_scripts_markers, marker);
    const text_tests_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_tests_markers_path);
    const text_tests_markers = try guard.readUtf8File(io, allocator, text_tests_markers_path);
    defer allocator.free(text_tests_markers);
    for (TESTS_MARKERS) |marker| try guard.requireMarker(text_tests_markers, marker);
    const text_text_surfaces_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_text_surfaces_path);
    const text_text_surfaces = try guard.readUtf8File(io, allocator, text_text_surfaces_path);
    defer allocator.free(text_text_surfaces);
    for (TEXT_SURFACES) |marker| try guard.requireMarker(text_text_surfaces, marker);
    for (SURFACE_PATHS) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) return guard.GuardError.IOError;
    }
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

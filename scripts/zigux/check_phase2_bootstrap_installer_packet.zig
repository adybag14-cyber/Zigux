const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_BOOTSTRAP_INSTALLER_PACKET=pass";
pub const self_test_pass_marker = "PHASE2_BOOTSTRAP_INSTALLER_PACKET_SELF_TEST=pass";

const NOTES_MARKERS = [_][]const u8{
    "`scripts/zigux/install_zig.zig` is directly readable on current `master` and keeps the pinned-channel archive download, SHA-256 verification, and install-root replay path explicit beside the reminder guards.",
    "`zig run scripts/zigux/install_zig.zig -- --self-test`",
    "the pinned-channel, pinned-archive integrity, local-first archive workflow, third_party README contract, installer, toolchain-pinning, pin-scope, kbuild-route, tests-root reminder, direct cross-route, cross-selftest alignment, required-make-route, docs-shared-reminder, manifest, artifact-support, genksyms bridge, kconfig bridge, fixdep governance and parity packet",
    "Keep future Phase 2 follow-up inside one current packet surface at a time: toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness",
};

const REVIEW_MARKERS = [_][]const u8{
    "`scripts/zigux/install_zig.zig`",
    "`zig run scripts/zigux/install_zig.zig -- --self-test`",
    "`scripts\\zigux/check_phase2_cross.zig`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
};

const SCRIPTS_MARKERS = [_][]const u8{
    "`scripts/zigux/install_zig.zig`",
    "`zig run scripts/zigux/install_zig.zig -- --self-test`",
    "installer helper",
    "direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet",
};

const TESTS_MARKERS = [_][]const u8{
    "`scripts/zigux/install_zig.zig`",
    "`zig run scripts/zigux/install_zig.zig -- --self-test`",
    "`scripts\\zigux/check_phase2_cross.zig`",
    "`zig run scripts\\zigux/check_phase2_cross.zig -- --self-test`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
};

const WORKFLOW_LINES = [_][]const u8{
    "- name: Self-test current Lane 05 local archive README checker",
    "run: zig run scripts\\zigux/check_lane05_local_archive_readme.zig -- --self-test",
    "- name: Check current Lane 05 local archive README packet",
    "run: zig run scripts\\zigux/check_lane05_local_archive_readme.zig",
    "- name: Self-test current Zig installer helper",
    "run: zig run scripts/zigux/install_zig.zig -- --self-test",
    "- name: Self-test current Phase 2 fixdep gate checker",
    "run: zig run scripts\\zigux/check_phase2_fixdep_gate.zig -- --self-test",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase2-toolchain:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --policy-only",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig -- --archive-only --allow-missing",
    "phase2: phase2-validate",
};

const INSTALL_ZIG_MARKERS = [_][]const u8{
    "def load_policy_channel(",
    "def load_policy_archive_sha256(",
    "def verify_archive_sha256(",
    "def copy_url_to_file_with_curl(",
    "def copy_url_to_file(",
    "def load_index(",
    "def resolve_target(",
    "def extract_archive(",
    "def append_github_path(",
    "parser.add_argument(\"--resolve-only\"",
    "parser.add_argument(\"--self-test\"",
    "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
    "print('ZIG_INSTALL_SELF_TEST=pass')",
};

const EXPECTED_TARGET_SCOPE = [_][]const u8{
    "x86_64-linux",
};

const EXPECTED_REQUIRED_ROUTES = [_][]const u8{
    "phase2-toolchain",
    "phase2-validate",
    "phase2-cross",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_notes_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_notes_markers_path);
    const text_notes_markers = try guard.readUtf8File(io, allocator, text_notes_markers_path);
    defer allocator.free(text_notes_markers);
    for (NOTES_MARKERS) |marker| try guard.requireMarker(text_notes_markers, marker);
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
    const text_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_lines_path);
    const text_workflow_lines = try guard.readUtf8File(io, allocator, text_workflow_lines_path);
    defer allocator.free(text_workflow_lines);
    for (WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_workflow_lines, marker, 1);
    const text_makefile_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_markers_path);
    const text_makefile_markers = try guard.readUtf8File(io, allocator, text_makefile_markers_path);
    defer allocator.free(text_makefile_markers);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text_makefile_markers, marker);
    const text_install_zig_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/install_zig.zig");
    defer allocator.free(text_install_zig_markers_path);
    const text_install_zig_markers = try guard.readUtf8File(io, allocator, text_install_zig_markers_path);
    defer allocator.free(text_install_zig_markers);
    for (INSTALL_ZIG_MARKERS) |marker| try guard.requireMarker(text_install_zig_markers, marker);
    const text_expected_target_scope_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_target_scope_path);
    const text_expected_target_scope = try guard.readUtf8File(io, allocator, text_expected_target_scope_path);
    defer allocator.free(text_expected_target_scope);
    for (EXPECTED_TARGET_SCOPE) |marker| try guard.requireMarker(text_expected_target_scope, marker);
    const text_expected_required_routes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_required_routes_path);
    const text_expected_required_routes = try guard.readUtf8File(io, allocator, text_expected_required_routes_path);
    defer allocator.free(text_expected_required_routes);
    for (EXPECTED_REQUIRED_ROUTES) |marker| try guard.requireMarker(text_expected_required_routes, marker);
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

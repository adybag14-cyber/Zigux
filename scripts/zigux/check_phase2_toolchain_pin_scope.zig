const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_TOOLCHAIN_PIN_SCOPE=pass";
pub const self_test_pass_marker = "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass";

const DOCS_ROOT_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`third_party/README.md`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --self-test`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --policy-only`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux`",
    "`zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig --self-test`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "pinned archive-integrity replay",
    "pinned Zig toolchain",
};

const REVIEW_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --self-test`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --policy-only`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2`",
    "same pinned toolchain",
};

const TESTS_MARKERS = [_][]const u8{
    "`zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig --self-test`",
    "`scripts\\zigux/check_phase2_toolchain_pin_scope.zig`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --policy-only`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "pinned `x86_64-linux` bootstrap archive note",
    "repo-local `.zig-toolchain` fallback reused",
};

const BOOTSTRAP_MARKERS = [_][]const u8{
    "`zig run scripts\\zigux/check_zig_toolchain.zig --self-test`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --policy-only`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing`",
    "`zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz --archive-target x86_64-linux`",
    "`third_party/README.md`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "pinned-archive integrity paths",
};

const WORKFLOW_MARKERS = [_][]const u8{
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --self-test",
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --policy-only",
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase2-toolchain:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig --policy-only",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig --archive-only --allow-missing",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-kconfig: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
};

const MAKEFILE_VARIABLE_MARKERS = [_][]const u8{
    "ZIG_PINNED_TARGET := $(shell $(PYTHON) -c ",
    "[\"upgrade_policy\"][\"archive_target_scope\"][0]",
    "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)",
    "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))",
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
};

const TOOLCHAIN_CHECKER_MARKERS = [_][]const u8{
    "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"",
    "def load_min_version(",
    "def load_pinned_channel(",
    "def iter_repo_local_zig_candidates(",
    "def resolve_zig_executable(",
    "def iter_repo_local_archive_candidates(",
    "def resolve_policy_archive(",
    "def expected_archive_metadata(",
    "def validate_policy_archive(",
    "parser.add_argument(\"--allow-missing\"",
    "parser.add_argument(\"--policy-only\"",
    "parser.add_argument(\"--archive-only\"",
    "parser.add_argument(\"--archive\"",
    "parser.add_argument(\"--archive-target\"",
    "parser.add_argument(\"--zig\"",
};

const EXPECTED_TARGETS = [_][]const u8{
    "x86_64-linux",
};

const EXPECTED_REQUIRED_ROUTES = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_docs_root_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_docs_root_markers_path);
    const text_docs_root_markers = try guard.readUtf8File(io, allocator, text_docs_root_markers_path);
    defer allocator.free(text_docs_root_markers);
    for (DOCS_ROOT_MARKERS) |marker| try guard.requireMarker(text_docs_root_markers, marker);
    const text_review_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_review_markers_path);
    const text_review_markers = try guard.readUtf8File(io, allocator, text_review_markers_path);
    defer allocator.free(text_review_markers);
    for (REVIEW_MARKERS) |marker| try guard.requireMarker(text_review_markers, marker);
    const text_tests_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_tests_markers_path);
    const text_tests_markers = try guard.readUtf8File(io, allocator, text_tests_markers_path);
    defer allocator.free(text_tests_markers);
    for (TESTS_MARKERS) |marker| try guard.requireMarker(text_tests_markers, marker);
    const text_bootstrap_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_bootstrap_markers_path);
    const text_bootstrap_markers = try guard.readUtf8File(io, allocator, text_bootstrap_markers_path);
    defer allocator.free(text_bootstrap_markers);
    for (BOOTSTRAP_MARKERS) |marker| try guard.requireMarker(text_bootstrap_markers, marker);
    const text_workflow_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_markers_path);
    const text_workflow_markers = try guard.readUtf8File(io, allocator, text_workflow_markers_path);
    defer allocator.free(text_workflow_markers);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text_workflow_markers, marker);
    const text_makefile_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_markers_path);
    const text_makefile_markers = try guard.readUtf8File(io, allocator, text_makefile_markers_path);
    defer allocator.free(text_makefile_markers);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text_makefile_markers, marker);
    const text_makefile_variable_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_variable_markers_path);
    const text_makefile_variable_markers = try guard.readUtf8File(io, allocator, text_makefile_variable_markers_path);
    defer allocator.free(text_makefile_variable_markers);
    for (MAKEFILE_VARIABLE_MARKERS) |marker| try guard.requireMarker(text_makefile_variable_markers, marker);
    const text_toolchain_checker_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/check_zig_toolchain.zig");
    defer allocator.free(text_toolchain_checker_markers_path);
    const text_toolchain_checker_markers = try guard.readUtf8File(io, allocator, text_toolchain_checker_markers_path);
    defer allocator.free(text_toolchain_checker_markers);
    for (TOOLCHAIN_CHECKER_MARKERS) |marker| try guard.requireMarker(text_toolchain_checker_markers, marker);
    const text_expected_targets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_targets_path);
    const text_expected_targets = try guard.readUtf8File(io, allocator, text_expected_targets_path);
    defer allocator.free(text_expected_targets);
    for (EXPECTED_TARGETS) |marker| try guard.requireMarker(text_expected_targets, marker);
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

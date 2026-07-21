const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_ZIG_RESOLVER_PACKET=pass";
pub const self_test_pass_marker = "PHASE2_ZIG_RESOLVER_PACKET_SELF_TEST=pass";

const MAKEFILE_VARIABLE_MARKERS = [_][]const u8{
    "PHASE2_TOOLCHAIN_POLICY := $(PHASE2_SCRIPT_ROOT)/zig-toolchain-policy.json",
    "ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"channel\"])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
    "ZIG_PINNED_TARGET := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"upgrade_policy\"][\"archive_target_scope\"][0])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
    "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)",
    "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))",
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
};

const MAKEFILE_ROUTE_MARKERS = [_][]const u8{
    "phase2-toolchain:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig -- --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig",
    "phase2-kconfig: phase2-toolchain",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
};

const WORKFLOW_MARKERS = [_][]const u8{
    "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
    "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]",
    "extract_root=\"$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL\"",
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "if zig run scripts\\zigux/check_zig_toolchain.zig -- --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"; then",
    "if zig run scripts\\zigux/check_zig_toolchain.zig -- --zig \"$zig_path\"; then",
    "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
};

const TOOLCHAIN_CHECKER_MARKERS = [_][]const u8{
    "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"",
    "def load_pinned_channel(",
    "def iter_repo_local_zig_candidates(",
    "def resolve_zig_executable(",
    "def iter_repo_local_archive_candidates(",
    "def resolve_policy_archive(",
    "def expected_archive_metadata(",
    "def validate_policy_archive(",
    "parser.add_argument(\"--policy-only\"",
    "parser.add_argument(\"--archive-only\"",
    "parser.add_argument(\"--archive\"",
    "parser.add_argument(\"--archive-target\"",
    "parser.add_argument(\"--zig\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_makefile_variable_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_variable_markers_path);
    const text_makefile_variable_markers = try guard.readUtf8File(io, allocator, text_makefile_variable_markers_path);
    defer allocator.free(text_makefile_variable_markers);
    for (MAKEFILE_VARIABLE_MARKERS) |marker| try guard.requireMarker(text_makefile_variable_markers, marker);
    const text_makefile_route_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_route_markers_path);
    const text_makefile_route_markers = try guard.readUtf8File(io, allocator, text_makefile_route_markers_path);
    defer allocator.free(text_makefile_route_markers);
    for (MAKEFILE_ROUTE_MARKERS) |marker| try guard.requireMarker(text_makefile_route_markers, marker);
    const text_workflow_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_markers_path);
    const text_workflow_markers = try guard.readUtf8File(io, allocator, text_workflow_markers_path);
    defer allocator.free(text_workflow_markers);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text_workflow_markers, marker);
    const text_toolchain_checker_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/check_zig_toolchain.zig");
    defer allocator.free(text_toolchain_checker_markers_path);
    const text_toolchain_checker_markers = try guard.readUtf8File(io, allocator, text_toolchain_checker_markers_path);
    defer allocator.free(text_toolchain_checker_markers);
    for (TOOLCHAIN_CHECKER_MARKERS) |marker| try guard.requireMarker(text_toolchain_checker_markers, marker);
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

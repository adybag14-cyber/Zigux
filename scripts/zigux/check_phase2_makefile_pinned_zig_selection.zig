const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_MAKEFILE_PINNED_ZIG_SELECTION=pass";
pub const self_test_pass_marker = "PHASE2_MAKEFILE_PINNED_ZIG_SELECTION_SELF_TEST=pass";

const EXPECTED_CHANNEL = [_][]const u8{
    "0.17.0-dev.877+a3ae499dc",
};

const EXPECTED_TARGET = [_][]const u8{
    "x86_64-linux",
};

const EXPECTED_ROUTES = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

const MAKEFILE_LINES = [_][]const u8{
    "PHASE2_TOOLCHAIN_POLICY := ../scripts/zigux/zig-toolchain-policy.json",
    "ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"channel\"])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
    "ZIG_PINNED_TARGET := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"upgrade_policy\"][\"archive_target_scope\"][0])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
    "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)",
    "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))",
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
};

const TOOLCHAIN_MARKERS = [_][]const u8{
    "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"",
    "def load_pinned_channel(policy_path: Path = TOOLCHAIN_POLICY) -> str | None:",
    "add_search_root(root / \".zig-toolchain\")",
    "add_search_root(root / \"toolchains\")",
    "add_search_root(root / \".toolchains\")",
    "pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"",
    "add_candidate_roots(base / pinned_dirname)",
};

const NOTE_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_zig_toolchain.zig` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    "`scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.877+a3ae499dc`",
    "`make -C zigux phase2-toolchain`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_channel_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_expected_channel_path);
    const text_expected_channel = try guard.readUtf8File(io, allocator, text_expected_channel_path);
    defer allocator.free(text_expected_channel);
    for (EXPECTED_CHANNEL) |marker| try guard.requireMarker(text_expected_channel, marker);
    const text_expected_target_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_expected_target_path);
    const text_expected_target = try guard.readUtf8File(io, allocator, text_expected_target_path);
    defer allocator.free(text_expected_target);
    for (EXPECTED_TARGET) |marker| try guard.requireMarker(text_expected_target, marker);
    const text_expected_routes_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_expected_routes_path);
    const text_expected_routes = try guard.readUtf8File(io, allocator, text_expected_routes_path);
    defer allocator.free(text_expected_routes);
    for (EXPECTED_ROUTES) |marker| try guard.requireMarker(text_expected_routes, marker);
    const text_makefile_lines_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_lines_path);
    const text_makefile_lines = try guard.readUtf8File(io, allocator, text_makefile_lines_path);
    defer allocator.free(text_makefile_lines);
    for (MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_makefile_lines, marker, 1);
    const text_toolchain_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_toolchain_markers_path);
    const text_toolchain_markers = try guard.readUtf8File(io, allocator, text_toolchain_markers_path);
    defer allocator.free(text_toolchain_markers);
    for (TOOLCHAIN_MARKERS) |marker| try guard.requireMarker(text_toolchain_markers, marker);
    const text_note_markers_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_note_markers_path);
    const text_note_markers = try guard.readUtf8File(io, allocator, text_note_markers_path);
    defer allocator.free(text_note_markers);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text_note_markers, marker);
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

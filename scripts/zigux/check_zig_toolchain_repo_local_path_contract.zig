const std = @import("std");
const testing = std.testing;

const checker_source = @embedFile("check-zig-toolchain.py");

fn requireContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn requireOrder(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, checker_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, checker_source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn requireBeforeLast(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, checker_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.lastIndexOf(u8, checker_source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "repo local zig search roots prefer project-local toolchain directories" {
    try requireContains("def iter_zig_search_roots(root: Path = ROOT) -> list[Path]:");
    try requireContains("add_search_root(root / \".zig-toolchain\")");
    try requireContains("add_search_root(root / \"toolchains\")");
    try requireContains("add_search_root(root / \".toolchains\")");
    try requireContains("for parent in root.parents:");
    try requireContains("add_search_root(parent / \".toolchains\")");
    try requireContains("add_search_root(parent / \"toolchains\")");

    try requireOrder("add_search_root(root / \".zig-toolchain\")", "add_search_root(root / \"toolchains\")");
    try requireOrder("add_search_root(root / \"toolchains\")", "add_search_root(root / \".toolchains\")");
    try requireOrder("add_search_root(root / \".toolchains\")", "for parent in root.parents:");
}

test "pinned channel candidates are searched before generic repo-local zig executables" {
    try requireContains("def iter_repo_local_zig_candidates(");
    try requireContains("pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"");
    try requireContains("add_candidate_roots(base / pinned_dirname)");
    try requireContains("add_candidate_roots(child / pinned_dirname)");
    try requireContains("for base in zig_search_roots:");
    try requireContains("add_candidate_roots(base)");
    try requireContains("add_candidate_roots(child)");

    try requireOrder("pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"", "add_candidate_roots(base / pinned_dirname)");
    try requireBeforeLast("add_candidate_roots(child / pinned_dirname)", "for base in zig_search_roots:");
    try requireBeforeLast("add_candidate_roots(child / pinned_dirname)", "add_candidate_roots(base)");
}

test "explicit zig wins before repo-local search and PATH fallback" {
    try requireContains("def resolve_zig_executable(");
    try requireContains("if explicit_zig is not None:");
    try requireContains("return normalize_explicit_zig_path(explicit_zig)");
    try requireContains("pinned_channel = load_pinned_channel(policy_path)");
    try requireContains("for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):");
    try requireContains("return which(\"zig\")");

    try requireOrder("if explicit_zig is not None:", "pinned_channel = load_pinned_channel(policy_path)");
    try requireOrder("pinned_channel = load_pinned_channel(policy_path)", "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):");
    try requireOrder("for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):", "return which(\"zig\")");
}

test "missing zig diagnostics keep pinned channel and search roots visible" {
    try requireContains("def describe_missing_zig(");
    try requireContains("message = \"zig not found on PATH or in repo-local toolchain search roots\"");
    try requireContains("message += f\" for pinned channel {pinned_channel}\"");
    try requireContains("return message, format_search_roots(search_roots)");
    try requireContains("print(\"ZIG_TOOLCHAIN_STATUS=missing\")");
    try requireContains("print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try requireContains("print(f\"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}\")");

    try requireOrder("message += f\" for pinned channel {pinned_channel}\"", "return message, format_search_roots(search_roots)");
    try requireOrder("print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")", "print(f\"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}\")");
}

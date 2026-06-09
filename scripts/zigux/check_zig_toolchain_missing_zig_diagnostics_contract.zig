const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "missing zig helper preserves pinned-channel search-root diagnostic" {
    try expectContains(checker_source, "def describe_missing_zig(");
    try expectContains(checker_source, "message = \"zig not found on PATH or in repo-local toolchain search roots\"");
    try expectContains(checker_source, "message += f\" for pinned channel {pinned_channel}\"");
    try expectContains(checker_source, "return message, format_search_roots(search_roots)");
    try expectContains(checker_source, "def format_search_roots(search_roots: list[Path]) -> str:");
    try expectContains(checker_source, "\",\".join(str(path) for path in search_roots)");
}

test "missing zig status packet reports policy and search roots before exit" {
    const missing_block = "if zig is None:";

    try expectContains(checker_source, "search_roots = iter_zig_search_roots()");
    try expectContains(checker_source, "message, search_roots_summary = describe_missing_zig(");
    try expectContains(checker_source, "pinned_channel=expected_channel_raw");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_STATUS=missing\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PATH=unresolved\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try expectContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}\")");
    try expectContains(checker_source, "print(f\"ZIG_TOOLCHAIN_NOTE={message}\")");
    try expectContains(checker_source, "return 0 if args.allow_missing else 1");
    try expectOrdered(checker_source, missing_block, "return 0 if args.allow_missing else 1");
    try expectOrdered(checker_source, missing_block, "version = read_zig_version(zig)");
}

test "resolver only reports missing after explicit repo-local and path probes" {
    try expectContains(checker_source, "def resolve_zig_executable(");
    try expectContains(checker_source, "if explicit_zig is not None:");
    try expectContains(checker_source, "return normalize_explicit_zig_path(explicit_zig)");
    try expectContains(checker_source, "pinned_channel = load_pinned_channel(policy_path)");
    try expectContains(checker_source, "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):");
    try expectContains(checker_source, "if candidate.is_file():");
    try expectContains(checker_source, "return which(\"zig\")");
    try expectOrdered(checker_source, "if explicit_zig is not None:", "pinned_channel = load_pinned_channel(policy_path)");
    try expectOrdered(checker_source, "for candidate in iter_repo_local_zig_candidates", "return which(\"zig\")");
}

test "self-test keeps missing executable fallback anchors" {
    try expectContains(checker_source, "expect_raises(lambda: normalize_explicit_zig_path(\"/tmp/zigux-toolchain-self-test-missing-zig\"), \"explicit zig path does not exist\")");
    try expectContains(checker_source, "expect_equal(resolve_zig_executable(root=root, policy_path=policy_path, which=lambda _: \"/usr/bin/zig\"), \"/usr/bin/zig\")");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_SELF_TEST=pass");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT=");
}

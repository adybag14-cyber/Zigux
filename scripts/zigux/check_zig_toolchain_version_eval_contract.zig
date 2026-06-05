const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn requireMarker(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn requireAbsent(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) == null);
}

fn requireOrder(source: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, source, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, source, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "version comparison distinguishes minimum and exact pin failures" {
    try requireMarker(checker_source, "VERSION_RE = re.compile(");
    try requireMarker(checker_source, "@dataclass(frozen=True, order=True)");
    try requireMarker(checker_source, "class ZigVersion:");
    try requireMarker(checker_source, "release_rank=1 if dev_build is None else 0");
    try requireMarker(checker_source, "dev_build=int(dev_build) if dev_build is not None else 0");
    try requireMarker(checker_source, "def evaluate_toolchain_version(");
    try requireMarker(checker_source, "if parsed_version < min_version:");
    try requireMarker(checker_source, "return \"too_old\", None");
    try requireMarker(checker_source, "return \"not_pinned\", f\"expected pinned Zig channel {expected_channel_raw}\"");
    try requireMarker(checker_source, "return \"present\", None");

    try requireMarker(checker_source, "\"0.17.0-dev.759+abcdef\"");
    try requireMarker(checker_source, "(\"not_pinned\", \"expected pinned Zig channel 0.17.0-dev.758+748e7c5e3\")");
    try requireMarker(checker_source, "(\"too_old\", None)");
}

test "zig version command failures keep explicit diagnostics" {
    try requireMarker(checker_source, "raise ValueError(f\"zig executable not found: {zig}\") from exc");
    try requireMarker(checker_source, "raise ValueError(f\"failed to execute zig at {zig}: {exc}\") from exc");
    try requireMarker(checker_source, "detail = completed.stderr.strip() or completed.stdout.strip() or f\"exit code {completed.returncode}\"");
    try requireMarker(checker_source, "raise ValueError(f\"zig version command failed: {detail}\")");
    try requireMarker(checker_source, "raise ValueError(\"zig version command returned empty output\")");
    try requireMarker(checker_source, "\"zig version command failed: permission denied\"");
    try requireMarker(checker_source, "\"zig version command returned empty output\"");
}

test "executable status output preserves exact and minimum-only policy surfaces" {
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_STATUS=invalid");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_STATUS=missing");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_STATUS={status}");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_PATH=unresolved");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_PATH={zig}");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_VERSION={version}");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_PIN_POLICY=exact");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_PIN_POLICY=minimum_only");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_PIN_POLICY=unresolved");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_NOTE={message}");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_NOTE={note}");

    try requireOrder(checker_source, "print(f\"ZIG_TOOLCHAIN_STATUS={status}\")", "print(f\"ZIG_TOOLCHAIN_PATH={zig}\")");
    try requireOrder(checker_source, "print(f\"ZIG_TOOLCHAIN_PATH={zig}\")", "print(f\"ZIG_TOOLCHAIN_VERSION={version}\")");
    try requireOrder(checker_source, "print(f\"ZIG_TOOLCHAIN_VERSION={version}\")", "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}\")");
    try requireOrder(checker_source, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")", "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try requireOrder(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")", "if note is not None:");
}

test "missing-toolchain branch remains pinned-channel aware" {
    try requireMarker(checker_source, "describe_missing_zig(");
    try requireMarker(checker_source, "zig not found on PATH or in repo-local toolchain search roots for pinned channel");
    try requireMarker(checker_source, "zig not found on PATH or in repo-local toolchain search roots");
    try requireMarker(checker_source, "return 0 if args.allow_missing else 1");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_SELF_TEST=pass");
    try requireMarker(checker_source, "ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT=");
    try requireAbsent(checker_source, "expected pinned Zig channel master");
}

const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsAfter(haystack: []const u8, anchor: []const u8, needle: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, haystack, anchor) orelse return error.MissingAnchor;
    const tail = haystack[anchor_index + anchor.len ..];
    try std.testing.expect(std.mem.indexOf(u8, tail, needle) != null);
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const tail = haystack[earlier_index + earlier.len ..];
    try std.testing.expect(std.mem.indexOf(u8, tail, later) != null);
}

test "read_zig_version converts command failures into stable diagnostics" {
    try expectContains(checker_source, "def read_zig_version(zig: str, *, runner=subprocess.run) -> str:");
    try expectContains(checker_source, "completed = runner([zig, \"version\"], capture_output=True, text=True, check=False)");
    try expectContains(checker_source, "except FileNotFoundError as exc:");
    try expectContains(checker_source, "raise ValueError(f\"zig executable not found: {zig}\") from exc");
    try expectContains(checker_source, "except OSError as exc:");
    try expectContains(checker_source, "raise ValueError(f\"failed to execute zig at {zig}: {exc}\") from exc");
    try expectContains(checker_source, "if completed.returncode != 0:");
    try expectContains(checker_source, "detail = completed.stderr.strip() or completed.stdout.strip() or f\"exit code {completed.returncode}\"");
    try expectContains(checker_source, "raise ValueError(f\"zig version command failed: {detail}\")");
    try expectContains(checker_source, "if not version:");
    try expectContains(checker_source, "raise ValueError(\"zig version command returned empty output\")");
}

test "main invalid envelope preserves zig command context" {
    try expectOrdered(
        checker_source,
        "version = read_zig_version(zig)",
        "status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)",
    );
    try expectContainsAfter(checker_source, "version = read_zig_version(zig)", "except ValueError as exc:");
    try expectContainsAfter(checker_source, "version = read_zig_version(zig)", "print(\"ZIG_TOOLCHAIN_STATUS=invalid\")");
    try expectContainsAfter(checker_source, "version = read_zig_version(zig)", "print(f\"ZIG_TOOLCHAIN_PATH={zig}\")");
    try expectContainsAfter(checker_source, "version = read_zig_version(zig)", "if version is not None:");
    try expectContainsAfter(checker_source, "version = read_zig_version(zig)", "print(f\"ZIG_TOOLCHAIN_VERSION={version}\")");
    try expectContainsAfter(checker_source, "version = read_zig_version(zig)", "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}\")");
    try expectContainsAfter(checker_source, "version = read_zig_version(zig)", "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try expectContainsAfter(checker_source, "version = read_zig_version(zig)", "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try expectContainsAfter(checker_source, "version = read_zig_version(zig)", "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try expectContainsAfter(checker_source, "version = read_zig_version(zig)", "print(\"ZIG_TOOLCHAIN_PIN_POLICY=unresolved\")");
    try expectContainsAfter(checker_source, "version = read_zig_version(zig)", "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
}

test "self-test covers missing nonzero and empty zig version outputs" {
    try expectContains(checker_source, "read_zig_version(");
    try expectContains(checker_source, "stdout=\"0.17.0-dev.758+748e7c5e3\\n\"");
    try expectContains(checker_source, "runner=lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError(\"missing\"))");
    try expectContains(checker_source, "\"zig executable not found\"");
    try expectContains(checker_source, "stderr=\"permission denied\\n\"");
    try expectContains(checker_source, "\"zig version command failed: permission denied\"");
    try expectContains(checker_source, "stdout=\"\\n\"");
    try expectContains(checker_source, "\"zig version command returned empty output\"");
}

test "version command failure stays separate from version comparison" {
    try expectContains(checker_source, "def evaluate_toolchain_version(");
    try expectOrdered(
        checker_source,
        "version = read_zig_version(zig)",
        "status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)",
    );
    try expectContains(checker_source, "return \"not_pinned\", f\"expected pinned Zig channel {expected_channel_raw}\"");
    try expectContains(checker_source, "return \"too_old\", None");
}

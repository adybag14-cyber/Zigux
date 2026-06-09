const std = @import("std");

const CHECKER_PATH = "scripts/zigux/check-zig-toolchain.py";
const POLICY_PATH = "scripts/zigux/zig-toolchain-policy.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(
        std.mem.indexOf(u8, haystack, needle) != null,
    );
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn expectOrderedAfter(haystack: []const u8, anchor: []const u8, before: []const u8, after: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, haystack, anchor) orelse return error.MissingAnchorMarker;
    const before_index = std.mem.indexOfPos(u8, haystack, anchor_index, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOfPos(u8, haystack, before_index, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "version probe keeps precise execution failure diagnostics" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, CHECKER_PATH);
    defer allocator.free(checker);

    try expectContains(checker, "def read_zig_version(zig: str, *, runner=subprocess.run) -> str:");
    try expectContains(checker, "except FileNotFoundError as exc:");
    try expectContains(checker, "raise ValueError(f\"zig executable not found: {zig}\") from exc");
    try expectContains(checker, "except OSError as exc:");
    try expectContains(checker, "raise ValueError(f\"failed to execute zig at {zig}: {exc}\") from exc");
    try expectContains(checker, "if completed.returncode != 0:");
    try expectContains(checker, "detail = completed.stderr.strip() or completed.stdout.strip() or f\"exit code {completed.returncode}\"");
    try expectContains(checker, "raise ValueError(f\"zig version command failed: {detail}\")");
    try expectContains(checker, "if not version:");
    try expectContains(checker, "raise ValueError(\"zig version command returned empty output\")");

    try expectOrdered(checker, "version = completed.stdout.strip()", "if not version:");
    try expectOrdered(checker, "if completed.returncode != 0:", "version = completed.stdout.strip()");
}

test "main executable probe failure reports invalid exact-pin status envelope" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, CHECKER_PATH);
    defer allocator.free(checker);

    try expectContains(checker, "zig = resolve_zig_executable(args.zig)");
    try expectContains(checker, "min_version_raw = args.min_version or load_min_version()");
    try expectContains(checker, "expected_channel_raw = None if args.min_version else load_pinned_channel()");
    try expectContains(checker, "version = read_zig_version(zig)");
    try expectContains(checker, "status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)");
    try expectContains(checker, "except ValueError as exc:");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_STATUS=invalid\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_PATH={zig}\")");
    try expectContains(checker, "if version is not None:");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_VERSION={version}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try expectContains(checker, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try expectContains(checker, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try expectContains(checker, "return 1");

    try expectOrderedAfter(
        checker,
        "try:\n        version = read_zig_version(zig)",
        "version = read_zig_version(zig)",
        "except ValueError as exc:",
    );
    try expectOrdered(checker, "print(\"ZIG_TOOLCHAIN_STATUS=invalid\")", "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
}

test "self test covers version probe failure cases" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, CHECKER_PATH);
    defer allocator.free(checker);

    try expectContains(checker, "read_zig_version(");
    try expectContains(checker, "subprocess.CompletedProcess(");
    try expectContains(checker, "stdout=\"0.17.0-dev.758+748e7c5e3\\n\"");
    try expectContains(checker, "(_ for _ in ()).throw(FileNotFoundError(\"missing\"))");
    try expectContains(checker, "\"zig executable not found\"");
    try expectContains(checker, "stderr=\"permission denied\\n\"");
    try expectContains(checker, "\"zig version command failed: permission denied\"");
    try expectContains(checker, "stdout=\"\\n\"");
    try expectContains(checker, "\"zig version command returned empty output\"");
    try expectContains(checker, "ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT={case_count}");
}

test "version probe contract stays tied to current pinned policy tuple" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, CHECKER_PATH);
    defer allocator.free(checker);
    const policy = try readRepoFile(allocator, POLICY_PATH);
    defer allocator.free(policy);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(checker, "parse_zig_version(min_version_raw)");
    try expectContains(checker, "parse_zig_version(expected_channel_raw)");
    try expectContains(checker, "evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)");
    try expectContains(checker, "return \"not_pinned\", f\"expected pinned Zig channel {expected_channel_raw}\"");
}

const std = @import("std");

const checker_path = "check-zig-toolchain.py";
const checker_source = @embedFile(checker_path);

fn requireContains(source: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, source, marker) == null) {
        std.debug.print("missing marker in {s}: {s}\n", .{ checker_path, marker });
        return error.MissingMarker;
    }
}

fn requireOrdered(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse {
        std.debug.print("missing ordered marker in {s}: {s}\n", .{ checker_path, before });
        return error.MissingMarker;
    };
    const after_index = std.mem.indexOf(u8, source, after) orelse {
        std.debug.print("missing ordered marker in {s}: {s}\n", .{ checker_path, after });
        return error.MissingMarker;
    };
    try std.testing.expect(before_index < after_index);
}

test "toolchain version status decisions remain exact and ordered" {
    const source = checker_source;

    try requireContains(source, "def evaluate_toolchain_version(");
    try requireContains(source, "parsed_version = parse_zig_version(version)");
    try requireContains(source, "min_version = parse_zig_version(min_version_raw)");
    try requireContains(source, "return \"too_old\", None");
    try requireContains(source, "parse_zig_version(expected_channel_raw)");
    try requireContains(source, "if version.strip() != expected_channel_raw:");
    try requireContains(source, "return \"not_pinned\", f\"expected pinned Zig channel {expected_channel_raw}\"");
    try requireContains(source, "return \"present\", None");

    try requireOrdered(source, "if parsed_version < min_version:", "return \"too_old\", None");
    try requireOrdered(source, "return \"too_old\", None", "if expected_channel_raw is not None:");
    try requireContains(source, "return \"not_pinned\", f\"expected pinned Zig channel {expected_channel_raw}\"\n    return \"present\", None");
}

test "toolchain CLI reports the final status packet" {
    const source = checker_source;

    try requireContains(source, "status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)");
    try requireContains(source, "exit_code = 0 if status == \"present\" else 1");
    try requireContains(source, "print(f\"ZIG_TOOLCHAIN_STATUS={status}\")");
    try requireContains(source, "print(f\"ZIG_TOOLCHAIN_PATH={zig}\")");
    try requireContains(source, "print(f\"ZIG_TOOLCHAIN_VERSION={version}\")");
    try requireContains(source, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}\")");
    try requireContains(source, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try requireContains(source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try requireContains(source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try requireContains(source, "if note is not None:");
    try requireContains(source, "print(f\"ZIG_TOOLCHAIN_NOTE={note}\")");
    try requireContains(source, "return exit_code");
}

test "checker self-test covers present not-pinned and too-old outcomes" {
    const source = checker_source;

    try requireContains(source, "evaluate_toolchain_version(\"0.17.0-dev.758+748e7c5e3\", \"0.17.0-dev.758+748e7c5e3\")");
    try requireContains(source, "(\"present\", None)");
    try requireContains(source, "(\"not_pinned\", \"expected pinned Zig channel 0.17.0-dev.758+748e7c5e3\")");
    try requireContains(source, "(\"too_old\", None)");
    try requireContains(source, "ZIG_TOOLCHAIN_SELF_TEST=pass");
    try requireContains(source, "ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT=");
}

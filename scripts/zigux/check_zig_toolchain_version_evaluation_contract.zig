const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, checker_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, checker_source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "version evaluation keeps exact present too old and not pinned states" {
    try expectContains("def evaluate_toolchain_version(");
    try expectContains("parsed_version = parse_zig_version(version)");
    try expectContains("min_version = parse_zig_version(min_version_raw)");
    try expectContains(
        \\if parsed_version < min_version:
        \\        return "too_old", None
    );
    try expectContains(
        \\if expected_channel_raw is not None:
        \\        expected_channel_raw = expected_channel_raw.strip()
    );
    try expectContains(
        \\if version.strip() != expected_channel_raw:
        \\            return "not_pinned", f"expected pinned Zig channel {expected_channel_raw}"
    );
    try expectContains(
        \\return "present", None
    );

    try expectBefore(
        "if parsed_version < min_version:",
        "if expected_channel_raw is not None:",
    );
    try expectContains(
        \\if expected_channel_raw is not None:
        \\        expected_channel_raw = expected_channel_raw.strip()
        \\        parse_zig_version(expected_channel_raw)
        \\        if version.strip() != expected_channel_raw:
        \\            return "not_pinned", f"expected pinned Zig channel {expected_channel_raw}"
        \\    return "present", None
    );
}

test "successful probe reports evaluated status and pin policy fields" {
    try expectContains("version = read_zig_version(zig)");
    try expectContains("status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)");
    try expectContains("exit_code = 0 if status == \"present\" else 1");
    try expectContains("print(f\"ZIG_TOOLCHAIN_STATUS={status}\")");
    try expectContains("print(f\"ZIG_TOOLCHAIN_PATH={zig}\")");
    try expectContains("print(f\"ZIG_TOOLCHAIN_VERSION={version}\")");
    try expectContains("print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}\")");
    try expectContains("print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try expectContains("print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try expectContains("print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try expectContains("print(f\"ZIG_TOOLCHAIN_NOTE={note}\")");
    try expectContains("return exit_code");
    try expectContains(
        \\print(f"ZIG_TOOLCHAIN_STATUS={status}")
        \\    print(f"ZIG_TOOLCHAIN_PATH={zig}")
        \\    print(f"ZIG_TOOLCHAIN_VERSION={version}")
        \\    print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")
    );

    try expectBefore("version = read_zig_version(zig)", "status, note = evaluate_toolchain_version");
    try expectBefore("exit_code = 0 if status == \"present\" else 1", "print(f\"ZIG_TOOLCHAIN_STATUS={status}\")");
    try expectBefore("if note is not None:", "print(f\"ZIG_TOOLCHAIN_NOTE={note}\")");
}

test "self test covers version evaluation branches" {
    try expectContains("evaluate_toolchain_version(");
    try expectContains("(\"not_pinned\", \"expected pinned Zig channel");
    try expectContains("(\"too_old\", None)");
    try expectContains("print(\"ZIG_TOOLCHAIN_SELF_TEST=pass\")");
    try expectContains("print(f\"ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT={case_count}\")");

    try expectBefore(
        "expect_equal(\n        evaluate_toolchain_version",
        "print(\"ZIG_TOOLCHAIN_SELF_TEST=pass\")",
    );
}

const std = @import("std");
const testing = std.testing;

const checker_source = @embedFile("check-zig-toolchain.py");
const policy_source = @embedFile("zig-toolchain-policy.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "policy summary emits action-stable policy fields" {
    if (std.mem.indexOf(u8, checker_source, "def emit_policy_summary(") != null) {
        try expectContains(checker_source, "ZIG_TOOLCHAIN_POLICY_STATUS=present");
        try expectContains(checker_source, "ZIG_TOOLCHAIN_POLICY_STATUS=missing");
        try expectContains(checker_source, "ZIG_TOOLCHAIN_POLICY_PATH=");
        try expectContains(checker_source, "ZIG_TOOLCHAIN_PHASE=");
        try expectContains(checker_source, "ZIG_TOOLCHAIN_ARCHIVE_TARGET_COUNT=");
        try expectContains(checker_source, "ZIG_TOOLCHAIN_ARCHIVE_TARGETS=");
        try expectContains(checker_source, "ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=");
        try expectBefore(
            checker_source,
            "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=present\")",
            "print(f\"ZIG_TOOLCHAIN_PHASE={payload['phase']}\")",
        );
    }

    try expectContains(checker_source, "ZIG_TOOLCHAIN_MIN_SUPPORTED=");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_PINNED_CHANNEL=");
}

test "pin policy status remains explicit and fail closed" {
    try expectContains(checker_source, "ZIG_TOOLCHAIN_PIN_POLICY=exact");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_PIN_POLICY=minimum_only");
    try expectContains(checker_source, "ZIG_TOOLCHAIN_PIN_POLICY=unresolved");

    if (std.mem.indexOf(u8, checker_source, "channel_minimum_lockstep") != null) {
        try expectContains(checker_source, "\"channel_minimum_lockstep\"");
        try expectContains(checker_source, "minimum_version must match channel when channel_minimum_lockstep is true");
        try expectContains(checker_source, "ZIG_TOOLCHAIN_PIN_POLICY=\" + (\"exact\"");
    }
}

test "policy file keeps Lane 18 action routes visible to the checker" {
    try expectContains(policy_source, "\"phase\": \"Phase 2\"");
    try expectContains(policy_source, "\"channel\"");
    try expectContains(policy_source, "\"minimum_version\"");
    try expectContains(policy_source, "\"archive_target_scope\"");
    try expectContains(policy_source, "\"required_make_routes\"");
    try expectContains(policy_source, "\"phase2-toolchain\"");
    try expectContains(policy_source, "\"phase2-validate\"");
    if (std.mem.indexOf(u8, policy_source, "\"phase2-cross\"") != null) {
        try expectBefore(policy_source, "\"phase2-toolchain\"", "\"phase2-cross\"");
        try expectBefore(policy_source, "\"phase2-cross\"", "\"phase2-validate\"");
    }
}

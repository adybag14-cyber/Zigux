const std = @import("std");

const checker_path = "check-zig-toolchain.py";

const min_version_override_markers = [_][]const u8{
    "\"--min-version\"",
    "Minimum supported Zig version string. Defaults to scripts/zigux/zig-toolchain-policy.json when available.",
    "min_version_raw: str | None = args.min_version",
    "min_version_raw = args.min_version or load_min_version()",
    "expected_channel_raw = None if args.min_version else load_pinned_channel()",
    "parse_zig_version(min_version_raw)",
    "elif args.min_version is not None:",
    "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")",
};

const pinned_policy_markers = [_][]const u8{
    "load_pinned_channel()",
    "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")",
    "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "min-version override keeps checker on explicit minimum-only path" {
    const source = @embedFile(checker_path);

    for (min_version_override_markers) |marker| {
        try expectContains(source, marker);
    }
}

test "min-version override preserves pinned-policy path as the default" {
    const source = @embedFile(checker_path);

    for (pinned_policy_markers) |marker| {
        try expectContains(source, marker);
    }

    const override_gate = std.mem.indexOf(u8, source, "expected_channel_raw = None if args.min_version else load_pinned_channel()") orelse return error.MissingOverrideGate;
    const min_only_policy = std.mem.indexOf(u8, source[override_gate..], "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")") orelse return error.MissingMinimumOnlyPolicy;
    const exact_policy_after_gate = std.mem.indexOf(u8, source[override_gate..], "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")") orelse return error.MissingExactPolicy;

    try std.testing.expect(min_only_policy > exact_policy_after_gate);
}

test "min-version override still validates explicit version syntax before probing zig" {
    const source = @embedFile(checker_path);

    const override_assignment = std.mem.indexOf(u8, source, "min_version_raw = args.min_version or load_min_version()") orelse return error.MissingMinVersionAssignment;
    const version_parse = std.mem.indexOf(u8, source[override_assignment..], "parse_zig_version(min_version_raw)") orelse return error.MissingMinVersionParse;
    const zig_probe = std.mem.indexOf(u8, source[override_assignment..], "read_zig_version(zig)") orelse return error.MissingZigProbe;

    try std.testing.expect(version_parse < zig_probe);
}

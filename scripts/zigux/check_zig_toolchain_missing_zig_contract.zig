const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn expectMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, marker) != null);
}

test "missing zig path reports pinned search roots" {
    try expectMarker("if zig is None:");
    try expectMarker("search_roots = iter_zig_search_roots()");
    try expectMarker("pinned_channel=expected_channel_raw");
    try expectMarker("ZIG_TOOLCHAIN_STATUS=missing");
    try expectMarker("ZIG_TOOLCHAIN_PATH=unresolved");
    try expectMarker("ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}");
    try expectMarker("ZIG_TOOLCHAIN_NOTE={message}");
}

test "missing zig preserves exact and minimum-only pin policy output" {
    try expectMarker("ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}");
    try expectMarker("ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}");
    try expectMarker("ZIG_TOOLCHAIN_PIN_POLICY=exact");
    try expectMarker("ZIG_TOOLCHAIN_PIN_POLICY=minimum_only");
    try expectMarker("return 0 if args.allow_missing else 1");
}

test "missing zig note names repo-local search roots and pinned channel" {
    try expectMarker("def describe_missing_zig(");
    try expectMarker("message = \"zig not found on PATH or in repo-local toolchain search roots\"");
    try expectMarker("for pinned channel {pinned_channel}");
    try expectMarker("return message, format_search_roots(search_roots)");
}

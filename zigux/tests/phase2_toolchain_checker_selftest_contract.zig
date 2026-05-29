const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireMarker(source: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, source, marker) == null) {
        std.debug.print("missing marker: {s}\n", .{marker});
        return error.MissingContractMarker;
    }
}

test "toolchain checker keeps its self-test entrypoint and success markers" {
    const checker = try readRepoFile(checker_path);
    defer std.testing.allocator.free(checker);

    try requireMarker(checker, "def run_self_test() -> int:");
    try requireMarker(checker, "parser.add_argument(\"--self-test\"");
    try requireMarker(checker, "if args.self_test:");
    try requireMarker(checker, "return run_self_test()");
    try requireMarker(checker, "print(\"ZIG_TOOLCHAIN_SELF_TEST=pass\")");
    try requireMarker(checker, "print(f\"ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT={case_count}\")");
}

test "toolchain checker self-test keeps version ordering and pin diagnostics covered" {
    const checker = try readRepoFile(checker_path);
    defer std.testing.allocator.free(checker);

    try requireMarker(checker, "parse_zig_version(\"0.17.0-dev.90\") > parse_zig_version(\"0.17.0-dev.87+9b177a7d2\")");
    try requireMarker(checker, "parse_zig_version(\"0.17.0\") > parse_zig_version(\"0.17.0-dev.999+abcdef\")");
    try requireMarker(checker, "parse_zig_version(\"0.17.1-dev.1\") > parse_zig_version(\"0.17.0\")");
    try requireMarker(checker, "(\"not_pinned\", \"expected pinned Zig channel 0.17.0-dev.87+9b177a7d2\")");
    try requireMarker(checker, "(\"too_old\", None)");
}

test "toolchain checker self-test keeps executable failure diagnostics covered" {
    const checker = try readRepoFile(checker_path);
    defer std.testing.allocator.free(checker);

    try requireMarker(checker, "def resolve_zig_executable(");
    try requireMarker(checker, "zig executable not found");
    try requireMarker(checker, "zig version command failed: permission denied");
    try requireMarker(checker, "zig version command returned empty output");
    try requireMarker(checker, "ZIG_TOOLCHAIN_STATUS=invalid");
    try requireMarker(checker, "ZIG_TOOLCHAIN_STATUS=missing");
}

test "toolchain policy stays aligned with the self-test's pinned channel" {
    const policy = try readRepoFile(policy_path);
    defer std.testing.allocator.free(policy);

    try requireMarker(policy, "\"phase\": \"Phase 2\"");
    try requireMarker(policy, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try requireMarker(policy, "\"minimum_version\": \"0.17.0-dev.87+9b177a7d2\"");
    try requireMarker(policy, "\"channel_minimum_lockstep\": true");
    try requireMarker(policy, "\"archive_target_scope\"");
    try requireMarker(policy, "\"x86_64-linux\"");
    try requireMarker(policy, "\"phase2-toolchain\"");
    try requireMarker(policy, "\"phase2-validate\"");
}

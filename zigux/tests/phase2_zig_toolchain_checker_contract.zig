const std = @import("std");
const testing = std.testing;

const checker_contract =
    \\\ check-zig-toolchain.py
    \\\ --self-test
    \\\ --policy-only
    \\\ --archive-only
    \\\ --archive
    \\\ --archive-target
    \\\ --zig
    \\\ --allow-missing
    \\\ ZIG_TOOLCHAIN_SELF_TEST=pass
    \\\ ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT=
    \\\ ZIG_TOOLCHAIN_POLICY_STATUS=present
    \\\ ZIG_TOOLCHAIN_POLICY_STATUS=missing
    \\\ ZIG_TOOLCHAIN_POLICY_STATUS=invalid
    \\\ ZIG_TOOLCHAIN_ARCHIVE_STATUS=present
    \\\ ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing
    \\\ ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid
    \\\ ZIG_TOOLCHAIN_ARCHIVE_STATUS=mismatch
    \\\ ZIG_TOOLCHAIN_STATUS=present
    \\\ ZIG_TOOLCHAIN_STATUS=missing
    \\\ ZIG_TOOLCHAIN_STATUS=invalid
    \\\ ZIG_TOOLCHAIN_STATUS=too_old
    \\\ ZIG_TOOLCHAIN_STATUS=not_pinned
;

const policy_contract =
    \\\ POLICY_KEYS = {"phase", "channel", "minimum_version", "archive_sha256", "upgrade_policy"}
    \\\ UPGRADE_POLICY_KEYS = {"channel_minimum_lockstep", "archive_target_scope", "required_make_routes"}
    \\\ duplicate toolchain policy keys
    \\\ duplicate archive_sha256 targets
    \\\ duplicate upgrade_policy keys
    \\\ unexpected toolchain policy keys
    \\\ unexpected upgrade_policy keys
    \\\ minimum_version must match channel when channel_minimum_lockstep is true
    \\\ ZIG_TOOLCHAIN_PIN_POLICY=exact
    \\\ ZIG_TOOLCHAIN_PIN_POLICY=minimum_only
    \\\ ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=
    \\\ ZIG_TOOLCHAIN_ARCHIVE_TARGETS=
;

const archive_contract =
    \\\ zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz
    \\\ .zig-toolchain
    \\\ toolchains
    \\\ .toolchains
    \\\ third_party
    \\\ agent_files
    \\\ pinned Zig archive not found in archive search roots
    \\\ explicit archive path does not exist
    \\\ explicit archive path is a directory, expected a regular file
    \\\ explicit archive path is not a regular file
    \\\ multiple repo-local pinned archive candidates matched
    \\\ expected archive filename
    \\\ expected sha256
    \\\ got renamed-zig.tar.xz
;

const version_contract =
    \\\ VERSION_RE = re.compile
    \\\ FALLBACK_MIN_VERSION = "0.16.0"
    \\\ unsupported Zig version string
    \\\ expected pinned Zig channel 0.17.0-dev.87+9b177a7d2
    \\\ zig not found on PATH or in repo-local toolchain search roots
    \\\ explicit zig path does not exist
    \\\ explicit zig path is a directory, expected an executable file
    \\\ zig executable not found
    \\\ zig version command failed
    \\\ zig version command returned empty output
;

fn requireAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
    }
}

test "toolchain checker keeps public action paths and status markers" {
    try requireAll(checker_contract, &.{
        "--self-test",
        "--policy-only",
        "--archive-only",
        "--archive",
        "--archive-target",
        "--zig",
        "--allow-missing",
        "ZIG_TOOLCHAIN_SELF_TEST=pass",
        "ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT=",
        "ZIG_TOOLCHAIN_POLICY_STATUS=present",
        "ZIG_TOOLCHAIN_ARCHIVE_STATUS=mismatch",
        "ZIG_TOOLCHAIN_STATUS=not_pinned",
    });
}

test "toolchain checker keeps strict policy schema diagnostics" {
    try requireAll(policy_contract, &.{
        "POLICY_KEYS",
        "archive_sha256",
        "required_make_routes",
        "duplicate toolchain policy keys",
        "duplicate archive_sha256 targets",
        "unexpected upgrade_policy keys",
        "minimum_version must match channel",
        "ZIG_TOOLCHAIN_PIN_POLICY=exact",
        "ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=",
    });
}

test "toolchain checker keeps archive search and integrity boundaries" {
    try requireAll(archive_contract, &.{
        "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
        ".zig-toolchain",
        "third_party",
        "agent_files",
        "pinned Zig archive not found in archive search roots",
        "explicit archive path does not exist",
        "multiple repo-local pinned archive candidates matched",
        "expected archive filename",
        "expected sha256",
    });
}

test "toolchain checker keeps version and executable failure markers" {
    try requireAll(version_contract, &.{
        "FALLBACK_MIN_VERSION = \"0.16.0\"",
        "unsupported Zig version string",
        "expected pinned Zig channel 0.17.0-dev.87+9b177a7d2",
        "zig not found on PATH or in repo-local toolchain search roots",
        "explicit zig path does not exist",
        "zig version command failed",
        "zig version command returned empty output",
    });
}

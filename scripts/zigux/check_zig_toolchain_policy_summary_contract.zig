const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");
const policy_source = @embedFile("zig-toolchain-policy.json");

const Error = error{
    MissingMarker,
    MarkerOutOfOrder,
    UnexpectedPolicyValue,
};

fn requireContains(source: []const u8, marker: []const u8) Error!void {
    if (std.mem.indexOf(u8, source, marker) == null) {
        return Error.MissingMarker;
    }
}

fn requireOrdered(source: []const u8, markers: []const []const u8) Error!void {
    var offset: usize = 0;
    for (markers) |marker| {
        const next = std.mem.indexOf(u8, source[offset..], marker) orelse return Error.MissingMarker;
        offset += next + marker.len;
    }
}

fn requirePolicyValue(marker: []const u8) Error!void {
    if (std.mem.indexOf(u8, policy_source, marker) == null) {
        return Error.UnexpectedPolicyValue;
    }
}

fn validatePolicySummarySurface(source: []const u8) Error!usize {
    var checks: usize = 0;

    try requireContains(source, "parser.add_argument(\"--policy-only\", action=\"store_true\"");
    checks += 1;

    try requireContains(source, "def emit_policy_summary(policy_path: Path = TOOLCHAIN_POLICY) -> None:");
    checks += 1;

    try requireOrdered(source, &.{
        "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=present\")",
        "print(f\"ZIG_TOOLCHAIN_POLICY_PATH={policy_path}\")",
        "print(f\"ZIG_TOOLCHAIN_PHASE={payload['phase']}\")",
        "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload['channel']}\")",
        "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={payload['minimum_version']}\")",
        "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET_COUNT={len(archive_sha256)}\")",
        "print(\"ZIG_TOOLCHAIN_ARCHIVE_TARGETS=\" + \",\".join(str(target) for target in upgrade_policy[\"archive_target_scope\"]))",
        "print(\"ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=\" + \",\".join(str(route) for route in upgrade_policy[\"required_make_routes\"]))",
        "print(\"ZIG_TOOLCHAIN_PIN_POLICY=\" + (\"exact\" if upgrade_policy[\"channel_minimum_lockstep\"] else \"minimum_only\"))",
    });
    checks += 1;

    try requireOrdered(source, &.{
        "if args.policy_only:",
        "emit_policy_summary()",
        "print(\"ZIG_TOOLCHAIN_POLICY_STATUS=invalid\")",
        "print(f\"ZIG_TOOLCHAIN_POLICY_PATH={TOOLCHAIN_POLICY}\")",
        "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")",
        "return 1",
    });
    checks += 1;

    return checks;
}

fn validatePolicySchemaSurface(source: []const u8) Error!usize {
    var checks: usize = 0;

    try requireContains(source, "POLICY_KEYS = {\"phase\", \"channel\", \"minimum_version\", \"archive_sha256\", \"upgrade_policy\"}");
    checks += 1;

    try requireContains(source, "UPGRADE_POLICY_KEYS = {\"channel_minimum_lockstep\", \"archive_target_scope\", \"required_make_routes\"}");
    checks += 1;

    try requireContains(source, "unexpected toolchain policy keys");
    try requireContains(source, "unexpected upgrade_policy keys");
    checks += 1;

    try requireContains(source, "duplicate upgrade_policy keys");
    try requireContains(source, "duplicate archive_sha256 targets");
    checks += 1;

    try requireContains(source, "archive_target_scope references missing archive_sha256 entries");
    try requireContains(source, "archive_sha256 contains targets outside archive_target_scope");
    checks += 1;

    try requireContains(source, "minimum_version must match channel when channel_minimum_lockstep is true");
    checks += 1;

    return checks;
}

fn validateSelfTestSurface(source: []const u8) Error!usize {
    var checks: usize = 0;

    try requireContains(source, "channel_minimum_lockstep");
    try requireContains(source, "archive_target_scope");
    try requireContains(source, "required_make_routes");
    checks += 1;

    try requireContains(source, "duplicate upgrade_policy keys");
    try requireContains(source, "unexpected upgrade_policy keys");
    try requireContains(source, "duplicate required_make_routes entry");
    checks += 1;

    try requireContains(source, "ZIG_TOOLCHAIN_SELF_TEST=pass");
    try requireContains(source, "ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT=");
    checks += 1;

    return checks;
}

fn validatePinnedPolicyValues() Error!usize {
    var checks: usize = 0;

    try requirePolicyValue("\"phase\": \"Phase 2\"");
    checks += 1;

    try requirePolicyValue("\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try requirePolicyValue("\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    checks += 1;

    try requirePolicyValue("\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    checks += 1;

    try requirePolicyValue("\"channel_minimum_lockstep\": true");
    try requirePolicyValue("\"archive_target_scope\"");
    try requirePolicyValue("\"required_make_routes\"");
    checks += 1;

    try requirePolicyValue("\"phase2-toolchain\"");
    try requirePolicyValue("\"phase2-tools\"");
    try requirePolicyValue("\"phase2-kconfig\"");
    try requirePolicyValue("\"phase2-cross\"");
    try requirePolicyValue("\"phase2-genksyms\"");
    try requirePolicyValue("\"phase2-fixdep\"");
    try requirePolicyValue("\"phase2-validate\"");
    checks += 1;

    return checks;
}

test "policy-only emits complete stable summary keys" {
    try std.testing.expectEqual(@as(usize, 4), try validatePolicySummarySurface(checker_source));
}

test "policy schema rejects drift before summary output" {
    try std.testing.expectEqual(@as(usize, 6), try validatePolicySchemaSurface(checker_source));
}

test "checker self-test keeps policy-only failure cases alive" {
    try std.testing.expectEqual(@as(usize, 3), try validateSelfTestSurface(checker_source));
}

test "pinned policy values match the policy-only summary contract" {
    try std.testing.expectEqual(@as(usize, 5), try validatePinnedPolicyValues());
}

pub fn main(init: std.process.Init) !void {
    var checks: usize = 0;
    checks += try validatePolicySummarySurface(checker_source);
    checks += try validatePolicySchemaSurface(checker_source);
    checks += try validateSelfTestSurface(checker_source);
    checks += try validatePinnedPolicyValues();

    const io = init.io;
    var stdout_buffer: [1024]u8 = undefined;
    var stdout = std.Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout.interface;
    try writer.print("ZIG_TOOLCHAIN_POLICY_SUMMARY_CONTRACT=pass\n", .{});
    try writer.print("ZIG_TOOLCHAIN_POLICY_SUMMARY_CONTRACT_CHECK_COUNT={d}\n", .{checks});
    try writer.flush();
}

const std = @import("std");

const installer_source = @embedFile("install-zig.py");

const ContractError = error{MissingMarker};

fn expectContains(needle: []const u8) !void {
    if (std.mem.indexOf(u8, installer_source, needle) == null) return ContractError.MissingMarker;
}

fn expectOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, installer_source, before) orelse return ContractError.MissingMarker;
    const after_index = std.mem.indexOf(u8, installer_source, after) orelse return ContractError.MissingMarker;
    try std.testing.expect(before_index < after_index);
}

test "install-zig policy loader rejects malformed policy payloads" {
    try expectContains("invalid toolchain policy JSON in {policy_path}: {exc.msg}");
    try expectContains("invalid toolchain policy payload in {policy_path}: expected object");

    try expectOrdered("def load_policy(", "invalid toolchain policy JSON in {policy_path}: {exc.msg}");
    try expectOrdered("invalid toolchain policy JSON in {policy_path}: {exc.msg}", "invalid toolchain policy payload in {policy_path}: expected object");
}

test "install-zig policy channel fallback remains policy-first" {
    try expectContains("FALLBACK_CHANNEL = 'master'");
    try expectContains("def load_policy_channel(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_CHANNEL) -> str:");
    try expectContains("if payload is None:\n        return fallback");
    try expectContains("channel = payload.get('channel')");
    try expectContains("invalid channel in {policy_path}");
    try expectContains("return channel.strip()");

    try expectOrdered("policy_channel = load_policy_channel()", "channel = args.channel or policy_channel");
}

test "install-zig archive digest loader validates policy shape" {
    try expectContains("def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:");
    try expectContains("if not isinstance(archive_sha256, dict):");
    try expectContains("digest = archive_sha256.get(target_key)");
    try expectContains("if digest is None:\n        return None");
    try expectContains("ARCHIVE_SHA256_RE.fullmatch(digest.lower())");
    try expectContains("invalid archive sha256 for {target_key} in {policy_path}");
    try expectContains("return digest.lower()");

    try expectOrdered("def load_policy_archive_sha256", "invalid archive sha256 for {target_key} in {policy_path}");
    try expectOrdered("ARCHIVE_SHA256_RE.fullmatch(digest.lower())", "return digest.lower()");
}

test "install-zig main path emits pinned archive digest only for policy channel" {
    try expectContains("expected_archive_sha256 = None");
    try expectContains("if channel == policy_channel:\n        expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)");
    try expectContains("ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}");
    try expectContains("ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified");
    try expectContains("ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified");

    try expectOrdered("expected_archive_sha256 = None", "if channel == policy_channel:");
    try expectOrdered("if expected_archive_sha256 is not None:", "ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}");
    try expectOrdered("ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}", "if args.resolve_only:");
}

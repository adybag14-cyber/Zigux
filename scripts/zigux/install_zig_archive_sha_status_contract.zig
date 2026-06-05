const std = @import("std");

const installer_path = "scripts/zigux/install-zig.py";

fn readInstaller(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        installer_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOrder(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(source: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = source;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "install-zig archive sha status stays tied to policy digest checks" {
    const source = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "ARCHIVE_SHA256_RE = re.compile(r'^[0-9a-f]{64}$')");
    try requireContains(source, "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:");
    try requireContains(source, "digest = archive_sha256.get(target_key)");
    try requireContains(source, "not isinstance(digest, str) or not ARCHIVE_SHA256_RE.fullmatch(digest.lower())");
    try requireContains(source, "return digest.lower()");
    try requireContains(source, "def verify_archive_sha256(path: Path, expected_sha256: str) -> str:");
    try requireContains(source, "actual_sha256.lower() != expected_sha256.lower()");
    try requireContains(source, "zig archive sha256 mismatch for");

    try requireOrder(source, "expected_archive_sha256 = None", "if channel == policy_channel:");
    try requireOrder(
        source,
        "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
        "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
    );
    try requireOrder(
        source,
        "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
        "if args.resolve_only:",
    );
}

test "install-zig archive status prints verified only after verification" {
    const source = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "if expected_archive_sha256 is not None:");
    try requireContains(source, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try requireContains(source, "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')");
    try requireContains(source, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')");
    try requireContains(source, "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')");

    try requireOrder(
        source,
        "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
    );
    try requireOrder(
        source,
        "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    );
    try requireOrder(
        source,
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
        "print('ZIG_INSTALL_STATUS=pass')",
    );
    try requireOrder(
        source,
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
        "print('ZIG_INSTALL_STATUS=pass')",
    );
}

test "install-zig local archive override remains fail closed when live surface is present" {
    const source = try readInstaller(std.testing.allocator);
    defer std.testing.allocator.free(source);

    if (std.mem.indexOf(u8, source, "parser.add_argument('--archive'") == null) {
        return;
    }

    try requireContains(source, "parser.add_argument('--archive', help='Use a local Zig archive instead of downloading from the resolved URL.')");
    try requireContains(source, "parser.add_argument('--archive-target', help='Archive target key from scripts/zigux/zig-toolchain-policy.json when using --archive.')");
    try requireContains(source, "archive_target_key = args.archive_target or target_key");
    try requireContains(source, "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:");
    try requireContains(source, "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)");
    try requireContains(source, "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:");
    try requireContains(source, "no pinned archive sha256 for target {archive_target_key}");
    try requireContains(source, "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')");

    try requireOrder(
        source,
        "archive_target_key = args.archive_target or target_key",
        "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)",
    );
    try requireOrder(
        source,
        "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:",
        "print(f'ZIG_INSTALL_CHANNEL={channel}')",
    );
    try std.testing.expect(countOccurrences(source, "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified") == 1);
    try std.testing.expect(countOccurrences(source, "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified") == 1);
}

const std = @import("std");

const checker_source = @embedFile("check-lane05-install-zig-archive-verification.py");

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
};

const install_markers = [_][]const u8{
    "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "copy_url_to_file(tarball_url, archive_path)",
    "if expected_archive_sha256 is not None:",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
    "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
    "shutil.copytree(extracted_root, final_root)",
};

const exact_count_markers = [_][]const u8{
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
};

const selftest_markers = [_][]const u8{
    "expected_case_count = 8",
    "assert collect_issues(root) == []",
    "(\"MISSING_INSTALL_MARKER\",",
    "(\"DUPLICATE_INSTALL_MARKER\",",
    "any(code == \"ORDER_MISMATCH\" for code, _ in collect_issues(root))",
    "(\"INVALID_POLICY_FIELD\", \"archive_sha256\")",
    "(\"UNEXPECTED_ARCHIVE_TARGET_COUNT\", \"2\")",
    "(\"INVALID_ARCHIVE_SHA256\", \"x86_64-linux\")",
    "required file missing",
    "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass",
    "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST_CASE_COUNT",
};

const output_markers = [_][]const u8{
    "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass",
    "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_MARKER_COUNT",
    "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_TARGET_COUNT=1",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn requirePresent(source: []const u8, marker: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, source, marker) == null) return ContractError.MissingMarker;
}

fn requireExactlyOnce(source: []const u8, marker: []const u8) ContractError!void {
    const count = countOccurrences(source, marker);
    if (count == 0) return ContractError.MissingMarker;
    if (count != 1) return ContractError.DuplicateMarker;
}

fn checkInstallZigArchiveVerificationChecker(source: []const u8) ContractError!void {
    for (install_markers) |marker| try requirePresent(source, marker);
    for (exact_count_markers) |marker| try requirePresent(source, marker);
    for (selftest_markers) |marker| try requirePresent(source, marker);
    for (output_markers) |marker| try requireExactlyOnce(source, marker);
}

pub fn main() !void {
    try checkInstallZigArchiveVerificationChecker(checker_source);
    std.debug.print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_CHECKER_CONTRACT=pass\n", .{});
    std.debug.print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_CHECKER_MARKER_COUNT={d}\n", .{
        install_markers.len + selftest_markers.len + output_markers.len,
    });
}

test "current checker keeps archive verification source contract" {
    try checkInstallZigArchiveVerificationChecker(checker_source);
}

test "missing archive verification marker fails closed" {
    const broken = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        checker_source,
        "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        "actual_archive_sha256 = expected_archive_sha256",
    ) catch unreachable;
    defer std.testing.allocator.free(broken);

    try std.testing.expectError(ContractError.MissingMarker, checkInstallZigArchiveVerificationChecker(broken));
}

test "duplicated status marker fails closed" {
    const duplicate_marker = "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_TARGET_COUNT=1";
    const broken = std.mem.concat(std.testing.allocator, u8, &.{ checker_source, "\n", duplicate_marker, "\n" }) catch unreachable;
    defer std.testing.allocator.free(broken);

    try std.testing.expectError(ContractError.DuplicateMarker, checkInstallZigArchiveVerificationChecker(broken));
}

test "ordering negative case coverage is required" {
    const broken = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        checker_source,
        "any(code == \"ORDER_MISMATCH\" for code, _ in collect_issues(root))",
        "any(code == \"ORDER_OK\" for code, _ in collect_issues(root))",
    ) catch unreachable;
    defer std.testing.allocator.free(broken);

    try std.testing.expectError(ContractError.MissingMarker, checkInstallZigArchiveVerificationChecker(broken));
}

test "selftest policy issue coverage is required" {
    const broken = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        checker_source,
        "(\"INVALID_ARCHIVE_SHA256\", \"x86_64-linux\")",
        "(\"INVALID_ARCHIVE_DIGEST\", \"x86_64-linux\")",
    ) catch unreachable;
    defer std.testing.allocator.free(broken);

    try std.testing.expectError(ContractError.MissingMarker, checkInstallZigArchiveVerificationChecker(broken));
}

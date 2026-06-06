const std = @import("std");

const checker_source = @embedFile("check-lane05-local-archive-readme.py");

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
};

const policy_markers = [_][]const u8{
    "README_PATH = Path(\"third_party/README.md\")",
    "POLICY_PATH = Path(\"scripts/zigux/zig-toolchain-policy.json\")",
    "ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(",
    "EXPECTED_ARCHIVE_SIZES = {",
    "\"x86_64-linux\": 59_410_844,",
    "def load_policy(root: Path) -> dict[str, object]:",
    "def require_string(payload: dict[str, object], key: str) -> str:",
    "def require_string_map(payload: dict[str, object], key: str) -> dict[str, str]:",
    "def require_string_list(payload: dict[str, object], key: str) -> list[str]:",
    "f\"zig-{target}-{channel}.tar.xz\"",
    "def duplicate_archive_name(expected_filename: str) -> str:",
    "def compute_sha256(path: Path) -> str:",
};

const readme_markers = [_][]const u8{
    "\"# Zigux third-party archives\"",
    "\"Lane 05 bootstrap CI\"",
    "f\"`{expected_path}`\"",
    "f\"`{expected_parts_path}`\"",
    "f\"`{expected_sha}`\"",
    "f\"`{expected_size}` bytes\"",
    "f\"`{validation_command}`\"",
    "\"`community-mirrors.txt`\"",
    "\"`scripts/zigux/check-lane05-local-first-archive-workflow.py`\"",
    "\"`scripts/zigux/check-lane05-local-archive-readme.py`\"",
    "\"`scripts/zigux/check-lane05-install-zig-archive-verification.py`\"",
    "\"`scripts/zigux/stage-pinned-zig-archive.py`\"",
    "\"`scripts/zigux/check-lane05-stage-helper-contract.py`\"",
    "\"`scripts/zigux/check-lane05-stage-helper-selftest.py`\"",
    "f\"`{duplicate_archive_name(expected_filename)}`\"",
    "f\"`{POLICY_PATH}`\"",
};

const archive_validation_markers = [_][]const u8{
    "for path in (root / \"third_party\").glob(\"*.tar.xz\")",
    "if ARCHIVE_DUPLICATE_SUFFIX_RE.fullmatch(path.name) is not None",
    "payload_status = \"missing_allowed\"",
    "if archive_path.exists():",
    "if not archive_path.is_file():",
    "actual_size = archive_path.stat().st_size",
    "if actual_size != expected_size:",
    "actual_sha = compute_sha256(archive_path)",
    "if actual_sha != expected_sha:",
    "payload_status = \"present\"",
};

const selftest_markers = [_][]const u8{
    "expect_pass()",
    "\"missing required markers\"",
    "\"to be 59410844 bytes, got 1\"",
    "\"duplicate-suffix archive copies\"",
    "\"to have sha256 0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"",
    "LANE05_LOCAL_ARCHIVE_README_SELF_TEST=pass",
    "LANE05_LOCAL_ARCHIVE_README_SELF_TEST_CASE_COUNT",
};

const exact_output_markers = [_][]const u8{
    "LANE05_LOCAL_ARCHIVE_README=fail",
    "LANE05_LOCAL_ARCHIVE_README=pass",
    "LANE05_LOCAL_ARCHIVE_TARGET=",
    "LANE05_LOCAL_ARCHIVE_README_MARKER_COUNT=",
    "LANE05_LOCAL_ARCHIVE_PAYLOAD_STATUS=",
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

fn checkLocalArchiveReadmeChecker(source: []const u8) ContractError!void {
    for (policy_markers) |marker| try requirePresent(source, marker);
    for (readme_markers) |marker| try requirePresent(source, marker);
    for (archive_validation_markers) |marker| try requirePresent(source, marker);
    for (selftest_markers) |marker| try requirePresent(source, marker);
    for (exact_output_markers) |marker| try requireExactlyOnce(source, marker);
}

pub fn main() !void {
    try checkLocalArchiveReadmeChecker(checker_source);
    std.debug.print("LANE05_LOCAL_ARCHIVE_README_CHECKER_CONTRACT=pass\n", .{});
    std.debug.print("LANE05_LOCAL_ARCHIVE_README_CHECKER_MARKER_COUNT={d}\n", .{
        policy_markers.len + readme_markers.len + archive_validation_markers.len + selftest_markers.len + exact_output_markers.len,
    });
}

test "current checker keeps local archive README source contract" {
    try checkLocalArchiveReadmeChecker(checker_source);
}

test "missing policy marker fails closed" {
    const broken = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        checker_source,
        "POLICY_PATH = Path(\"scripts/zigux/zig-toolchain-policy.json\")",
        "POLICY_PATH = Path(\"scripts/zigux/zig-toolchain.json\")",
    ) catch unreachable;
    defer std.testing.allocator.free(broken);

    try std.testing.expectError(ContractError.MissingMarker, checkLocalArchiveReadmeChecker(broken));
}

test "missing README marker fails closed" {
    const broken = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        checker_source,
        "\"`scripts/zigux/check-lane05-install-zig-archive-verification.py`\"",
        "\"`scripts/zigux/check-lane05-install-zig.py`\"",
    ) catch unreachable;
    defer std.testing.allocator.free(broken);

    try std.testing.expectError(ContractError.MissingMarker, checkLocalArchiveReadmeChecker(broken));
}

test "missing payload status branch fails closed" {
    const broken = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        checker_source,
        "payload_status = \"missing_allowed\"",
        "payload_status = \"missing\"",
    ) catch unreachable;
    defer std.testing.allocator.free(broken);

    try std.testing.expectError(ContractError.MissingMarker, checkLocalArchiveReadmeChecker(broken));
}

test "duplicated pass output marker fails closed" {
    const duplicate_marker = "LANE05_LOCAL_ARCHIVE_README=pass";
    const broken = std.mem.concat(std.testing.allocator, u8, &.{ checker_source, "\n", duplicate_marker, "\n" }) catch unreachable;
    defer std.testing.allocator.free(broken);

    try std.testing.expectError(ContractError.DuplicateMarker, checkLocalArchiveReadmeChecker(broken));
}

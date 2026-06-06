const std = @import("std");
const testing = std.testing;

const checker_source = @embedFile("check-lane05-stage-helper-contract.py");

fn requireContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn requireOrder(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, checker_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, checker_source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "checker derives the pinned archive contract from policy" {
    try requireContains("STAGE_HELPER_PATH = Path(\"scripts/zigux/stage-pinned-zig-archive.py\")");
    try requireContains("TOOLCHAIN_POLICY_PATH = Path(\"scripts/zigux/zig-toolchain-policy.json\")");
    try requireContains("README_PATH = Path(\"third_party/README.md\")");
    try requireContains("EXPECTED_ARCHIVE_SIZES = {");
    try requireContains("\"x86_64-linux\": 59_410_844,");

    try requireContains("def resolve_contract(root: Path) -> dict[str, object]:");
    try requireContains("channel = require_string(payload, \"channel\")");
    try requireContains("archives = require_string_map(payload, \"archive_sha256\")");
    try requireContains("targets = require_string_list(upgrade_policy, \"archive_target_scope\")");
    try requireContains("if len(targets) != 1:");
    try requireContains("archive_target_scope target {target} missing from archive_sha256");
    try requireContains("filename = f\"zig-{target}-{channel}.tar.xz\"");
    try requireContains("\"duplicate_name\": f\"{filename[:-len('.tar.xz')]} (1).tar.xz\"");
    try requireContains("\"archive_path\": f\"third_party/{filename}\"");

    try requireOrder("channel = require_string(payload, \"channel\")", "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try requireOrder("targets = require_string_list(upgrade_policy, \"archive_target_scope\")", "target = targets[0]");
}

test "checker pins staged helper marker roster and output order" {
    try requireContains("def check_stage_helper(root: Path, contract: dict[str, object]) -> int:");
    try requireContains("helper_markers = [");
    try requireContains("'TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")'");
    try requireContains("'THIRD_PARTY_DIR = Path(\"third_party\")'");
    try requireContains("'ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile('");
    try requireContains("'duplicate_archive_name('");
    try requireContains("'archive_name_has_duplicate_suffix('");
    try requireContains("'duplicate-suffix archive copies'");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE=pass'");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE=fail'");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_TARGET='");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_FILENAME='");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE='");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256='");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256='");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_DESTINATION='");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_STATUS='");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass'");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT='");
    try requireContains("assert check_stage_helper(root, contract) == 19");

    try requireContains("require_order(");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_TARGET='");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_FILENAME='");
    try requireContains("\"stage helper output order\"");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_DESTINATION='");
    try requireContains("'STAGE_PINNED_ZIG_ARCHIVE_STATUS='");
}

test "checker ties README markers to the same policy packet" {
    try requireContains("def check_readme(root: Path, contract: dict[str, object]) -> int:");
    try requireContains("\"# Zigux third-party archives\"");
    try requireContains("f\"`{contract['target']}`\"");
    try requireContains("f\"`{contract['channel']}`\"");
    try requireContains("f\"`{contract['archive_path']}`\"");
    try requireContains("f\"`{contract['sha256']}`\"");
    try requireContains("f\"`{contract['size']}` bytes\"");
    try requireContains("f\"`{contract['duplicate_name']}`\"");
    try requireContains("assert check_readme(root, contract) == 7");

    try requireContains("\"- target: `x86_64-linux`\"");
    try requireContains("\"- channel: `0.17.0-dev.758+748e7c5e3`\"");
    try requireContains("\"- file: `third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz`\"");
    try requireContains("\"- sha256: `0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6`\"");
    try requireContains("\"- size: `59410844` bytes\"");
    try requireContains("\"- duplicate: `zig-x86_64-linux-0.17.0-dev.758+748e7c5e3 (1).tar.xz`\"");
}

test "checker self-test covers pass and drift failures" {
    try requireContains("def run_self_test() -> int:");
    try requireContains("with tempfile.TemporaryDirectory(prefix=\"lane05_stage_helper_contract_\") as tmp_dir:");
    try requireContains("def expect_failure(mutator, expected_substring: str) -> None:");
    try requireContains("\"missing stage helper marker\"");
    try requireContains("\"missing README marker\"");
    try requireContains("\"expected exactly one archive target\"");
    try requireContains("\"output order\"");
    try requireContains("`59410844` bytes");
    try requireContains("`1` bytes");
    try requireContains("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass");
    try requireContains("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST_CASE_COUNT=");

    try requireContains("LANE05_STAGE_HELPER_CONTRACT=pass");
    try requireContains("LANE05_STAGE_HELPER_CONTRACT=fail");
    try requireContains("LANE05_STAGE_HELPER_CONTRACT_TARGET=");
    try requireContains("LANE05_STAGE_HELPER_CONTRACT_FILENAME=");
    try requireContains("LANE05_STAGE_HELPER_CONTRACT_SHA256=");
    try requireContains("LANE05_STAGE_HELPER_CONTRACT_SIZE=");
    try requireContains("LANE05_STAGE_HELPER_MARKER_COUNT=");
    try requireContains("LANE05_STAGE_HELPER_README_MARKER_COUNT=");
}

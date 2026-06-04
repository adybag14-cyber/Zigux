const std = @import("std");

const validator_path = "scripts/zigux/validate-phase2.py";
const direct_cross_checker_path = "scripts/zigux/check-phase2-cross.py";
const cross_targets_path = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireInOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse {
        std.debug.panic("missing marker before order check: {s}", .{before});
    };
    const after_index = std.mem.indexOf(u8, haystack, after) orelse {
        std.debug.panic("missing marker after order check: {s}", .{after});
    };
    try std.testing.expect(before_index < after_index);
}

test "aggregate validator keeps direct cross public output envelope" {
    const validator_text = try readRepoFile(validator_path);
    defer std.testing.allocator.free(validator_text);

    try requireContains(validator_text, "PHASE2_VALIDATION=pass");
    try requireContains(validator_text, "PHASE2_VALIDATION=fail");
    try requireContains(validator_text, "PHASE2_VALIDATION_WORKFLOW_LINE_COUNT=");
    try requireContains(validator_text, "PHASE2_VALIDATION_REQUIRED_PATH_COUNT=");
    try requireContains(validator_text, "PHASE2_VALIDATION_SELF_TEST=pass");
    try requireContains(validator_text, "PHASE2_VALIDATION_SELF_TEST_CASE_COUNT=");
}

test "aggregate validator keeps cross matrix files in required path roster" {
    const validator_text = try readRepoFile(validator_path);
    defer std.testing.allocator.free(validator_text);

    try requireContains(validator_text, "\"scripts/zigux/check-phase2-cross.py\"");
    try requireContains(validator_text, "\"scripts/zigux/check-phase2-cross-selftest-alignment.py\"");
    try requireContains(validator_text, "\"zigux/tests/fixtures/phase2_cross_targets.json\"");
    try requireContains(validator_text, "\"scripts/zigux/zig-toolchain-policy.json\"");
    try requireContains(validator_text, "ARCHIVE_SUPPORT_ALTERNATIVES");
}

test "aggregate validator groups cross-relevant failures with stable issue codes" {
    const validator_text = try readRepoFile(validator_path);
    defer std.testing.allocator.free(validator_text);

    try requireContains(validator_text, "MISSING_REQUIRED_PATH");
    try requireContains(validator_text, "MISSING_REQUIRED_ARCHIVE_SUPPORT");
    try requireContains(validator_text, "MISSING_WORKFLOW_LINE");
    try requireContains(validator_text, "DUPLICATE_WORKFLOW_LINE");
    try requireContains(validator_text, "MISSING_MAKEFILE_LINE");
    try requireContains(validator_text, "DUPLICATE_MAKEFILE_LINE");
    try requireContains(validator_text, "{code}_START");
    try requireContains(validator_text, "{code}_END");
}

test "aggregate validator routes direct cross before later Phase 2 closure checks" {
    const validator_text = try readRepoFile(validator_path);
    defer std.testing.allocator.free(validator_text);

    try requireInOrder(
        validator_text,
        "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
        "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    );
    try requireInOrder(
        validator_text,
        "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    );
    try requireInOrder(
        validator_text,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    );
}

test "direct checker and fixture still expose aggregate counts" {
    const direct_cross_checker_text = try readRepoFile(direct_cross_checker_path);
    defer std.testing.allocator.free(direct_cross_checker_text);
    const cross_targets_text = try readRepoFile(cross_targets_path);
    defer std.testing.allocator.free(cross_targets_text);

    try requireContains(direct_cross_checker_text, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try requireContains(direct_cross_checker_text, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try requireContains(direct_cross_checker_text, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
    try requireContains(cross_targets_text, "\"target\": \"x86_64-linux\"");
    try requireContains(cross_targets_text, "\"target\": \"aarch64-linux\"");
    try requireContains(cross_targets_text, "\"validation_mode\": \"archive_required\"");
    try requireContains(cross_targets_text, "\"validation_mode\": \"route_contract_only\"");
}

const std = @import("std");

const checker_path = "scripts/zigux/check-phase2-cross.py";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

const pass_label = "PHASE2_DIRECT_CROSS_ROUTE=pass";
const fail_label = "PHASE2_DIRECT_CROSS_ROUTE=fail";
const target_count_label = "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=";
const archive_scope_count_label = "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=";
const self_test_case_count = "EXPECTED_SELF_TEST_CASE_COUNT = 17";
const self_test_label = "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass";
const archive_scope_mismatch = "ARCHIVE_SCOPE_MISMATCH";
const archive_required_mismatch = "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH";
const duplicate_target = "DUPLICATE_CROSS_TARGET";
const expected_route = "make -C zigux phase2-cross";
const archive_target = "\"target\": \"x86_64-linux\"";
const route_contract_target = "\"target\": \"aarch64-linux\"";
const archive_required_mode = "\"validation_mode\": \"archive_required\"";
const route_contract_mode = "\"validation_mode\": \"route_contract_only\"";

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    OutOfOrder,
    UnexpectedMarker,
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024)) catch |err| switch (err) {
        error.FileNotFound => blk: {
            const fallback = try std.mem.concat(allocator, u8, &.{ "../../", path });
            defer allocator.free(fallback);
            break :blk try std.Io.Dir.cwd().readFileAlloc(std.testing.io, fallback, allocator, .limited(1024 * 1024));
        },
        else => return err,
    };
}

fn countNeedle(text: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, text, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

fn requireOnce(text: []const u8, needle: []const u8) !usize {
    const count = countNeedle(text, needle);
    if (count == 0) return ContractError.MissingMarker;
    if (count != 1) return ContractError.DuplicateMarker;
    return std.mem.indexOf(u8, text, needle).?;
}

fn requirePresent(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) == null) return ContractError.MissingMarker;
}

fn requireAbsent(text: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, text, needle) != null) return ContractError.UnexpectedMarker;
}

fn requireBefore(text: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = try requireOnce(text, before);
    const after_index = try requireOnce(text, after);
    if (before_index >= after_index) return ContractError.OutOfOrder;
}

fn validateCheckerSummarySurface(text: []const u8) !void {
    _ = try requireOnce(text, pass_label);
    _ = try requireOnce(text, fail_label);
    _ = try requireOnce(text, target_count_label);
    _ = try requireOnce(text, archive_scope_count_label);
    _ = try requireOnce(text, self_test_label);
    _ = try requireOnce(text, self_test_case_count);
    try requirePresent(text, archive_scope_mismatch);
    try requirePresent(text, archive_required_mismatch);
    try requirePresent(text, duplicate_target);
    try requireBefore(text, pass_label, target_count_label);
    try requireBefore(text, target_count_label, archive_scope_count_label);
}

fn validateFixtureBoundary(text: []const u8) !void {
    try requirePresent(text, "\"phase\": \"Phase 2\"");
    try requirePresent(text, "\"status\": \"active\"");
    try requirePresent(text, expected_route);
    try requirePresent(text, archive_target);
    try requirePresent(text, route_contract_target);
    try requirePresent(text, archive_required_mode);
    try requirePresent(text, route_contract_mode);
    try requireBefore(text, archive_target, route_contract_target);
    try requireAbsent(text, "\"target\": \"riscv64-linux\"");
}

test "direct cross checker keeps stable pass summary and count labels" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try validateCheckerSummarySurface(checker);
}

test "direct cross fixture keeps archive-backed and route-contract targets explicit" {
    const allocator = std.testing.allocator;
    const fixture = try readRepoFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try validateFixtureBoundary(fixture);
}

test "contract catches summary drift, duplicate labels, and target widening" {
    const good_checker =
        \\print("PHASE2_DIRECT_CROSS_ROUTE=fail")
        \\ARCHIVE_SCOPE_MISMATCH
        \\ARCHIVE_REQUIRED_TARGET_SET_MISMATCH
        \\DUPLICATE_CROSS_TARGET
        \\EXPECTED_SELF_TEST_CASE_COUNT = 17
        \\print("PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass")
        \\print("PHASE2_DIRECT_CROSS_ROUTE=pass")
        \\print(f"PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}")
        \\print(f"PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}")
    ;
    try validateCheckerSummarySurface(good_checker);

    const duplicate_target_label = good_checker ++ "\nprint(\"PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=2\")\n";
    try std.testing.expectError(ContractError.DuplicateMarker, validateCheckerSummarySurface(duplicate_target_label));

    const missing_mismatch = std.mem.replacementSize(u8, good_checker, archive_scope_mismatch, "");
    var buffer: [512]u8 = undefined;
    try std.testing.expect(missing_mismatch < buffer.len);
    _ = std.mem.replace(u8, good_checker, archive_scope_mismatch, "", &buffer);
    try std.testing.expectError(ContractError.MissingMarker, validateCheckerSummarySurface(buffer[0..missing_mismatch]));

    const bad_order =
        \\print("PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=2")
        \\print("PHASE2_DIRECT_CROSS_ROUTE=pass")
        \\print("PHASE2_DIRECT_CROSS_ROUTE=fail")
        \\print("PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=1")
        \\print("PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass")
        \\EXPECTED_SELF_TEST_CASE_COUNT = 17
        \\ARCHIVE_SCOPE_MISMATCH
        \\ARCHIVE_REQUIRED_TARGET_SET_MISMATCH
        \\DUPLICATE_CROSS_TARGET
    ;
    try std.testing.expectError(ContractError.OutOfOrder, validateCheckerSummarySurface(bad_order));

    const widened_fixture =
        \\"phase": "Phase 2",
        \\"status": "active",
        \\make -C zigux phase2-cross
        \\"target": "x86_64-linux"
        \\"validation_mode": "archive_required"
        \\"target": "aarch64-linux"
        \\"validation_mode": "route_contract_only"
        \\"target": "riscv64-linux"
    ;
    try std.testing.expectError(ContractError.UnexpectedMarker, validateFixtureBoundary(widened_fixture));
}

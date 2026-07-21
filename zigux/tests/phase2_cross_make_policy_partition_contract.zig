const std = @import("std");

const makefile_path = "zigux/Makefile";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

const make_phase2_cross_rule = "phase2-cross:";
const make_phase2_genksyms_rule = "phase2-genksyms:";
const make_cross_self_test = "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig -- --self-test\n";
const make_cross_check = "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig\n";
const make_alignment_self_test = "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig -- --self-test\n";
const make_alignment_check = "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig\n";

const phase2_cross_route = "\"phase2-cross\"";
const fixture_route = "\"route\": \"make -C zigux phase2-cross\"";
const archive_target_scope = "\"archive_target_scope\"";
const archive_sha256 = "\"archive_sha256\"";
const x86_target = "\"x86_64-linux\"";
const aarch64_target = "\"aarch64-linux\"";
const archive_required = "\"validation_mode\": \"archive_required\"";
const route_contract_only = "\"validation_mode\": \"route_contract_only\"";
const pinned_bootstrap_archive = "\"review_status\": \"pinned bootstrap archive\"";
const route_contract_review = "\"review_status\": \"route contract only\"";

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    OutOfOrder,
    UnexpectedMarker,
    UnexpectedCount,
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

fn countOccurrences(text: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, text[cursor..], marker)) |relative| {
        count += 1;
        cursor += relative + marker.len;
    }
    return count;
}

fn requireContainsOnce(text: []const u8, marker: []const u8) !usize {
    var count: usize = 0;
    var found_index: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, text[cursor..], marker)) |relative| {
        count += 1;
        found_index = cursor + relative;
        cursor += relative + marker.len;
    }

    if (count == 0) return ContractError.MissingMarker;
    if (count != 1) return ContractError.DuplicateMarker;
    return found_index;
}

fn requireBefore(text: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = try requireContainsOnce(text, before);
    const after_index = try requireContainsOnce(text, after);
    if (before_index >= after_index) return ContractError.OutOfOrder;
}

fn requireAbsent(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) != null) return ContractError.UnexpectedMarker;
}

fn requireCount(text: []const u8, marker: []const u8, expected: usize) !void {
    if (countOccurrences(text, marker) != expected) return ContractError.UnexpectedCount;
}

fn phase2CrossBlock(text: []const u8) ![]const u8 {
    const start = try requireContainsOnce(text, make_phase2_cross_rule);
    const end = try requireContainsOnce(text, make_phase2_genksyms_rule);
    if (start >= end) return ContractError.OutOfOrder;
    return text[start..end];
}

fn validateMakefilePartition(text: []const u8) !void {
    try requireBefore(text, make_phase2_cross_rule, make_cross_self_test);
    try requireBefore(text, make_cross_self_test, make_cross_check);
    try requireBefore(text, make_cross_check, make_alignment_self_test);
    try requireBefore(text, make_alignment_self_test, make_alignment_check);
    try requireBefore(text, make_alignment_check, make_phase2_genksyms_rule);

    const block = try phase2CrossBlock(text);
    try requireAbsent(block, "phase2-cross: phase2-toolchain");
    try requireAbsent(block, archive_target_scope);
    try requireAbsent(block, archive_sha256);
    try requireAbsent(block, "\"validation_mode\"");
    try requireAbsent(block, "route_contract_only");
    try requireAbsent(block, "archive_required");
    try requireAbsent(block, "x86_64-linux");
    try requireAbsent(block, "aarch64-linux");
}

fn validatePolicyPartition(text: []const u8) !void {
    _ = try requireContainsOnce(text, archive_sha256);
    _ = try requireContainsOnce(text, archive_target_scope);
    try requireCount(text, x86_target, 2);
    _ = try requireContainsOnce(text, phase2_cross_route);
    try requireBefore(text, "\"phase2-kconfig\"", phase2_cross_route);
    try requireBefore(text, phase2_cross_route, "\"phase2-genksyms\"");

    try requireAbsent(text, aarch64_target);
    try requireAbsent(text, archive_required);
    try requireAbsent(text, route_contract_only);
    try requireAbsent(text, fixture_route);
}

fn validateFixturePartition(text: []const u8) !void {
    _ = try requireContainsOnce(text, archive_target_scope);
    try requireCount(text, x86_target, 2);
    _ = try requireContainsOnce(text, aarch64_target);
    _ = try requireContainsOnce(text, archive_required);
    _ = try requireContainsOnce(text, route_contract_only);
    _ = try requireContainsOnce(text, pinned_bootstrap_archive);
    _ = try requireContainsOnce(text, route_contract_review);
    try requireCount(text, "\"target\":", 2);
    try requireCount(text, fixture_route, 3);
    try requireBefore(text, pinned_bootstrap_archive, archive_required);
    try requireBefore(text, route_contract_review, route_contract_only);

    try requireAbsent(text, archive_sha256);
    try requireAbsent(text, "\"required_make_routes\"");
}

test "phase2-cross makefile route stays checker-only and target-agnostic" {
    const allocator = std.testing.allocator;
    const makefile = try readRepoFile(allocator, makefile_path);
    defer allocator.free(makefile);

    try validateMakefilePartition(makefile);
}

test "toolchain policy owns required route and archive scope only" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);

    try validatePolicyPartition(policy);
}

test "cross fixture owns the concrete two-target matrix partition" {
    const allocator = std.testing.allocator;
    const fixture = try readRepoFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try validateFixturePartition(fixture);
}

test "contract rejects partition drift across makefile policy and fixture surfaces" {
    const good_makefile =
        "phase2-cross:\n" ++
        "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig -- --self-test\n" ++
        "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig\n" ++
        "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig -- --self-test\n" ++
        "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig\n\n" ++
        "phase2-genksyms:\n";
    try validateMakefilePartition(good_makefile);
    const makefile_with_target_in_block =
        "phase2-cross:\n" ++
        "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig -- --self-test\n" ++
        "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig\n" ++
        "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig -- --self-test\n" ++
        "\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig\n" ++
        "\t# x86_64-linux\n\n" ++
        "phase2-genksyms:\n";
    try std.testing.expectError(ContractError.UnexpectedMarker, validateMakefilePartition(makefile_with_target_in_block));

    const good_policy =
        "{\"archive_sha256\":{\"x86_64-linux\":\"digest\"},\"upgrade_policy\":{\"archive_target_scope\":[\"x86_64-linux\"],\"required_make_routes\":[\"phase2-kconfig\",\"phase2-cross\",\"phase2-genksyms\"]}}";
    try validatePolicyPartition(good_policy);
    try std.testing.expectError(ContractError.UnexpectedMarker, validatePolicyPartition(good_policy ++ "\n\"aarch64-linux\"\n"));

    const good_fixture =
        "{\"archive_target_scope\":[\"x86_64-linux\"],\"route\": \"make -C zigux phase2-cross\",\"cross_targets\":[{\"target\":\"x86_64-linux\",\"review_status\": \"pinned bootstrap archive\",\"validation_mode\": \"archive_required\",\"route\": \"make -C zigux phase2-cross\"},{\"target\":\"aarch64-linux\",\"review_status\": \"route contract only\",\"validation_mode\": \"route_contract_only\",\"route\": \"make -C zigux phase2-cross\"}]}";
    try validateFixturePartition(good_fixture);
    try std.testing.expectError(ContractError.UnexpectedMarker, validateFixturePartition(good_fixture ++ "\n\"archive_sha256\"\n"));
}

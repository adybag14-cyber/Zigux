const std = @import("std");
const testing = std.testing;

const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";
const checker_path = "scripts/zigux/check-phase2-cross.py";

const ContractError = error{
    MissingMarker,
    UnexpectedMarker,
    WrongValidationMode,
};

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, testing.allocator, .limited(1024 * 1024));
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (!contains(haystack, needle)) return ContractError.MissingMarker;
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    if (contains(haystack, needle)) return ContractError.UnexpectedMarker;
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return ContractError.MissingMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return ContractError.MissingMarker;
    try testing.expect(first_index < second_index);
}

fn expectTargetMode(fixture: []const u8, target: []const u8, mode: []const u8) !void {
    const target_marker = try std.fmt.allocPrint(testing.allocator, "\"target\": \"{s}\"", .{target});
    defer testing.allocator.free(target_marker);

    const mode_marker = try std.fmt.allocPrint(testing.allocator, "\"validation_mode\": \"{s}\"", .{mode});
    defer testing.allocator.free(mode_marker);

    const target_index = std.mem.indexOf(u8, fixture, target_marker) orelse return ContractError.MissingMarker;
    const mode_index = std.mem.indexOfPos(u8, fixture, target_index, mode_marker) orelse return ContractError.WrongValidationMode;
    const next_target = std.mem.indexOfPos(u8, fixture, target_index + target_marker.len, "\"target\": ");
    if (next_target) |next_index| {
        if (mode_index > next_index) return ContractError.WrongValidationMode;
    }
}

fn expectCurrentPolicyFixtureSplit(policy: []const u8, fixture: []const u8) !void {
    try expectContains(policy, "\"archive_sha256\": {");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectNotContains(policy, "\"aarch64-linux\": \"");
    try expectNotContains(policy, "\"riscv64-linux\": \"");

    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectTargetMode(fixture, "x86_64-linux", "archive_required");
    try expectTargetMode(fixture, "aarch64-linux", "route_contract_only");
    try expectNotContains(fixture, "\"target\": \"riscv64-linux\"");
    try expectOrdered(fixture, "\"target\": \"x86_64-linux\"", "\"target\": \"aarch64-linux\"");
}

test "phase2 cross policy and fixture keep one archive-required target" {
    const policy = try readRepoFile(policy_path);
    defer testing.allocator.free(policy);
    const fixture = try readRepoFile(fixture_path);
    defer testing.allocator.free(fixture);

    try expectCurrentPolicyFixtureSplit(policy, fixture);
}

test "direct cross checker derives archive_required from archive target scope" {
    const checker = try readRepoFile(checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
    try expectContains(checker, "if validation_mode == \"archive_required\":");
    try expectContains(checker, "archive_required_targets.add(target)");
    try expectContains(checker, "if archive_required_targets != set(archive_target_scope):");
    try expectContains(checker, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
    try expectContains(checker, "fixture[\"cross_targets\"][0][\"validation_mode\"] = \"route_contract_only\"");
    try expectOrdered(
        checker,
        "archive_required_targets.add(target)",
        "if archive_required_targets != set(archive_target_scope):",
    );
}

test "fixture mode guard rejects swapped archive ownership" {
    const policy =
        \\{
        \\  "archive_sha256": {
        \\    "x86_64-linux": "3333333333333333333333333333333333333333333333333333333333333333"
        \\  },
        \\  "upgrade_policy": {
        \\    "archive_target_scope": [
        \\      "x86_64-linux"
        \\    ]
        \\  }
        \\}
    ;
    const swapped_fixture =
        \\{
        \\  "archive_target_scope": [
        \\    "x86_64-linux"
        \\  ],
        \\  "cross_targets": [
        \\    {
        \\      "target": "x86_64-linux",
        \\      "validation_mode": "route_contract_only"
        \\    },
        \\    {
        \\      "target": "aarch64-linux",
        \\      "validation_mode": "archive_required"
        \\    }
        \\  ]
        \\}
    ;

    try testing.expectError(
        ContractError.WrongValidationMode,
        expectCurrentPolicyFixtureSplit(policy, swapped_fixture),
    );
}

test "fixture mode guard rejects stale riscv target widening" {
    const policy =
        \\{
        \\  "archive_sha256": {
        \\    "x86_64-linux": "3333333333333333333333333333333333333333333333333333333333333333"
        \\  },
        \\  "upgrade_policy": {
        \\    "archive_target_scope": [
        \\      "x86_64-linux"
        \\    ]
        \\  }
        \\}
    ;
    const stale_fixture =
        \\{
        \\  "archive_target_scope": [
        \\    "x86_64-linux"
        \\  ],
        \\  "cross_targets": [
        \\    {
        \\      "target": "x86_64-linux",
        \\      "validation_mode": "archive_required"
        \\    },
        \\    {
        \\      "target": "aarch64-linux",
        \\      "validation_mode": "route_contract_only"
        \\    },
        \\    {
        \\      "target": "riscv64-linux",
        \\      "validation_mode": "route_contract_only"
        \\    }
        \\  ]
        \\}
    ;

    try testing.expectError(
        ContractError.UnexpectedMarker,
        expectCurrentPolicyFixtureSplit(policy, stale_fixture),
    );
}

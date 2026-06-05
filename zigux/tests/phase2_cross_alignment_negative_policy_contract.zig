const std = @import("std");

const checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
const fixture = @embedFile("fixtures/phase2_cross_targets.json");

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    ForbiddenMarkerPresent,
};

fn count(text: []const u8, marker: []const u8) usize {
    return std.mem.count(u8, text, marker);
}

fn requireContains(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) == null) return ContractError.MissingMarker;
}

fn requireOnce(text: []const u8, marker: []const u8) !void {
    const matches = count(text, marker);
    if (matches == 0) return ContractError.MissingMarker;
    if (matches != 1) return ContractError.DuplicateMarker;
}

fn requireAbsent(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) != null) return ContractError.ForbiddenMarkerPresent;
}

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

fn validateNegativePolicySelfTests(text: []const u8) !void {
    try requireContains(text, "expected_case_count = (");
    try requireContains(text, "+ 19");
    try requireContains(text, "+ 10");
    try requireContains(text, "payload[\"upgrade_policy\"][\"required_make_routes\"] = [\"phase2-toolchain\", \"phase2-validate\"]");
    try requireContains(text, "payload[\"upgrade_policy\"][\"required_make_routes\"] = \"broken\"");
    try requireContains(text, "payload[\"upgrade_policy\"][\"archive_target_scope\"] = [\"riscv64-linux\"]");
    try requireContains(text, "payload[\"archive_sha256\"] = {\"riscv64-linux\": \"3\" * 64}");
    try requireContains(text, "payload[\"archive_target_scope\"] = [\"aarch64-linux\"]");
    try requireContains(text, "payload[\"cross_targets\"][1][\"validation_mode\"] = \"archive_required\"");
    try requireContains(text, "payload[\"cross_targets\"].append(payload[\"cross_targets\"][0].copy())");
    try requireContains(text, "payload[\"cross_targets\"][0][\"route\"] = \"make -C zigux phase2-toolchain\"");
    try requireContains(text, "payload[\"cross_targets\"][1][\"validation_mode\"] = \"\"");
    try requireContains(text, "path.write_text(\"{\\n\", encoding=\"utf-8\")");
    try requireOnce(text, "\"unsupported archive_target_scope targets\"");
    try requireOnce(text, "\"unsupported policy target did not abort\"");
    try requireOnce(text, "\"missing phase2-cross route did not abort\"");
    try requireOnce(text, "\"invalid required_make_routes shape did not abort\"");
    try requireOnce(text, "(\"DUPLICATE_CROSS_TARGET_ENTRY\", \"x86_64-linux\")");
    try requireContains(text, "(\"INVALID_CROSS_TARGET_FIXTURE_FIELD\", \"archive_target_scope\")");
    try requireContains(text, "(\"INVALID_CROSS_TARGET_FIXTURE_FIELD\", \"cross_targets\")");
    try requireContains(text, "(\"INVALID_CROSS_TARGET_ENTRY\", \"str\")");
    try requireContains(text, "(\"INVALID_CROSS_TARGET_ENTRY\", \"target\")");
    try requireContains(text, "(\"INVALID_CROSS_TARGET_ENTRY\", \"aarch64-linux:validation_mode\")");
    try requireContains(text, "(\"INVALID_CROSS_TARGET_ROUTE\", \"x86_64-linux\")");
    try requireContains(text, "any(code == \"INVALID_CROSS_TARGET_MATRIX\" for code, _ in issues)");
}

fn validateCurrentFixtureBoundary(text: []const u8) !void {
    try requireContains(text, "\"phase\": \"Phase 2\"");
    try requireContains(text, "\"status\": \"active\"");
    try requireContains(text, "\"route\": \"make -C zigux phase2-cross\"");
    try requireOnce(text, "\"target\": \"x86_64-linux\"");
    try requireOnce(text, "\"target\": \"aarch64-linux\"");
    try requireOnce(text, "\"validation_mode\": \"archive_required\"");
    try requireOnce(text, "\"validation_mode\": \"route_contract_only\"");
    try requireAbsent(text, "\"target\": \"riscv64-linux\"");
}

test "alignment checker keeps negative policy self-tests for cross matrix drift" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, checker_path);
    defer allocator.free(checker);

    try validateNegativePolicySelfTests(checker);
}

test "fixture remains the current two-target cross matrix boundary" {
    try validateCurrentFixtureBoundary(fixture);
}

test "contract rejects missing unsupported-target guard" {
    const reduced =
        \\expected_case_count = (
        \\    1
        \\    + 19
        \\    + 10
        \\)
        \\payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        \\payload["upgrade_policy"]["required_make_routes"] = "broken"
        \\payload["upgrade_policy"]["archive_target_scope"] = ["riscv64-linux"]
        \\payload["archive_sha256"] = {"riscv64-linux": "3" * 64}
        \\payload["archive_target_scope"] = ["aarch64-linux"]
        \\payload["cross_targets"][1]["validation_mode"] = "archive_required"
        \\payload["cross_targets"].append(payload["cross_targets"][0].copy())
        \\payload["cross_targets"][0]["route"] = "make -C zigux phase2-toolchain"
        \\payload["cross_targets"][1]["validation_mode"] = ""
        \\path.write_text("{\n", encoding="utf-8")
        \\"unsupported policy target did not abort"
        \\"missing phase2-cross route did not abort"
        \\"invalid required_make_routes shape did not abort"
        \\("DUPLICATE_CROSS_TARGET_ENTRY", "x86_64-linux")
        \\("INVALID_CROSS_TARGET_FIXTURE_FIELD", "archive_target_scope")
        \\("INVALID_CROSS_TARGET_FIXTURE_FIELD", "cross_targets")
        \\("INVALID_CROSS_TARGET_ENTRY", "str")
        \\("INVALID_CROSS_TARGET_ENTRY", "target")
        \\("INVALID_CROSS_TARGET_ENTRY", "aarch64-linux:validation_mode")
        \\("INVALID_CROSS_TARGET_ROUTE", "x86_64-linux")
        \\any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in issues)
    ;

    try std.testing.expectError(ContractError.MissingMarker, validateNegativePolicySelfTests(reduced));
}

test "contract rejects stale riscv64 fixture targets" {
    const stale_fixture =
        \\"phase": "Phase 2",
        \\"status": "active",
        \\"route": "make -C zigux phase2-cross",
        \\"cross_targets": [
        \\  {"target": "x86_64-linux", "validation_mode": "archive_required"},
        \\  {"target": "aarch64-linux", "validation_mode": "route_contract_only"},
        \\  {"target": "riscv64-linux"}
        \\]
    ;

    try std.testing.expectError(ContractError.ForbiddenMarkerPresent, validateCurrentFixtureBoundary(stale_fixture));
}

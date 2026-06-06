const std = @import("std");

const fixture = @embedFile("fixtures/phase2_cross_targets.json");
const docs_note_path = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md";
const scripts_readme_path = "scripts/zigux/README.md";
const tests_readme_path = "zigux/tests/README.md";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    ForbiddenMarkerPresent,
    OutOfOrderMarker,
};

fn requireContains(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) == null) return ContractError.MissingMarker;
}

fn requireOnce(text: []const u8, marker: []const u8) !void {
    const matches = std.mem.count(u8, text, marker);
    if (matches == 0) return ContractError.MissingMarker;
    if (matches != 1) return ContractError.DuplicateMarker;
}

fn requireAbsent(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) != null) return ContractError.ForbiddenMarkerPresent;
}

fn requireBefore(text: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, text, first) orelse return ContractError.MissingMarker;
    const remainder = text[first_index + first.len ..];
    const second_offset = std.mem.indexOf(u8, remainder, second) orelse return ContractError.MissingMarker;
    const second_index = first_index + first.len + second_offset;
    if (first_index >= second_index) return ContractError.OutOfOrderMarker;
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

fn validateFixtureBoundary(text: []const u8) !void {
    try requireContains(text, "\"phase\": \"Phase 2\"");
    try requireContains(text, "\"status\": \"active\"");
    try requireContains(text, "\"route\": \"make -C zigux phase2-cross\"");
    try requireContains(text, "\"archive_target_scope\": [");
    try requireOnce(text, "\"target\": \"x86_64-linux\"");
    try requireOnce(text, "\"target\": \"aarch64-linux\"");
    try requireOnce(text, "\"validation_mode\": \"archive_required\"");
    try requireOnce(text, "\"validation_mode\": \"route_contract_only\"");
    try requireAbsent(text, "\"target\": \"riscv64-linux\"");
}

fn validatePolicyBoundary(text: []const u8) !void {
    try requireContains(text, "\"phase\": \"Phase 2\"");
    try requireContains(text, "\"archive_sha256\": {");
    try requireContains(text, "\"archive_target_scope\": [");
    try requireOnce(text, "\"phase2-cross\"");
    try requireContains(text, "\"x86_64-linux\"");
    try requireAbsent(text, "\"riscv64-linux\"");
}

fn validateDocsNote(text: []const u8) !void {
    try requireContains(text, "scripts/zigux/check-phase2-cross.py");
    try requireContains(text, "scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try requireContains(text, "zigux/tests/fixtures/phase2_cross_targets.json");
    try requireContains(text, "make -C zigux phase2-cross");
    try requireContains(text, "x86_64-linux");
    try requireContains(text, "aarch64-linux");
    try requireContains(text, "archive_required");
    try requireContains(text, "route_contract_only");
    try requireBefore(text, "python3 scripts/zigux/check-phase2-cross.py --self-test", "python3 scripts/zigux/check-phase2-cross.py`");
    try requireBefore(text, "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test", "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`");
}

fn validateScriptsReadme(text: []const u8) !void {
    try requireContains(text, "scripts/zigux/check-phase2-cross.py");
    try requireContains(text, "scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try requireContains(text, "zigux/tests/fixtures/phase2_cross_targets.json");
    try requireContains(text, "python3 scripts/zigux/check-phase2-cross.py --self-test");
    try requireContains(text, "python3 scripts/zigux/check-phase2-cross.py");
    try requireContains(text, "make -C zigux phase2-cross");
    try requireContains(text, "direct cross-route");
    try requireContains(text, "cross-selftest alignment");
}

fn validateTestsReadme(text: []const u8) !void {
    try requireContains(text, "scripts/zigux/check-phase2-cross.py");
    try requireContains(text, "scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try requireContains(text, "zigux/tests/fixtures/phase2_cross_targets.json");
    try requireContains(text, "python3 scripts/zigux/check-phase2-cross.py --self-test");
    try requireContains(text, "python3 scripts/zigux/check-phase2-cross.py");
    try requireContains(text, "make -C zigux phase2-cross");
    try requireContains(text, "x86_64-linux");
    try requireContains(text, "aarch64-linux");
    try requireContains(text, "direct cross-route");
}

test "fixture and policy still describe the bounded cross matrix" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);

    try validateFixtureBoundary(fixture);
    try validatePolicyBoundary(policy);
}

test "docs note keeps cross checker, alignment checker, route, and target split visible" {
    const allocator = std.testing.allocator;
    const docs_note = try readRepoFile(allocator, docs_note_path);
    defer allocator.free(docs_note);

    try validateDocsNote(docs_note);
}

test "scripts and tests readmes keep the cross packet aligned" {
    const allocator = std.testing.allocator;
    const scripts_readme = try readRepoFile(allocator, scripts_readme_path);
    defer allocator.free(scripts_readme);
    const tests_readme = try readRepoFile(allocator, tests_readme_path);
    defer allocator.free(tests_readme);

    try validateScriptsReadme(scripts_readme);
    try validateTestsReadme(tests_readme);
}

test "contract catches reminder and matrix drift" {
    const missing_alignment = "scripts/zigux/check-phase2-cross.py\nmake -C zigux phase2-cross\nx86_64-linux\naarch64-linux\n";
    try std.testing.expectError(ContractError.MissingMarker, validateDocsNote(missing_alignment));

    const missing_live_direct = "scripts/zigux/check-phase2-cross.py\nscripts/zigux/check-phase2-cross-selftest-alignment.py\nzigux/tests/fixtures/phase2_cross_targets.json\nmake -C zigux phase2-cross\nx86_64-linux\naarch64-linux\narchive_required\nroute_contract_only\npython3 scripts/zigux/check-phase2-cross.py --self-test\npython3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\npython3 scripts/zigux/check-phase2-cross-selftest-alignment.py`\n";
    try std.testing.expectError(ContractError.MissingMarker, validateDocsNote(missing_live_direct));

    const widened_fixture =
        \\"phase": "Phase 2",
        \\"status": "active",
        \\"route": "make -C zigux phase2-cross",
        \\"archive_target_scope": [
        \\  "x86_64-linux"
        \\],
        \\"cross_targets": [
        \\  {"target": "x86_64-linux", "validation_mode": "archive_required"},
        \\  {"target": "aarch64-linux", "validation_mode": "route_contract_only"},
        \\  {"target": "riscv64-linux", "validation_mode": "manual_probe_only"}
        \\]
    ;
    try std.testing.expectError(ContractError.ForbiddenMarkerPresent, validateFixtureBoundary(widened_fixture));
}

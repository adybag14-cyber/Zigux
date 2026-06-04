const std = @import("std");

const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";

fn readFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn expectInOrder(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const index = std.mem.indexOfPos(u8, haystack, cursor, needle) orelse
            return error.ExpectedNeedleMissingOrOutOfOrder;
        cursor = index + needle.len;
    }
}

test "phase2 closure manifest keeps no-gap active shape explicit" {
    const manifest = try readFile(manifest_path, 256 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
    try expectContains(manifest, "\"workflow\": \".github/workflows/zigux-bootstrap.yml\"");
    try expectContains(manifest, "\"scope\": \"current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet\"");

    try expectInOrder(manifest, &.{
        "\"notes\": [",
        "\"present_surfaces\": {",
        "\"archive_support\": [",
        "\"artifact_support\": [",
        "\"bootstrap_helpers\": [",
        "\"bridge_helpers\": [",
        "\"checkers\": [",
        "\"closure_notes\": [",
        "\"cross_route_support\": [",
        "\"fixdep_support\": [",
        "\"fixture_roster\": [",
        "\"make_wrappers\": [",
        "\"policy\": [",
        "\"review_surfaces\": [",
        "\"validators\": [",
        "\"repo_reality_gaps\": []",
    });
}

test "phase2 closure manifest pins validators and make wrappers as first-class closure surfaces" {
    const manifest = try readFile(manifest_path, 256 * 1024);
    defer std.testing.allocator.free(manifest);

    const validators = [_][]const u8{
        "\"scripts/zigux/validate-phase2.py\"",
        "\"scripts/zigux/validate-phase2-closure.py\"",
    };
    for (validators) |validator| {
        try expectContains(manifest, validator);
    }

    const routes = [_][]const u8{
        "\"make -C zigux phase2-toolchain\"",
        "\"make -C zigux phase2-tools\"",
        "\"make -C zigux phase2-kconfig\"",
        "\"make -C zigux phase2-cross\"",
        "\"make -C zigux phase2-genksyms\"",
        "\"make -C zigux phase2-fixdep\"",
        "\"make -C zigux phase2-validate\"",
        "\"make -C zigux phase2\"",
    };
    try expectInOrder(manifest, &routes);
}

test "phase2 closure manifest covers each Phase 2 implementation family once in the shared checker roster" {
    const manifest = try readFile(manifest_path, 256 * 1024);
    defer std.testing.allocator.free(manifest);

    const key_checkers = [_][]const u8{
        "\"scripts/zigux/check-zig-toolchain.py\"",
        "\"scripts/zigux/check-kconfig-bridge.py\"",
        "\"scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\"",
        "\"scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py\"",
        "\"scripts/zigux/check-genksyms-bridge.py\"",
        "\"scripts/zigux/check-phase2-fixdep-gate.py\"",
        "\"scripts/zigux/check-fixdep-diff.py\"",
        "\"scripts/zigux/check-phase2-cross.py\"",
        "\"scripts/zigux/check-phase2-tool-manifest.py\"",
        "\"scripts/zigux/check-phase2-bootstrap-workflow-routes.py\"",
    };
    for (key_checkers) |checker| {
        try expectContains(manifest, checker);
    }

    try expectCount(manifest, "\"scripts/zigux/kconfig/conf_bridge.zig\"", 1);
    try expectCount(manifest, "\"scripts/zigux/kconfig/confdata_bridge.zig\"", 1);
    try expectCount(manifest, "\"scripts/zigux/genksyms.zig\"", 1);
    try expectCount(manifest, "\"scripts/zigux/fixdep.zig\"", 1);
    try expectCount(manifest, "\"zigux/tests/fixtures/phase2_cross_targets.json\"", 2);
    try expectCount(manifest, "\"scripts/zigux/zig-toolchain-policy.json\"", 1);
}

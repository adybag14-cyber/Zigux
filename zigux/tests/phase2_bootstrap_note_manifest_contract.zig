const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 2 bootstrap note names the live manifest guard packet" {
    const bootstrap_note = try readRepoFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md", 128 * 1024);
    defer std.testing.allocator.free(bootstrap_note);

    try expectContains(bootstrap_note, "scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(bootstrap_note, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(bootstrap_note, "zigux/tests/fixtures/phase2_tool_manifest.json");
    try expectContains(bootstrap_note, "zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    try expectContains(bootstrap_note, "scripts/zigux/artifact_diff.py");
    try expectContains(bootstrap_note, "fixture-backed artifact-support packet");
    try expectContains(bootstrap_note, "primary artifact-diff helper");
}

test "phase 2 bootstrap note keeps direct cross-route evidence present" {
    const bootstrap_note = try readRepoFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md", 128 * 1024);
    defer std.testing.allocator.free(bootstrap_note);

    try expectContains(bootstrap_note, "zigux/tests/fixtures/phase2_cross_targets.json");
    try expectContains(bootstrap_note, "pinned `x86_64-linux` `archive_required` lane");
    try expectContains(bootstrap_note, "`aarch64-linux` `route_contract_only` lane");
    try expectContains(bootstrap_note, "direct cross-route packet");
    try expectContains(bootstrap_note, "make -C zigux phase2-cross");
}

test "phase 2 manifests mirror the bootstrap-note packet boundaries" {
    const tool_manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 256 * 1024);
    defer std.testing.allocator.free(tool_manifest);
    const artifact_manifest = try readRepoFile("zigux/tests/fixtures/phase2_artifact_tools_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(artifact_manifest);
    const cross_targets = try readRepoFile("zigux/tests/fixtures/phase2_cross_targets.json", 16 * 1024);
    defer std.testing.allocator.free(cross_targets);

    try expectContains(tool_manifest, "scripts/zigux/check-phase2-tool-manifest.py");
    try expectContains(tool_manifest, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(tool_manifest, "scripts/zigux/artifact_diff.py");
    try expectContains(tool_manifest, "scripts/zigux/check-phase2-cross.py");
    try expectContains(tool_manifest, "zigux/tests/fixtures/phase2_cross_targets.json");
    try expectContains(tool_manifest, "make -C zigux phase2-cross");

    try expectContains(artifact_manifest, "\"scope\": \"artifact-diff support for fixture-backed scripts/zigux validation\"");
    try expectContains(artifact_manifest, "\"scripts/zigux/artifact_diff.py\"");
    try expectContains(artifact_manifest, "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectContains(artifact_manifest, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(artifact_manifest, "\"bytes\"");

    try expectContains(cross_targets, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(cross_targets, "\"target\": \"x86_64-linux\"");
    try expectContains(cross_targets, "\"validation_mode\": \"archive_required\"");
    try expectContains(cross_targets, "\"target\": \"aarch64-linux\"");
    try expectContains(cross_targets, "\"validation_mode\": \"route_contract_only\"");
}

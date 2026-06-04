const std = @import("std");

const max_file_size = 512 * 1024;

const RootFiles = struct {
    bootstrap_note: []const u8,
    tool_manifest: []const u8,
    third_party_readme: []const u8,
    makefile: []const u8,
};

fn readRootFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_file_size),
    );
}

fn loadRootFiles(allocator: std.mem.Allocator) !RootFiles {
    return .{
        .bootstrap_note = try readRootFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"),
        .tool_manifest = try readRootFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json"),
        .third_party_readme = try readRootFile(allocator, "third_party/README.md"),
        .makefile = try readRootFile(allocator, "zigux/Makefile"),
    };
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(haystack, needle));
}

test "toolchain bootstrap note pins the returned Phase 2 packet" {
    const files = try loadRootFiles(std.testing.allocator);
    defer std.testing.allocator.free(files.bootstrap_note);
    defer std.testing.allocator.free(files.tool_manifest);
    defer std.testing.allocator.free(files.third_party_readme);
    defer std.testing.allocator.free(files.makefile);

    try expectContains(files.bootstrap_note, "channel `0.17.0-dev.758+748e7c5e3`");
    try expectContains(files.bootstrap_note, "limits archive digests to `x86_64-linux`");
    try expectContains(files.bootstrap_note, "phase2-toolchain");
    try expectContains(files.bootstrap_note, "phase2-tools");
    try expectContains(files.bootstrap_note, "phase2-kconfig");
    try expectContains(files.bootstrap_note, "phase2-cross");
    try expectContains(files.bootstrap_note, "phase2-genksyms");
    try expectContains(files.bootstrap_note, "phase2-fixdep");
    try expectContains(files.bootstrap_note, "phase2-validate");
    try expectContains(files.bootstrap_note, "aggregate `phase2` route");
}

test "bootstrap note reconciles local archive and artifact-support evidence" {
    const files = try loadRootFiles(std.testing.allocator);
    defer std.testing.allocator.free(files.bootstrap_note);
    defer std.testing.allocator.free(files.tool_manifest);
    defer std.testing.allocator.free(files.third_party_readme);
    defer std.testing.allocator.free(files.makefile);

    try expectContains(files.bootstrap_note, "scripts/zigux/check-phase2-artifact-tools-manifest.py");
    try expectContains(files.bootstrap_note, "scripts/zigux/artifact_diff.py");
    try expectContains(files.bootstrap_note, "text`, `json`, `bytes`, and legacy `sha256`-alias");
    try expectContains(files.bootstrap_note, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz");
    try expectContains(files.bootstrap_note, "scripts/zigux/stage-pinned-zig-archive.py");

    try expectContains(files.tool_manifest, "\"artifact_support\"");
    try expectContains(files.tool_manifest, "\"scripts/zigux/artifact_diff.py\"");
    try expectContains(files.tool_manifest, "\"scripts/zigux/check-phase2-artifact-tools-manifest.py\"");
    try expectContains(files.third_party_readme, "sha256: `0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6`");
}

test "bootstrap note keeps bridge, fixdep, cross, and no-gap posture explicit" {
    const files = try loadRootFiles(std.testing.allocator);
    defer std.testing.allocator.free(files.bootstrap_note);
    defer std.testing.allocator.free(files.tool_manifest);
    defer std.testing.allocator.free(files.third_party_readme);
    defer std.testing.allocator.free(files.makefile);

    try expectContains(files.bootstrap_note, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectContains(files.bootstrap_note, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectContains(files.bootstrap_note, "scripts/zigux/genksyms.zig");
    try expectContains(files.bootstrap_note, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(files.bootstrap_note, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(files.bootstrap_note, "zigux/tests/fixtures/phase2_cross_targets.json");
    try expectContains(files.bootstrap_note, "No current repo-reality gaps remain");

    try expectContains(files.tool_manifest, "\"repo_reality_gaps\": []");
    try expectContains(files.makefile, "phase2-toolchain:");
    try expectContains(files.makefile, "phase2: phase2-validate");
}

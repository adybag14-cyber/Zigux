const std = @import("std");

const max_file_size = 512 * 1024;

const RootFiles = struct {
    bootstrap_note: []const u8,
    tool_manifest: []const u8,
    third_party_readme: []const u8,
    makefile: []const u8,
    workflow: []const u8,
    policy: []const u8,
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
        .workflow = try readRootFile(allocator, ".github/workflows/zigux-bootstrap.yml"),
        .policy = try readRootFile(allocator, "scripts/zigux/zig-toolchain-policy.json"),
    };
}

fn freeRootFiles(allocator: std.mem.Allocator, files: RootFiles) void {
    allocator.free(files.bootstrap_note);
    allocator.free(files.tool_manifest);
    allocator.free(files.third_party_readme);
    allocator.free(files.makefile);
    allocator.free(files.workflow);
    allocator.free(files.policy);
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(haystack, needle));
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "toolchain bootstrap note pins the returned Phase 2 packet" {
    const files = try loadRootFiles(std.testing.allocator);
    defer freeRootFiles(std.testing.allocator, files);

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
    defer freeRootFiles(std.testing.allocator, files);

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
    defer freeRootFiles(std.testing.allocator, files);

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

test "workflow replay stays aligned with bootstrap note and policy" {
    const files = try loadRootFiles(std.testing.allocator);
    defer freeRootFiles(std.testing.allocator, files);

    try expectContains(files.policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(files.policy, "\"archive_target_scope\"");
    try expectContains(files.workflow, "ZIGUX_ZIG_CANONICAL_URL");
    try expectContains(files.workflow, "try_local_archive");
    try expectContains(files.workflow, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try expectContains(files.workflow, "community-mirrors.txt");
    try expectContains(files.workflow, "try_download \"$ZIGUX_ZIG_URL\"");
    try expectContains(files.workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try expectContains(files.workflow, "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py");
    try expectContains(files.workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");
    try expectContains(files.workflow, "python3 scripts/zigux/check-lane05-stage-helper-contract.py");
    try expectContains(files.workflow, "python3 scripts/zigux/check-lane05-stage-helper-selftest.py");

    try expectOrdered(files.workflow, "try_local_archive", "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try expectOrdered(files.workflow, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"", "community-mirrors.txt");
    try expectOrdered(files.workflow, "community-mirrors.txt", "try_download \"$ZIGUX_ZIG_URL\"");
    try expectOrdered(files.workflow, "python3 scripts/zigux/check-lane05-stage-helper-selftest.py", "python3 scripts/zigux/check-phase2-fixdep-gate.py");

    try expectContains(files.bootstrap_note, "tries the canonical release before `community-mirrors.txt` and the direct Zig download URL");
    try expectContains(files.bootstrap_note, "archive-verification, helper-contract, helper-selftest");
}

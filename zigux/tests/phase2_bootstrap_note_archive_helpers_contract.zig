const std = @import("std");

const RepoFile = struct {
    path: []const u8,
    text: []const u8,
};

const archive_helper_commands = [_][]const u8{
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) !RepoFile {
    const text = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
    return .{ .path = path, .text = text };
}

fn requireContains(file: RepoFile, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, file.text, marker) != null);
}

fn requireAbsent(file: RepoFile, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, file.text, marker) == null);
}

fn requireOnce(file: RepoFile, marker: []const u8) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOf(u8, file.text[index..], marker)) |relative| {
        count += 1;
        index += relative + marker.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn requireLineOnce(file: RepoFile, line: []const u8) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, file.text, '\n');
    while (lines.next()) |current| {
        if (std.mem.eql(u8, std.mem.trim(u8, current, " \t\r"), line)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn requireBefore(file: RepoFile, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, file.text, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, file.text, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn requireCommandPacket(file: RepoFile) !void {
    for (archive_helper_commands) |command| {
        try requireContains(file, command);
    }
}

fn requireWorkflowCommand(allocator: std.mem.Allocator, file: RepoFile, command: []const u8) !void {
    const line = try std.fmt.allocPrint(allocator, "run: {s}", .{command});
    try requireLineOnce(file, line);
}

test "toolchain bootstrap note keeps archive helper packet explicit" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const note = try readRepoFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");

    try requireContains(note, "This note keeps the current directly readable Phase 2 toolchain packet honest from the docs root.");
    try requireContains(note, "scripts/zigux/check-lane05-install-zig-archive-verification.py");
    try requireContains(note, "scripts/zigux/stage-pinned-zig-archive.py");
    try requireContains(note, "scripts/zigux/check-lane05-stage-helper-contract.py");
    try requireContains(note, "scripts/zigux/check-lane05-stage-helper-selftest.py");
    try requireContains(note, "archive-verification");
    try requireContains(note, "staged archive helper selftest");
    try requireContains(note, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz");
    try requireContains(note, "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.");
    try requireCommandPacket(note);
}

test "workflow preserves archive verification and staged helper order" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");

    const ordered_steps = [_][]const u8{
        "- name: Check current pinned Zig archive packet",
        "- name: Self-test current Lane 05 install-zig archive verification checker",
        "- name: Check current Lane 05 install-zig archive verification packet",
        "- name: Self-test current staged pinned Zig archive helper",
        "- name: Self-test current Zig installer helper",
        "- name: Self-test current Lane 05 stage helper contract checker",
        "- name: Check current Lane 05 stage helper contract packet",
        "- name: Self-test current Lane 05 stage helper selftest checker",
        "- name: Check current Lane 05 stage helper selftest packet",
        "- name: Self-test current Phase 2 fixdep gate checker",
    };

    for (ordered_steps) |step| {
        try requireLineOnce(workflow, step);
    }
    for (archive_helper_commands) |command| {
        try requireWorkflowCommand(allocator, workflow, command);
    }
    for (ordered_steps[0 .. ordered_steps.len - 1], ordered_steps[1..]) |earlier, later| {
        try requireBefore(workflow, earlier, later);
    }
}

test "source checkers expose the same archive helper contract vocabulary" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const install_archive_check = try readRepoFile(allocator, "scripts/zigux/check-lane05-install-zig-archive-verification.py");
    const stage_helper = try readRepoFile(allocator, "scripts/zigux/stage-pinned-zig-archive.py");
    const stage_contract = try readRepoFile(allocator, "scripts/zigux/check-lane05-stage-helper-contract.py");
    const stage_selftest = try readRepoFile(allocator, "scripts/zigux/check-lane05-stage-helper-selftest.py");

    try requireContains(install_archive_check, "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass");
    try requireContains(install_archive_check, "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified");
    try requireContains(install_archive_check, "copy_url_to_file(tarball_url, archive_path)");
    try requireContains(install_archive_check, "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");
    try requireBefore(install_archive_check, "copy_url_to_file(tarball_url, archive_path)", "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)");

    try requireContains(stage_helper, "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=");
    try requireContains(stage_helper, "STAGE_PINNED_ZIG_ARCHIVE_STATUS=");
    try requireContains(stage_helper, "parts_dir");
    try requireContains(stage_helper, "duplicate-suffix archive copies");
    try requireAbsent(stage_helper, "expected exactly two archive target");

    try requireContains(stage_contract, "LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass");
    try requireContains(stage_contract, "LANE05_STAGE_HELPER_CONTRACT_TARGET=");
    try requireContains(stage_contract, "LANE05_STAGE_HELPER_MARKER_COUNT=");
    try requireContains(stage_contract, "duplicate-suffix archive copies");

    try requireContains(stage_selftest, "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass");
    try requireContains(stage_selftest, "Self-test current staged pinned Zig archive helper");
    try requireContains(stage_selftest, "Check current Lane 05 stage helper selftest packet");
    try requireBefore(stage_selftest, "Self-test current Lane 05 stage helper contract checker", "Check current Lane 05 stage helper contract packet");
}

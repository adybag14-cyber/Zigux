const std = @import("std");

const max_file_bytes = 1024 * 1024;

const installer_status_markers = [_][]const u8{
    "ZIG_INSTALL_CHANNEL=",
    "ZIG_INSTALL_VERSION=",
    "ZIG_INSTALL_TARGET=",
    "ZIG_INSTALL_URL=",
    "ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256=",
    "ZIG_INSTALL_ARCHIVE_SHA256=",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified",
    "ZIG_INSTALL_SOURCE=",
    "ZIG_INSTALL_PATH=",
    "ZIG_INSTALL_STATUS=resolved",
    "ZIG_INSTALL_STATUS=pass",
};

const installer_source_markers = [_][]const u8{
    "return 'local_archive'",
    "return 'download'",
    "stage_archive(local_archive, tarball_url, archive_path)",
};

const workflow_markers = [_][]const u8{
    "Setup pinned Zig toolchain",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "make -C zigux phase2-toolchain",
};

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(max_file_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "install-zig exposes the expected CI output contract" {
    const installer = try readRepoFileAlloc(std.testing.allocator, "scripts/zigux/install-zig.py");
    defer std.testing.allocator.free(installer);

    inline for (installer_status_markers) |marker| {
        try expectContains(installer, marker);
    }
    inline for (installer_source_markers) |marker| {
        try expectContains(installer, marker);
    }

    try expectOrdered(installer, "ZIG_INSTALL_CHANNEL=", "ZIG_INSTALL_VERSION=");
    try expectOrdered(installer, "ZIG_INSTALL_VERSION=", "ZIG_INSTALL_TARGET=");
    try expectOrdered(installer, "ZIG_INSTALL_TARGET=", "ZIG_INSTALL_URL=");
    try expectOrdered(installer, "ZIG_INSTALL_STATUS=resolved", "archive_source = stage_archive(local_archive, tarball_url, archive_path)");
    try expectOrdered(installer, "ZIG_INSTALL_SOURCE=", "ZIG_INSTALL_PATH=");
    try expectOrdered(installer, "ZIG_INSTALL_PATH=", "ZIG_INSTALL_STATUS=pass");
}

test "toolchain policy and workflow keep the installer packet reachable" {
    const policy = try readRepoFileAlloc(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy);
    const workflow = try readRepoFileAlloc(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy, "\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"");
    try expectContains(policy, "\"phase2-toolchain\"");

    inline for (workflow_markers) |marker| {
        try expectContains(workflow, marker);
    }

    try expectOrdered(workflow, "Setup pinned Zig toolchain", "python3 scripts/zigux/install-zig.py --self-test");
    try expectOrdered(workflow, "python3 scripts/zigux/install-zig.py --self-test", "make -C zigux phase2-toolchain");
}

test "phase2 notes describe the returned installer output surface as current evidence" {
    const notes = try readRepoFileAlloc(std.testing.allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer std.testing.allocator.free(notes);

    try expectContains(notes, "scripts/zigux/install-zig.py");
    try expectContains(notes, "pinned-channel archive download");
    try expectContains(notes, "archive-verification");
    try expectContains(notes, "install-root replay path");
    try expectContains(notes, "python3 scripts/zigux/install-zig.py --self-test");
    try expectContains(notes, "make -C zigux phase2-toolchain");
    try expectContains(notes, "No current repo-reality gaps remain inside the bounded toolchain, installer");
}

const std = @import("std");

const checker_paths = [_][]const u8{
    "scripts/zigux/check-zig-toolchain.py",
    "check-zig-toolchain.py",
};

const zig_search_markers = [_][]const u8{
    "def iter_zig_search_roots",
    "root / \".zig-toolchain\"",
    "root / \"toolchains\"",
    "root / \".toolchains\"",
    "parent / \".toolchains\"",
    "parent / \"toolchains\"",
};

const zig_resolution_markers = [_][]const u8{
    "def resolve_zig_executable",
    "load_pinned_channel(policy_path)",
    "iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel)",
    "candidate.is_file()",
    "return which(\"zig\")",
};

const current_archive_markers = [_][]const u8{
    "def iter_archive_search_roots",
    "root / \"third_party\"",
    "root / \"agent_files\"",
    "parent / \"agent_files\"",
    "def resolve_policy_archive",
    "def select_matching_policy_archive",
    "multiple repo-local pinned archive candidates matched",
    "archive_name_has_duplicate_suffix",
    "ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS",
};

const archive_cli_markers = [_][]const u8{
    "\"--archive-only\"",
    "\"--archive\"",
    "\"--archive-target\"",
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing",
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid",
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS=present",
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS=mismatch",
};

fn readCheckerSource(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    for (checker_paths) |path| {
        return std.Io.Dir.cwd().readFileAlloc(
            io_instance.io(),
            path,
            allocator,
            .limited(768 * 1024),
        ) catch |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        };
    }
    return error.FileNotFound;
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(haystack, needle));
}

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try expectContains(haystack, needle);
    }
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "toolchain checker keeps repo-local zig search roots ahead of PATH fallback" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    if (contains(source, "def iter_zig_search_roots")) {
        try expectContainsAll(source, &zig_search_markers);
    } else {
        try expectContains(source, "root / \".zig-toolchain\"");
    }
    try expectContainsAll(source, &zig_resolution_markers);
    if (contains(source, "normalize_explicit_zig_path(explicit_zig)")) {
        try expectBefore(source, "normalize_explicit_zig_path(explicit_zig)", "load_pinned_channel(policy_path)");
    }
    try expectBefore(source, "load_pinned_channel(policy_path)", "iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel)");
    try expectBefore(source, "candidate.is_file()", "return which(\"zig\")");
}

test "toolchain checker keeps current pinned archive search roots explicit when present" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    if (!contains(source, "def iter_archive_search_roots")) {
        return;
    }

    try expectContainsAll(source, &current_archive_markers);
    try expectBefore(source, "root / \".zig-toolchain\"", "root / \"third_party\"");
    try expectBefore(source, "root / \"third_party\"", "root / \"agent_files\"");
    try expectBefore(source, "def resolve_policy_archive", "def compute_sha256");
}

test "toolchain checker keeps archive-only reporting separate from executable probing" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "\"--zig\"");
    try expectContains(source, "ZIG_TOOLCHAIN_STATUS=missing");
    if (contains(source, "ZIG_TOOLCHAIN_STATUS=present")) {
        try expectContains(source, "ZIG_TOOLCHAIN_VERSION=");
    }

    if (!contains(source, "\"--policy-only\"")) {
        return;
    }

    try expectContains(source, "\"--policy-only\"");
    if (!contains(source, "\"--archive-only\"")) {
        return;
    }

    try expectContainsAll(source, &archive_cli_markers);
    try expectBefore(source, "if args.policy_only:", "if args.archive_only:");
    try expectBefore(source, "if args.archive_only:", "zig = resolve_zig_executable");
}

const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";

fn readCheckerSource(allocator: std.mem.Allocator) ![]const u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        checker_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireBefore(source: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, source, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, source, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

test "repo-local Zig search roots include repository and parent toolchain roots" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "def iter_zig_search_roots(root: Path = ROOT) -> list[Path]:");
    try requireContains(source, "add_search_root(root / \".zig-toolchain\")");
    try requireContains(source, "add_search_root(root / \"toolchains\")");
    try requireContains(source, "add_search_root(root / \".toolchains\")");
    try requireContains(source, "for parent in root.parents:");
    try requireContains(source, "add_search_root(parent / \".toolchains\")");
    try requireContains(source, "add_search_root(parent / \"toolchains\")");
    try requireBefore(
        source,
        "add_search_root(root / \".toolchains\")",
        "for parent in root.parents:",
    );
}

test "pinned channel candidates are checked before generic local Zig candidates" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "def iter_repo_local_zig_candidates(");
    try requireContains(source, "pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"");
    try requireContains(source, "add_candidate_roots(base / pinned_dirname)");
    try requireContains(source, "add_candidate_roots(child / pinned_dirname)");
    try requireContains(source, "add_candidate_roots(base)");
    try requireContains(source, "add_candidate_roots(child)");
    try requireBefore(
        source,
        "add_candidate_roots(base / pinned_dirname)",
        "add_candidate_roots(base)",
    );
    try requireBefore(
        source,
        "add_candidate_roots(child / pinned_dirname)",
        "add_candidate_roots(child)",
    );
}

test "resolved Zig executable prefers repo-local candidates before PATH fallback" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try requireContains(source, "pinned_channel = load_pinned_channel(policy_path)");
    try requireContains(source, "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):");
    try requireContains(source, "if candidate.is_file():");
    try requireContains(source, "return str(candidate)");
    try requireContains(source, "return which(\"zig\")");
    try requireBefore(
        source,
        "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):",
        "return which(\"zig\")",
    );
    try requireContains(source, "\"zig not found on PATH or in repo-local toolchain search roots\"");
    try requireContains(source, "message += f\" for pinned channel {pinned_channel}\"");
}

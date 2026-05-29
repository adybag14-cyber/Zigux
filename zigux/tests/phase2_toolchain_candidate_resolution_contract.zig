const std = @import("std");
const testing = std.testing;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

test "toolchain checker normalizes explicit zig before repo local fallback" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-zig-toolchain.py");
    defer allocator.free(checker);

    try expectContains(checker, "def normalize_explicit_zig_path(explicit_zig: str) -> str:");
    try expectContains(checker, "normalized = Path(explicit_zig).expanduser()");
    try expectContains(checker, "explicit zig path does not exist");
    try expectContains(checker, "explicit zig path is a directory, expected an executable file");
    try expectOrdered(
        checker,
        "if explicit_zig is not None:\n        return normalize_explicit_zig_path(explicit_zig)",
        "pinned_channel = load_pinned_channel(policy_path)",
    );
}

test "repo local zig search roots prefer in-repo roots before parent fallbacks" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-zig-toolchain.py");
    defer allocator.free(checker);

    try expectContains(checker, "def iter_zig_search_roots(root: Path = ROOT) -> list[Path]:");
    try expectOrdered(checker, "add_search_root(root / \".zig-toolchain\")", "add_search_root(root / \"toolchains\")");
    try expectOrdered(checker, "add_search_root(root / \"toolchains\")", "add_search_root(root / \".toolchains\")");
    try expectOrdered(checker, "for parent in root.parents:", "add_search_root(parent / \".toolchains\")");
    try expectOrdered(checker, "add_search_root(parent / \".toolchains\")", "add_search_root(parent / \"toolchains\")");
}

test "pinned channel candidate scan checks direct and bin zig paths" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-zig-toolchain.py");
    defer allocator.free(checker);

    try expectContains(checker, "def iter_repo_local_zig_candidates(");
    try expectContains(checker, "pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"");
    try expectContains(checker, "add_candidate(base / \"zig\")");
    try expectContains(checker, "add_candidate(base / \"bin\" / \"zig\")");
    try expectOrdered(checker, "for base in zig_search_roots:", "add_candidate_roots(base / pinned_dirname)");
    try expectOrdered(checker, "add_candidate_roots(base / pinned_dirname)", "for child in sorted(base.iterdir()):");
    try testing.expect(countOccurrences(checker, "add_candidate_roots(child / pinned_dirname)") == 1);
}

test "resolution order keeps repo local candidates ahead of PATH zig" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-zig-toolchain.py");
    defer allocator.free(checker);

    try expectOrdered(
        checker,
        "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):",
        "return which(\"zig\")",
    );
    try expectContains(checker, "if candidate.is_file():\n            return str(candidate)");
}

test "pinned policy keeps candidate directory aligned with exact phase two channel" {
    const allocator = testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-zig-toolchain.py");
    defer allocator.free(checker);
    const policy = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);

    try expectContains(policy, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(checker, "zig-x86_64-linux-{pinned_channel}");
    try expectContains(checker, "expected pinned Zig channel {expected_channel_raw}");
}

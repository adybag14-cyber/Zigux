const std = @import("std");

const ContractRoot = struct {
    workflow: []const u8,
    notes: []const u8,
    third_party_readme: []const u8,
    policy: []const u8,
};

fn readContractRoot(allocator: std.mem.Allocator) !ContractRoot {
    return .{
        .workflow = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, ".github/workflows/zigux-bootstrap.yml", allocator, .limited(256 * 1024)),
        .notes = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md", allocator, .limited(96 * 1024)),
        .third_party_readme = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "third_party/README.md", allocator, .limited(48 * 1024)),
        .policy = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "scripts/zigux/zig-toolchain-policy.json", allocator, .limited(24 * 1024)),
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "workflow preserves policy-driven local archive before mirror and direct fallback" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const root = try readContractRoot(arena.allocator());

    try expectContains(root.workflow, "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))");
    try expectContains(root.workflow, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]");
    try expectContains(root.workflow, "channel = policy[\"channel\"]");
    try expectContains(root.workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(root.workflow, "url = f\"https://ziglang.org/builds/{filename}\"");
    try expectContains(root.workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(root.workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(root.workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(root.workflow, "--root \"$GITHUB_WORKSPACE\"");
    try expectContains(root.workflow, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContains(root.workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(root.workflow, "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"");
    try expectContains(root.workflow, "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org");

    try expectOrder(root.workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"", "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectOrder(root.workflow, "try_local_archive() {", "try_download() {");
    try expectOrder(root.workflow, "if try_local_archive; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try expectOrder(root.workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then", "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try expectOrder(root.workflow, "rm -f \"$archive_path\" \"$mirror_file\"", "try_local_archive() {");
    try expectOrder(root.workflow, "rm -rf \"$extract_root\"", "try_local_archive() {");
}

test "workflow keeps local-first reminder checks on the bootstrap path" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const root = try readContractRoot(arena.allocator());

    try expectContains(root.workflow, "- 'third_party/**'");
    try expectContains(root.workflow, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test");
    try expectContains(root.workflow, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try expectContains(root.workflow, "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test");
    try expectContains(root.workflow, "python3 scripts/zigux/check-lane05-local-archive-readme.py");
    try expectContains(root.workflow, "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test");
    try expectContains(root.workflow, "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py");
    try expectContains(root.workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");

    try expectOrder(root.workflow, "- 'scripts/zigux/**'", "- 'third_party/**'");
    try expectOrder(root.workflow, "- 'third_party/**'", "- 'tools/lib/*.zig'");
    try expectOrder(root.workflow, "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test", "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py\n");
    try expectOrder(root.workflow, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py", "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test");
    try expectOrder(root.workflow, "python3 scripts/zigux/check-lane05-local-archive-readme.py", "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test");
    try expectOrder(root.workflow, "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py", "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");

    try std.testing.expectEqual(@as(usize, 1), countOccurrences(root.workflow, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(root.workflow, "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py\n"));
}

test "policy notes and third-party readme agree on the pinned local-first packet" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const root = try readContractRoot(arena.allocator());

    const channel = "0.17.0-dev.87+9b177a7d2";
    const target = "x86_64-linux";
    const digest = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77";
    const archive = "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz";

    try expectContains(root.policy, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(root.policy, "\"minimum_version\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(root.policy, "\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"");
    try expectContains(root.policy, "\"archive_target_scope\": [");
    try expectContains(root.policy, "\"phase2-toolchain\"");

    try expectContains(root.third_party_readme, channel);
    try expectContains(root.third_party_readme, target);
    try expectContains(root.third_party_readme, digest);
    try expectContains(root.third_party_readme, archive);
    try expectContains(root.third_party_readme, "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL");
    try expectContains(root.third_party_readme, "clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle");
    try expectContains(root.third_party_readme, "scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try expectContains(root.third_party_readme, "scripts/zigux/check-lane05-install-zig-archive-verification.py");
    try expectContains(root.third_party_readme, "scripts/zigux/check-lane05-stage-helper-contract.py");

    try expectContains(root.notes, channel);
    try expectContains(root.notes, "tries `community-mirrors.txt` before the direct Zig download URL");
    try expectContains(root.notes, "No current repo-reality gaps remain inside the bounded toolchain");
    try expectContains(root.notes, "local-first archive");
    try expectContains(root.notes, "archive-verification");
    try expectContains(root.notes, "staged-archive helper packet");
}

const std = @import("std");

const archive_filename = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const archive_path = "third_party/" ++ archive_filename;
const archive_parts_dir = archive_path ++ ".parts";
const archive_digest = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const archive_size = "59410844";

const RootDocs = struct {
    third_party_readme: []const u8,
    bootstrap_notes: []const u8,
    tests_readme: []const u8,
    bootstrap_workflow: []const u8,

    fn load(allocator: std.mem.Allocator) !RootDocs {
        return .{
            .third_party_readme = try readFile(allocator, "third_party/README.md"),
            .bootstrap_notes = try readFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"),
            .tests_readme = try readFile(allocator, "zigux/tests/README.md"),
            .bootstrap_workflow = try readFile(allocator, ".github/workflows/zigux-bootstrap.yml"),
        };
    }

    fn deinit(self: RootDocs, allocator: std.mem.Allocator) void {
        allocator.free(self.third_party_readme);
        allocator.free(self.bootstrap_notes);
        allocator.free(self.tests_readme);
        allocator.free(self.bootstrap_workflow);
    }
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingRequiredMarker;
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = try indexOfRequired(haystack, first);
    const second_index = try indexOfRequired(haystack, second);
    try std.testing.expect(first_index < second_index);
}

test "third party README documents the pinned archive and the absent payload recovery path" {
    var docs = try RootDocs.load(std.testing.allocator);
    defer docs.deinit(std.testing.allocator);

    try expectContains(docs.third_party_readme, "target: `x86_64-linux`");
    try expectContains(docs.third_party_readme, "channel: `0.17.0-dev.758+748e7c5e3`");
    try expectContains(docs.third_party_readme, "sha256: `" ++ archive_digest ++ "`");
    try expectContains(docs.third_party_readme, "size: `" ++ archive_size ++ "` bytes");
    try expectContains(docs.third_party_readme, archive_path);
    try expectContains(docs.third_party_readme, archive_parts_dir);
    try expectContains(docs.third_party_readme, "If the exact archive file is absent");
    try expectContains(docs.third_party_readme, "stage-pinned-zig-archive.py");
}

test "Phase 2 docs preserve allow-missing archive replay as the truthful absence check" {
    var docs = try RootDocs.load(std.testing.allocator);
    defer docs.deinit(std.testing.allocator);

    const allow_missing = "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing";
    try expectContains(docs.bootstrap_notes, allow_missing);
    try expectContains(docs.tests_readme, allow_missing);
    try expectContains(docs.bootstrap_notes, "stage-pinned-zig-archive.py --self-test");
    try expectContains(docs.bootstrap_notes, "check-lane05-stage-helper-contract.py");
    try expectContains(docs.bootstrap_notes, "check-lane05-stage-helper-selftest.py");
    try expectNotContains(docs.bootstrap_notes, "repo-local archive payload is present");
    try expectNotContains(docs.tests_readme, "repo-local archive payload is present");
}

test "bootstrap workflow keeps local archive parts before network fallback" {
    var docs = try RootDocs.load(std.testing.allocator);
    defer docs.deinit(std.testing.allocator);

    try expectContains(docs.bootstrap_workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(docs.bootstrap_workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(docs.bootstrap_workflow, "stage-pinned-zig-archive.py");
    try expectContains(docs.bootstrap_workflow, "ZIGUX_ZIG_CANONICAL_URL");
    try expectContains(docs.bootstrap_workflow, "community-mirrors.txt");
    try expectContains(docs.bootstrap_workflow, "ziglang.org/builds");
    try expectBefore(docs.bootstrap_workflow, "try_local_archive", "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try expectBefore(docs.bootstrap_workflow, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"", "community-mirrors.txt");
    try expectBefore(docs.bootstrap_workflow, "community-mirrors.txt", "try_download \"$ZIGUX_ZIG_URL\"");
}

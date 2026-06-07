const std = @import("std");

const target = "x86_64-linux";
const channel = "0.17.0-dev.758+748e7c5e3";
const archive_name = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const archive_path = "third_party/" ++ archive_name;
const parts_path = archive_path ++ ".parts";
const archive_sha = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const archive_size = "59410844";
const archive_replay_command =
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive " ++
    archive_path ++ " --archive-target " ++ target;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "third_party archive README mirrors the policy-owned pinned archive identity" {
    const allocator = std.testing.allocator;
    const third_party_readme = try readRepoFile(allocator, "third_party/README.md");
    defer allocator.free(third_party_readme);
    const policy_json = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy_json);

    try requireContains(policy_json, "\"phase\": \"Phase 2\"");
    try requireContains(policy_json, "\"channel\": \"" ++ channel ++ "\"");
    try requireContains(policy_json, "\"minimum_version\": \"" ++ channel ++ "\"");
    try requireContains(policy_json, "\"" ++ target ++ "\": \"" ++ archive_sha ++ "\"");
    try requireContains(policy_json, "\"archive_target_scope\"");
    try requireContains(policy_json, "\"" ++ target ++ "\"");

    try requireContains(third_party_readme, "# Zigux third-party archives");
    try requireContains(third_party_readme, "`" ++ target ++ "`");
    try requireContains(third_party_readme, "`" ++ channel ++ "`");
    try requireContains(third_party_readme, "`" ++ archive_path ++ "`");
    try requireContains(third_party_readme, "`" ++ parts_path ++ "`");
    try requireContains(third_party_readme, "`" ++ archive_sha ++ "`");
    try requireContains(third_party_readme, "`" ++ archive_size ++ "` bytes");
    try requireContains(third_party_readme, "`" ++ archive_replay_command ++ "`");
    try requireContains(third_party_readme, "`scripts/zigux/zig-toolchain-policy.json`");
}

test "third_party README keeps the local-first archive replay and duplicate boundary explicit" {
    const allocator = std.testing.allocator;
    const third_party_readme = try readRepoFile(allocator, "third_party/README.md");
    defer allocator.free(third_party_readme);

    try requireContains(third_party_readme, "Lane 05 bootstrap first reuses and validates");
    try requireContains(third_party_readme, "stages the same pinned payload locally with `scripts/zigux/stage-pinned-zig-archive.py`");
    try requireContains(third_party_readme, "canonical release, mirror, or direct-download path");
    try requireContains(third_party_readme, "`community-mirrors.txt`");
    try requireContains(third_party_readme, "`scripts/zigux/check-lane05-local-first-archive-workflow.py`");
    try requireContains(third_party_readme, "`scripts/zigux/check-lane05-local-archive-readme.py`");
    try requireContains(third_party_readme, "`scripts/zigux/check-lane05-install-zig-archive-verification.py`");
    try requireContains(third_party_readme, "`scripts/zigux/check-lane05-stage-helper-contract.py`");
    try requireContains(third_party_readme, "`scripts/zigux/check-lane05-stage-helper-selftest.py`");
    try requireContains(third_party_readme, "duplicate-suffix archives are rejected before staging");
    try requireContains(third_party_readme, "`zig-x86_64-linux-0.17.0-dev.758+748e7c5e3 (1).tar.xz`");

    try requireBefore(third_party_readme, "repo-local archive", "canonical release before `community-mirrors.txt`");
    try requireBefore(third_party_readme, "`community-mirrors.txt`", "direct `ziglang.org` download URL");
}

test "archive README checker consumes the same current README contract" {
    const allocator = std.testing.allocator;
    const archive_readme_checker = try readRepoFile(allocator, "scripts/zigux/check-lane05-local-archive-readme.py");
    defer allocator.free(archive_readme_checker);

    try requireContains(archive_readme_checker, "README_PATH = Path(\"third_party/README.md\")");
    try requireContains(archive_readme_checker, "POLICY_PATH = Path(\"scripts/zigux/zig-toolchain-policy.json\")");
    try requireContains(archive_readme_checker, "\"x86_64-linux\": 59_410_844");
    try requireContains(archive_readme_checker, "expected_archive_filename(target, channel)");
    try requireContains(archive_readme_checker, "\"python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"");
    try requireContains(archive_readme_checker, "expected_parts_path = f\"{expected_path}.parts\"");
    try requireContains(archive_readme_checker, "ARCHIVE_DUPLICATE_SUFFIX_RE");
    try requireContains(archive_readme_checker, "\"third_party contains duplicate-suffix archive copies\"");
    try requireContains(archive_readme_checker, "payload_status = \"missing_allowed\"");
    try requireContains(archive_readme_checker, "payload_status = \"present\"");
    try requireContains(archive_readme_checker, "LANE05_LOCAL_ARCHIVE_README_SELF_TEST=pass");
    try requireContains(archive_readme_checker, "LANE05_LOCAL_ARCHIVE_README_SELF_TEST_CASE_COUNT=");
}

test "shared Phase 2 documentation points reviewers back to the third_party archive packet" {
    const allocator = std.testing.allocator;
    const bootstrap_note = try readRepoFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer allocator.free(bootstrap_note);
    const review_checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(review_checklist);

    try requireContains(bootstrap_note, "`third_party/README.md` is directly readable on current `master`");
    try requireContains(bootstrap_note, "repo-local pinned archive filename, digest, size, duplicate-copy boundary");
    try requireContains(bootstrap_note, archive_replay_command);
    try requireContains(bootstrap_note, "third_party archive README truthfulness");

    try requireContains(review_checklist, "if the change touches the shared Phase 2 toolchain packet");
    try requireContains(review_checklist, "`third_party/README.md`");
    try requireContains(review_checklist, archive_replay_command);
    try requireContains(review_checklist, "`python3 scripts/zigux/check-lane05-local-archive-readme.py`");
    try requireContains(review_checklist, "`make -C zigux phase2-toolchain`");
}

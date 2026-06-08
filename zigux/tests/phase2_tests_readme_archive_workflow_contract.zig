const std = @import("std");
const testing = std.testing;

const archive_target = "x86_64-linux";
const archive_channel = "0.17.0-dev.758+748e7c5e3";
const archive_filename = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const archive_path = "third_party/" ++ archive_filename;
const archive_parts_path = archive_path ++ ".parts";
const archive_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const archive_size = "59410844";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try testing.expect(earlier_index < later_index);
}

test "tests README keeps local-first archive workflow packet explicit" {
    const readme = try readFile(testing.allocator, "zigux/tests/README.md");
    defer testing.allocator.free(readme);

    const required_markers = [_][]const u8{
        "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`",
        "returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract",
        archive_path,
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive " ++ archive_path ++ " --archive-target " ++ archive_target,
        "local-first `third_party`, canonical `adybag14-cyber/zig` release, mirror, then direct-download bootstrap order",
        "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
        "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
        "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
        "python3 scripts/zigux/check-lane05-local-archive-readme.py",
        "scripts/zigux/stage-pinned-zig-archive.py",
        "scripts/zigux/check-lane05-install-zig-archive-verification.py",
        "scripts/zigux/check-lane05-stage-helper-contract.py",
        "scripts/zigux/check-lane05-stage-helper-selftest.py",
    };

    for (required_markers) |marker| {
        try expectContains(readme, marker);
    }

    try expectBefore(readme, "third_party/README.md", "scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try expectBefore(readme, "scripts/zigux/check-lane05-local-first-archive-workflow.py", "scripts/zigux/check-lane05-local-archive-readme.py");
}

test "third-party archive README mirrors policy and staging contract" {
    const readme = try readFile(testing.allocator, "third_party/README.md");
    defer testing.allocator.free(readme);

    const required_markers = [_][]const u8{
        "Lane 05 bootstrap CI",
        "`" ++ archive_target ++ "`",
        "`" ++ archive_channel ++ "`",
        "`" ++ archive_path ++ "`",
        "`" ++ archive_parts_path ++ "`",
        "`" ++ archive_sha256 ++ "`",
        "`" ++ archive_size ++ "` bytes",
        "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive " ++ archive_path ++ " --archive-target " ++ archive_target ++ "`",
        "stages the same pinned payload locally with `scripts/zigux/stage-pinned-zig-archive.py`",
        "canonical `adybag14-cyber/zig` release before `community-mirrors.txt` and the direct `ziglang.org` download URL",
        "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
        "`scripts/zigux/check-lane05-local-archive-readme.py`",
        "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
        "`scripts/zigux/check-lane05-stage-helper-contract.py`",
        "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
        "`zig-x86_64-linux-0.17.0-dev.758+748e7c5e3 (1).tar.xz`",
    };

    for (required_markers) |marker| {
        try expectContains(readme, marker);
    }

    try expectBefore(readme, "repo-local archive is unavailable", "canonical `adybag14-cyber/zig` release");
    try expectBefore(readme, "canonical `adybag14-cyber/zig` release", "`community-mirrors.txt`");
}

test "workflow runs archive guards before broader Phase 2 checks" {
    const workflow = try readFile(testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer testing.allocator.free(workflow);

    const required_markers = [_][]const u8{
        "- 'third_party/**'",
        "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
        "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
        "python3 scripts/zigux/stage-pinned-zig-archive.py",
        "--parts-dir \"$repo_archive_parts_dir\"",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
        "if try_download \"$ZIGUX_ZIG_URL\"; then",
        "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
        "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
        "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
        "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
        "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
        "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
        "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
        "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
        "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
        "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
        "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
        "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    };

    for (required_markers) |marker| {
        try expectContains(workflow, marker);
    }

    try expectBefore(workflow, "- name: Self-test current Lane 05 local-first archive checker", "- name: Check current Lane 05 local-first archive packet");
    try expectBefore(workflow, "- name: Check current Lane 05 local-first archive packet", "- name: Self-test current Lane 05 local archive README checker");
    try expectBefore(workflow, "- name: Check current Lane 05 local archive README packet", "- name: Self-test current Lane 05 install-zig archive verification checker");
    try expectBefore(workflow, "- name: Check current Lane 05 stage helper selftest packet", "- name: Self-test current Phase 2 fixdep gate checker");
}

test "docs and helper checkers keep the same archive packet names" {
    const bootstrap_note = try readFile(testing.allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer testing.allocator.free(bootstrap_note);
    const checklist = try readFile(testing.allocator, "Documentation/zigux/review-checklist.md");
    defer testing.allocator.free(checklist);
    const local_first_checker = try readFile(testing.allocator, "scripts/zigux/check-lane05-local-first-archive-workflow.py");
    defer testing.allocator.free(local_first_checker);
    const local_archive_checker = try readFile(testing.allocator, "scripts/zigux/check-lane05-local-archive-readme.py");
    defer testing.allocator.free(local_archive_checker);
    const stage_checker = try readFile(testing.allocator, "scripts/zigux/check-lane05-stage-helper-contract.py");
    defer testing.allocator.free(stage_checker);

    for ([_][]const u8{ bootstrap_note, checklist }) |text| {
        try expectContains(text, "third_party/README.md");
        try expectContains(text, "scripts/zigux/check-lane05-local-first-archive-workflow.py");
        try expectContains(text, "scripts/zigux/check-lane05-local-archive-readme.py");
        try expectContains(text, archive_path);
        try expectContains(text, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive " ++ archive_path ++ " --archive-target " ++ archive_target);
    }

    try expectContains(local_first_checker, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(local_first_checker, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(local_first_checker, "STAGE_HELPER_CMD = \"python3 scripts/zigux/stage-pinned-zig-archive.py\"");
    try expectContains(local_first_checker, "README_SELF_TEST_CMD = \"python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test\"");
    try expectContains(local_first_checker, "README_CHECK_CMD = \"python3 scripts/zigux/check-lane05-local-archive-readme.py\"");

    try expectContains(local_archive_checker, "EXPECTED_ARCHIVE_SIZES");
    try expectContains(local_archive_checker, "\"" ++ archive_target ++ "\": 59_410_844");
    try expectContains(local_archive_checker, "expected_parts_path = f\"{expected_path}.parts\"");
    try expectContains(local_archive_checker, "duplicate_archive_name(expected_filename)");

    try expectContains(stage_checker, "STAGE_PINNED_ZIG_ARCHIVE=pass");
    try expectContains(stage_checker, "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass");
    try expectContains(stage_checker, "scripts/zigux/stage-pinned-zig-archive.py");
}

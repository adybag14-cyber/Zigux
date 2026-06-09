const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

const expected_channel = "0.17.0-dev.758+748e7c5e3";
const expected_target = "x86_64-linux";
const expected_archive_sha = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";

fn readFileAlloc(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, std.Io.Limit.limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse {
        std.debug.print("missing first marker: {s}\n", .{first});
        return error.MissingMarker;
    };
    const second_index = std.mem.indexOf(u8, haystack, second) orelse {
        std.debug.print("missing second marker: {s}\n", .{second});
        return error.MissingMarker;
    };
    try std.testing.expect(first_index < second_index);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var remaining = haystack;
    var count: usize = 0;
    while (std.mem.indexOf(u8, remaining, needle)) |index| {
        count += 1;
        remaining = remaining[index + needle.len ..];
    }
    try std.testing.expectEqual(expected, count);
}

test "workflow derives archive cache names from the single policy target" {
    const workflow = try readFileAlloc(workflow_path);
    defer std.testing.allocator.free(workflow);
    const policy = try readFileAlloc(policy_path);
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"channel\": \"" ++ expected_channel ++ "\"");
    try expectContains(policy, "\"" ++ expected_target ++ "\": \"" ++ expected_archive_sha ++ "\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectCount(policy, "\"" ++ expected_target ++ "\"", 2);
    try expectContains(workflow, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]");
    try expectContains(workflow, "if len(targets) != 1:");
    try expectContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try expectContains(workflow, "ZIGUX_ZIG_TARGET='{target}'");
    try expectContains(workflow, "ZIGUX_ZIG_CHANNEL='{channel}'");
    try expectContains(workflow, "archive_path=\".zig-toolchain/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "extract_root=\"$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL\"");
}

test "workflow remains local-first and validates archives before extraction" {
    const workflow = try readFileAlloc(workflow_path);
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try expectContains(workflow, "tar -xJf \"$archive_path\" -C .zig-toolchain");
    try expectBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"", "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try expectBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"", "tar -xJf \"$archive_path\" -C .zig-toolchain");
}

test "workflow fallback ladder keeps canonical release before mirrors and ziglang" {
    const workflow = try readFileAlloc(workflow_path);
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "canonical_repo = \"adybag14-cyber/zig\"");
    try expectContains(workflow, "canonical_tag = \"upstream-748e7c5e39fc\"");
    try expectContains(workflow, "ZIGUX_ZIG_CANONICAL_URL");
    try expectContains(workflow, "try_local_archive");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try expectContains(workflow, "https://ziglang.org/download/community-mirrors.txt");
    try expectContains(workflow, "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_URL\"");
    try expectBefore(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectBefore(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow, "https://ziglang.org/download/community-mirrors.txt", "try_download \"$ZIGUX_ZIG_URL\"");
}

test "cross fixture stays aligned with the archive-backed workflow target" {
    const fixture = try readFileAlloc(fixture_path);
    defer std.testing.allocator.free(fixture);

    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\"");
    try expectCount(fixture, "\"" ++ expected_target ++ "\"", 2);
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectContains(fixture, "\"review_status\": \"route contract only\"");
    try std.testing.expect(std.mem.indexOf(u8, fixture, "riscv64-linux") == null);
}

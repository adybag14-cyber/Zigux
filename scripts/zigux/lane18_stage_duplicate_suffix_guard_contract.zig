const std = @import("std");
const testing = std.testing;

const stage_helper_source = @embedFile("stage-pinned-zig-archive.py");

fn expectContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, stage_helper_source, needle) != null);
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, stage_helper_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, stage_helper_source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "Lane 18 stage helper preserves duplicate suffix archive detection" {
    try expectContains("ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile");
    try expectContains("(?P<copy>\\d+)");
    try expectContains("def duplicate_archive_name(expected_filename: str) -> str:");
    try expectContains("return f\"{stem} (1).tar.xz\"");
    try expectContains("def duplicate_source_fixture_name(expected_filename: str) -> str:");
    try expectContains("return duplicate_archive_name(expected_filename)");
    try expectContains("def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:");
    try expectContains("ARCHIVE_DUPLICATE_SUFFIX_RE.fullmatch(path_name)");
    try expectContains("return match.group(\"stem\") == expected_filename[: -len(\".tar.xz\")]");
}

test "Lane 18 stage helper fails closed on duplicate third-party archive copies before staging" {
    try expectContains("def require_clean_third_party(root: Path, expected_filename: str) -> None:");
    try expectContains("third_party_dir.glob(\"*.tar.xz\")");
    try expectContains("archive_name_has_duplicate_suffix(path.name, expected_filename)");
    try expectContains("third_party contains duplicate-suffix archive copies");
    try expectContains("third_party must not contain {duplicate_archive_name(expected_filename)}");
    try expectBefore(
        "destination = root / THIRD_PARTY_DIR / str(metadata[\"filename\"])\n    require_clean_third_party(root, str(metadata[\"filename\"]))",
        "resolved_source, input_mode, cleanup = resolve_source_archive(",
    );
    try expectBefore(
        "require_clean_third_party(root, str(metadata[\"filename\"]))",
        "copy_file(resolved_source, destination)",
    );
}

test "Lane 18 stage helper self-test covers allowed source duplicate and blocked repo duplicate" {
    try expectContains("stage_archive_external_duplicate_source_pass_");
    try expectContains("source_with_duplicate_name = source.with_name(");
    try expectContains("duplicate_source_fixture_name(str(metadata[\"filename\"]))");
    try expectContains("assert destination.name == metadata[\"filename\"]");
    try expectContains("duplicate_archive_name(\"zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz\")");
    try expectContains("expected_substring=\"duplicate-suffix archive copies\"");
}

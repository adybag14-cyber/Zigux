const std = @import("std");
const testing = std.testing;

const checker_source = @embedFile("check-phase1-parity.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireStartsWith(haystack: []const u8, prefix: []const u8) !void {
    try testing.expect(std.mem.startsWith(u8, haystack, prefix));
}

fn requireBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "duplicate tracking loader rejects silent JSON key overwrite" {
    try requireStartsWith(checker_source, "#!/usr/bin/env python3");
    try requireContains(checker_source, "class DuplicateTrackingDict(dict[str, object]):");
    try requireContains(checker_source, "self.duplicate_keys: list[str] = []");
    try requireContains(checker_source, "if key in self and key not in self.duplicate_keys:");
    try requireContains(checker_source, "self.duplicate_keys.append(key)");
    try requireContains(checker_source, "json.loads(text, object_pairs_hook=DuplicateTrackingDict)");

    try requireBefore(
        checker_source,
        "def load_json_with_duplicate_tracking(text: str) -> object:",
        "def read_json(path: Path, label: str, issues: list[str]) -> object | None:",
    );
}

test "recursive duplicate path collector preserves nested issue labels" {
    try requireContains(checker_source, "def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:");
    try requireContains(checker_source, "paths.append(\".\".join(prefix + (key,)))");
    try requireContains(checker_source, "paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))");
    try requireContains(checker_source, "elif isinstance(data, list):");
    try requireContains(checker_source, "paths.extend(collect_duplicate_json_key_paths(item, prefix))");
    try requireContains(checker_source, "issues.extend(f\"{label}:duplicate_json_key:{duplicate_path}\" for duplicate_path in duplicate_paths)");

    try requireBefore(
        checker_source,
        "duplicate_paths = collect_duplicate_json_key_paths(payload)",
        "issues.extend(f\"{label}:duplicate_json_key:{duplicate_path}\" for duplicate_path in duplicate_paths)",
    );
}

test "fixture manifest and blocker packets all use duplicate-aware JSON reads" {
    try requireContains(checker_source, "fixture_payload = read_json(root / FIXTURE_REL, \"fixture\", issues)");
    try requireContains(checker_source, "manifest_payload = read_json(root / MANIFEST_REL, \"manifest\", issues)");
    try requireContains(checker_source, "blockers_payload = read_json(root / BLOCKERS_REL, \"blockers\", issues)");

    try requireBefore(
        checker_source,
        "fixture_payload = read_json(root / FIXTURE_REL, \"fixture\", issues)",
        "manifest_payload = read_json(root / MANIFEST_REL, \"manifest\", issues)",
    );
    try requireBefore(
        checker_source,
        "manifest_payload = read_json(root / MANIFEST_REL, \"manifest\", issues)",
        "blockers_payload = read_json(root / BLOCKERS_REL, \"blockers\", issues)",
    );
    try requireContains(checker_source, "issues.extend(f\"{label}:duplicate_json_key:{duplicate_path}\" for duplicate_path in duplicate_paths)");
}

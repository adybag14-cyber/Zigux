const std = @import("std");

const checker_source = @embedFile("check-phase1-parity.py");

fn requireCurrentChecker() !void {
    if (!std.mem.containsAtLeast(u8, checker_source, 1, "class DuplicateTrackingDict")) {
        return error.SkipZigTest;
    }
}

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, checker_source, 1, needle));
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, checker_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, checker_source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase1 parity checker tracks duplicate json keys through object pairs" {
    try requireCurrentChecker();

    try expectContains("class DuplicateTrackingDict(dict[str, object]):");
    try expectContains("self.duplicate_keys: list[str] = []");
    try expectContains("if key in self and key not in self.duplicate_keys:");
    try expectContains("self.duplicate_keys.append(key)");
    try expectContains("json.loads(text, object_pairs_hook=DuplicateTrackingDict)");
    try expectContains("def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str>:");
    try expectContains("paths.append(\".\".join(prefix + (key,)))");

    try expectBefore(
        "def load_json_with_duplicate_tracking(text: str) -> object:",
        "def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str>:",
    );
    try expectBefore(
        "def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str>:",
        "def read_json(path: Path, label: str, issues: list[str]) -> object | None:",
    );
}

test "phase1 parity checker fails closed on duplicate json keys" {
    try requireCurrentChecker();

    try expectContains("duplicate_paths = collect_duplicate_json_key_paths(payload)");
    try expectContains("if duplicate_paths:");
    try expectContains("issues.extend(f\"{label}:duplicate_json_key:{duplicate_path}\" for duplicate_path in duplicate_paths)");
    try expectContains("return None");

    try expectBefore(
        "duplicate_paths = collect_duplicate_json_key_paths(payload)",
        "issues.extend(f\"{label}:duplicate_json_key:{duplicate_path}\" for duplicate_path in duplicate_paths)",
    );
    try expectBefore(
        "issues.extend(f\"{label}:duplicate_json_key:{duplicate_path}\" for duplicate_path in duplicate_paths)",
        "return None",
    );
}

test "phase1 parity checker routes every json packet through duplicate tracking" {
    try requireCurrentChecker();

    try expectContains("fixture_payload = read_json(root / FIXTURE_REL, \"fixture\", issues)");
    try expectContains("manifest_payload = read_json(root / MANIFEST_REL, \"manifest\", issues)");
    try expectContains("blockers_payload = read_json(root / BLOCKERS_REL, \"blockers\", issues)");

    try expectBefore(
        "fixture_payload = read_json(root / FIXTURE_REL, \"fixture\", issues)",
        "manifest_payload = read_json(root / MANIFEST_REL, \"manifest\", issues)",
    );
    try expectBefore(
        "manifest_payload = read_json(root / MANIFEST_REL, \"manifest\", issues)",
        "blockers_payload = read_json(root / BLOCKERS_REL, \"blockers\", issues)",
    );
}

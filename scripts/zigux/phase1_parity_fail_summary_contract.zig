const std = @import("std");

const checker_source = @embedFile("check-phase1-parity.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn expectOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, checker_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, checker_source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn requireCurrentFailureSurface() !void {
    if (std.mem.indexOf(u8, checker_source, "def run_check(root: Path) -> int:") == null or
        std.mem.indexOf(u8, checker_source, "print(f\"PHASE1_PARITY_ISSUE={issue}\")") == null)
    {
        return error.SkipZigTest;
    }
}

test "phase1 parity failure envelope emits status before issue lines" {
    try requireCurrentFailureSurface();

    try expectContains("def run_check(root: Path) -> int:");
    try expectContains("issues = collect_issues(root)");
    try expectContains("if issues:");
    try expectContains("print(\"PHASE1_PARITY=fail\")");
    try expectContains("for issue in issues:");
    try expectContains("print(f\"PHASE1_PARITY_ISSUE={issue}\")");
    try expectContains("return 1");

    try expectOrdered("print(\"PHASE1_PARITY=fail\")", "print(f\"PHASE1_PARITY_ISSUE={issue}\")");
    try expectOrdered("print(f\"PHASE1_PARITY_ISSUE={issue}\")", "return 1");
    try expectOrdered("return 1", "print(\"PHASE1_PARITY=pass\")");
}

test "phase1 parity issue collection preserves deterministic check order" {
    try requireCurrentFailureSurface();

    try expectContains("def collect_issues(root: Path) -> list[str]:");
    try expectContains("for rel in (ARTIFACT_DIFF_REL, FIXTURE_REL, MANIFEST_REL, BLOCKERS_REL, REPLAY_REL, REPLAY_BUILD_REL):");
    try expectContains("check_artifact_diff(root, issues)");
    try expectContains("check_replay_routes(root, issues)");
    try expectContains("fixture_payload = read_json(root / FIXTURE_REL, \"fixture\", issues)");
    try expectContains("manifest_payload = read_json(root / MANIFEST_REL, \"manifest\", issues)");
    try expectContains("blockers_payload = read_json(root / BLOCKERS_REL, \"blockers\", issues)");

    try expectOrdered("check_artifact_diff(root, issues)", "check_replay_routes(root, issues)");
    try expectOrdered("check_replay_routes(root, issues)", "fixture_payload = read_json(root / FIXTURE_REL, \"fixture\", issues)");
    try expectOrdered("fixture_payload = read_json(root / FIXTURE_REL, \"fixture\", issues)", "manifest_payload = read_json(root / MANIFEST_REL, \"manifest\", issues)");
    try expectOrdered("manifest_payload = read_json(root / MANIFEST_REL, \"manifest\", issues)", "blockers_payload = read_json(root / BLOCKERS_REL, \"blockers\", issues)");
}

test "phase1 parity failure markers stay disjoint from success summary markers" {
    try requireCurrentFailureSurface();

    try expectContains("print(\"PHASE1_PARITY=pass\")");
    try expectContains("print(f\"PHASE1_PARITY_SECTION_COUNT={len(EXPECTED_SECTIONS)}\")");
    try expectContains("print(f\"PHASE1_PARITY_HELPER_COUNT={len(EXPECTED_HELPERS)}\")");
    try expectContains("print(\"PHASE1_PARITY_REPLAY=present\")");
    try expectContains("print(f\"PHASE1_PARITY_BLOCKER_COUNT={len(EXPECTED_REPLAY_BLOCKER_IDS)}\")");
    try expectContains("print(\"PHASE1_PARITY_BLOCKER_IDS=\" + \",\".join(EXPECTED_REPLAY_BLOCKER_IDS))");
    try expectContains("print(f\"PHASE1_PARITY_DIRECT_REVIEW_HELPER_COUNT={len(EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS)}\")");
    try expectContains("return 0");

    try expectOrdered("print(\"PHASE1_PARITY=fail\")", "print(\"PHASE1_PARITY=pass\")");
    try expectOrdered("print(f\"PHASE1_PARITY_ISSUE={issue}\")", "print(f\"PHASE1_PARITY_SECTION_COUNT={len(EXPECTED_SECTIONS)}\")");
}

const std = @import("std");

const repo_files = .{
    .docs_readme = "Documentation/zigux/README.md",
    .review_checklist = "Documentation/zigux/review-checklist.md",
    .freeze_map = "Documentation/zigux/freeze-map.md",
    .validator = "scripts/zigux/validate-phase15.py",
    .architecture_checker = "scripts/zigux/check-phase15-architecture-council-packet.py",
};

const expected_validator_checkers = [_][]const u8{
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-architecture-council-packet.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "phase15 validator keeps the governance checker roster explicit" {
    const allocator = std.testing.allocator;
    const validator = try readFile(allocator, repo_files.validator);
    defer allocator.free(validator);

    try expectContains(validator, "EXPECTED_PHASE15_VALIDATE_CHECKERS");
    inline for (expected_validator_checkers) |checker_path| {
        try expectContains(validator, checker_path);
    }

    try expectContains(validator, "EXPECTED_DIRECT_PACKET_PATHS");
    try expectContains(validator, "Documentation/zigux/freeze-map.md");
    try expectContains(validator, "Documentation/zigux/review-checklist.md");
    try expectContains(validator, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(validator, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(validator, "zigux/tests/phase15_build.zig");
    try expectContains(validator, "no Architecture Council approval is currently recorded for a freeze-map status change");
}

test "shared documentation routes phase15 governance back to the validator-first packet" {
    const allocator = std.testing.allocator;
    const docs_readme = try readFile(allocator, repo_files.docs_readme);
    defer allocator.free(docs_readme);
    const review_checklist = try readFile(allocator, repo_files.review_checklist);
    defer allocator.free(review_checklist);
    const freeze_map = try readFile(allocator, repo_files.freeze_map);
    defer allocator.free(freeze_map);

    try expectContains(docs_readme, "Phase 15 notes");
    try expectContains(docs_readme, "scripts/zigux/check-phase15-docs-readme-alignment.py");
    try expectContains(docs_readme, "scripts/zigux/check-phase15-architecture-council-packet.py");
    try expectContains(docs_readme, "scripts/zigux/validate-phase15.py");
    try expectContains(docs_readme, "no Architecture Council approval");

    try expectContains(review_checklist, "if a freeze-map anchor is entering Architecture Council status review");
    try expectContains(review_checklist, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(review_checklist, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(review_checklist, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(review_checklist, "scripts/zigux/validate-phase15.py");

    try expectContains(freeze_map, "freeze-map status-change requests must route through");
    try expectContains(freeze_map, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-freeze-map-governance.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
}

test "architecture council packet stays before validator aggregation" {
    const allocator = std.testing.allocator;
    const validator = try readFile(allocator, repo_files.validator);
    defer allocator.free(validator);
    const architecture_checker = try readFile(allocator, repo_files.architecture_checker);
    defer allocator.free(architecture_checker);

    try expectBefore(
        validator,
        "scripts/zigux/check-phase15-architecture-council-packet.py",
        "scripts/zigux/check-phase15-readiness-gate-packet.py",
    );
    try expectContains(architecture_checker, "PHASE15_STATUS=architecture_council_review_process_landed");
    try expectContains(architecture_checker, "Documentation/zigux/phase15-architecture-council-decision-index.md");
    try expectContains(architecture_checker, "approved status-bucket changes recorded on current `master`: none");
    try expectContains(architecture_checker, "stay-in-C closeout decision records recorded on current `master`: none");
}

const std = @import("std");

const read_limit = 512 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(read_limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "review checklist names the current Phase 1 closure packet" {
    const allocator = std.testing.allocator;

    const checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(checklist);

    for ([_][]const u8{
        "if the change touches the shared Phase 1 host-tools closure packet",
        "Documentation/zigux/phase1-closure.md",
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
        "Documentation/zigux/README.md",
        "Documentation/zigux/review-checklist.md",
        "scripts/zigux/README.md",
        "scripts/zigux/validate-phase1-closure.py",
        "scripts/zigux/check-phase1-string-review-packet.py",
        "scripts/zigux/check-phase1-direct-owner-markers.py",
        "scripts/zigux/check-phase1-bench.py",
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "zigux/tests/README.md",
        "zigux/tests/build.zig",
        "zigux/tests/phase1_host_tools_smoke.zig",
        ".github/workflows/zigux-bootstrap.yml",
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        "current closed-helper reminder packet",
    }) |marker| {
        try expectContains(checklist, marker);
    }
}

test "review checklist keeps route-summary evidence adjacent and older routes historical" {
    const allocator = std.testing.allocator;

    const checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(checklist);

    for ([_][]const u8{
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
        "scripts/zigux/check-phase1-route-summary-counts.py",
        "make -C zigux phase1-route-summary",
        "zigux/Makefile",
        "adjacent Phase 1 route-summary evidence",
        "returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families",
        "older validator-first, parity, bench-route, and replay names stay framed as historical packet members",
    }) |marker| {
        try expectContains(checklist, marker);
    }

    try expectNotContains(checklist, "PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master");
    try expectNotContains(checklist, "restore the missing phase1 closure note first");
}

test "review checklist stays aligned with closure note and validator authority" {
    const allocator = std.testing.allocator;

    const checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(checklist);

    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);

    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    for ([_][]const u8{
        "Documentation/zigux/review-checklist.md",
        "scripts/zigux/validate-phase1-closure.py",
        "scripts/zigux/check-phase1-string-review-packet.py",
        "scripts/zigux/check-phase1-direct-owner-markers.py",
        "scripts/zigux/check-phase1-bench.py",
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "zigux/tests/fixtures/phase1_helper_manifest.json",
    }) |marker| {
        try expectContains(checklist, marker);
        try expectContains(closure_note, marker);
    }

    for ([_][]const u8{
        "REVIEW_CHECKLIST_REL = Path(\"Documentation/zigux/review-checklist.md\")",
        "REQUIRED_FILES",
        "EXPECTED_CLOSURE_MARKERS",
        "FORBIDDEN_CLOSURE_MARKERS",
        "PHASE1_CLOSURE_REL",
        "SCRIPTS_README_REL",
        "TESTS_README_REL",
    }) |marker| {
        try expectContains(validator, marker);
    }
}

test "review checklist remains paired with the shared reminder surfaces" {
    const allocator = std.testing.allocator;

    const checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(checklist);

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);

    const scripts_root = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_root);

    const tests_root = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_root);

    for ([_][]const u8{
        "Documentation/zigux/review-checklist.md",
        "scripts/zigux/README.md",
        "zigux/tests/README.md",
        "the current Phase 1 reminder packet",
        "the nine shared-replay parked helpers",
        "bitmap, find_bit, rbtree, and string",
    }) |marker| {
        try expectContains(checklist, marker);
        try expectContains(docs_root, marker);
    }

    for ([_][]const u8{
        "Documentation/zigux/review-checklist.md",
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    }) |marker| {
        try expectContains(scripts_root, marker);
        try expectContains(tests_root, marker);
    }
}

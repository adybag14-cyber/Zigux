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

test "docs root keeps the current Phase 1 closure packet explicit" {
    const allocator = std.testing.allocator;

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);

    for ([_][]const u8{
        "Phase 1 notes",
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
        "Documentation/zigux/phase1-closure.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/README.md",
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        "scripts/zigux/README.md",
        "scripts/zigux/validate-phase1-closure.py",
        "scripts/zigux/check-phase1-string-review-packet.py",
        "scripts/zigux/check-phase1-direct-owner-markers.py",
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "scripts/zigux/check-phase1-bench.py",
        "keep the live owner map, the restored closure note and closure validator",
        "the parked shared-replay-versus-direct-anchor split",
        "the shipped bench checker",
        "the current Phase 1 reminder packet explicit from the docs root",
    }) |marker| {
        try expectContains(docs_root, marker);
    }
}

test "docs root parks older Phase 1 companions as historical gaps" {
    const allocator = std.testing.allocator;

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);

    for ([_][]const u8{
        "repeated authenticated reads on current `master` still return missing",
        "scripts/zigux/install-zig.py",
        "scripts/zigux/check-phase1-installer-review-surfaces.py",
        "scripts/zigux/check-phase1-installer-companion-checks.py",
        "scripts/zigux/validate-phase1.py",
        "scripts/zigux/check-phase1-parity.py",
        "zigux/tests/phase1_bench.zig",
        "zigux/tests/fixtures/phase1_bench_expectations.json",
        "make -C zigux phase1-validate",
        "make -C zigux phase1-test",
        "make -C zigux phase1-bench",
        "make -C zigux phase1",
        "historical packet members",
        "while `zigux/Makefile` is current repo evidence again",
    }) |marker| {
        try expectContains(docs_root, marker);
    }

    try expectNotContains(docs_root, "PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master");
    try expectNotContains(docs_root, "restore the missing phase1 closure note first");
}

test "docs root stays aligned with closure note and validator authority" {
    const allocator = std.testing.allocator;

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);

    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);

    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    for ([_][]const u8{
        "Documentation/zigux/README.md",
        "Documentation/zigux/review-checklist.md",
        "scripts/zigux/README.md",
        "scripts/zigux/check-phase1-string-review-packet.py",
        "scripts/zigux/check-phase1-direct-owner-markers.py",
        "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "scripts/zigux/check-phase1-bench.py",
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "scripts/zigux/validate-phase1-closure.py",
        "zigux/tests/README.md",
        "zigux/tests/build.zig",
        "zigux/tests/phase1_helpers.zig",
        "zigux/tests/phase1_helpers_build.zig",
        "zigux/tests/phase1_host_tools_smoke.zig",
        ".github/workflows/zigux-bootstrap.yml",
        "zigux/tests/fixtures/phase1_helper_manifest.json",
    }) |marker| {
        try expectContains(docs_root, marker);
        try expectContains(closure_note, marker);
    }

    for ([_][]const u8{
        "DOCS_ROOT_REL = Path(\"Documentation/zigux/README.md\")",
        "REVIEW_CHECKLIST_REL = Path(\"Documentation/zigux/review-checklist.md\")",
        "SCRIPTS_README_REL = Path(\"scripts/zigux/README.md\")",
        "SHARED_REMINDER_CHECKER_REL = Path(\"scripts/zigux/check-phase1-shared-reminder-packet.py\")",
        "TESTS_README_REL = Path(\"zigux/tests/README.md\")",
        "EXPECTED_CLOSURE_MARKERS",
        "FORBIDDEN_CLOSURE_MARKERS",
    }) |marker| {
        try expectContains(validator, marker);
    }
}

test "docs root preserves helper-family split and current replay commands" {
    const allocator = std.testing.allocator;

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);

    const lane_note = try readRepoFile(allocator, "Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    defer allocator.free(lane_note);

    for ([_][]const u8{
        "the nine shared-replay parked helpers reopen only for packet drift",
        "bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors",
        "python3 scripts/zigux/validate-phase1-closure.py",
        "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "python3 scripts/zigux/check-phase1-bench.py --self-test",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "without widening it back into the older closure-side or installer-companion stack",
    }) |marker| {
        try expectContains(docs_root, marker);
    }

    for ([_][]const u8{
        "PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig",
        "PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig",
        "PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py",
    }) |marker| {
        try expectContains(lane_note, marker);
    }
}

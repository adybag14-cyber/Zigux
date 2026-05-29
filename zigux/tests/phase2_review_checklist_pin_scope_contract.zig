const std = @import("std");
const testing = std.testing;

const review_checklist_path = "Documentation/zigux/review-checklist.md";
const bootstrap_notes_path = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md";
const tests_readme_path = "zigux/tests/README.md";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(4 * 1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "review checklist keeps phase2 pin-scope prompt anchored" {
    const allocator = testing.allocator;
    const review_checklist = try readFile(allocator, review_checklist_path);
    defer allocator.free(review_checklist);

    try expectContains(review_checklist, "if the change touches the shared Phase 2 toolchain pin-scope packet");
    try expectContains(review_checklist, "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`");
    try expectContains(review_checklist, "`Documentation/zigux/review-checklist.md`");
    try expectContains(review_checklist, "`zigux/tests/README.md`");
    try expectContains(review_checklist, "`scripts/zigux/check-phase2-toolchain-pin-scope.py`");
    try expectContains(review_checklist, "`scripts/zigux/check-zig-toolchain.py`");
    try expectContains(review_checklist, "current pinned-channel reminder packet");
}

test "phase2 pin-scope route roster stays current in the review checklist" {
    const allocator = testing.allocator;
    const review_checklist = try readFile(allocator, review_checklist_path);
    defer allocator.free(review_checklist);

    try expectContains(review_checklist, "`python3 scripts/zigux/check-zig-toolchain.py --self-test`");
    try expectContains(review_checklist, "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`");
    try expectContains(review_checklist, "`make -C zigux phase2-toolchain`");
    try expectContains(review_checklist, "`make -C zigux phase2-tools`");
    try expectContains(review_checklist, "`make -C zigux phase2-kconfig`");
    try expectContains(review_checklist, "`make -C zigux phase2-cross`");
    try expectContains(review_checklist, "`make -C zigux phase2-validate`");
    try expectContains(review_checklist, "`make -C zigux phase2`");
    try expectContains(review_checklist, "current rematerialized Phase 2 routes");
    try expectContains(review_checklist, "instead of treating those route names as missing-current-master gaps");
}

test "pin-scope packet remains mirrored by bootstrap notes and tests root" {
    const allocator = testing.allocator;
    const bootstrap_notes = try readFile(allocator, bootstrap_notes_path);
    defer allocator.free(bootstrap_notes);
    const tests_readme = try readFile(allocator, tests_readme_path);
    defer allocator.free(tests_readme);

    try expectContains(bootstrap_notes, "`scripts/zigux/check-phase2-toolchain-pin-scope.py`");
    try expectContains(bootstrap_notes, "`scripts/zigux/check-zig-toolchain.py`");
    try expectContains(bootstrap_notes, "`python3 scripts/zigux/check-zig-toolchain.py --self-test`");
    try expectContains(bootstrap_notes, "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`");
    try expectContains(bootstrap_notes, "`make -C zigux phase2-toolchain`");
    try expectContains(bootstrap_notes, "`make -C zigux phase2-tools`");
    try expectContains(bootstrap_notes, "`make -C zigux phase2-kconfig`");
    try expectContains(bootstrap_notes, "`make -C zigux phase2-cross`");
    try expectContains(bootstrap_notes, "`make -C zigux phase2-validate`");
    try expectContains(bootstrap_notes, "aggregate `phase2` route");

    try expectContains(tests_readme, "`scripts/zigux/check-phase2-toolchain-pin-scope.py`");
    try expectContains(tests_readme, "`python3 scripts/zigux/check-zig-toolchain.py --self-test`");
    try expectContains(tests_readme, "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`");
    try expectContains(tests_readme, "Keep the current toolchain self-check and replay surface explicit");
}

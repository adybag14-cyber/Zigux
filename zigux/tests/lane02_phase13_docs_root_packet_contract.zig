const std = @import("std");
const testing = std.testing;

const max_doc_bytes = 1024 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_doc_bytes),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "docs root keeps the Phase 13 contributor packet explicit" {
    const allocator = testing.allocator;
    const readme = try readRepoFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(readme);

    try requireContains(readme, "Phase 13 notes");
    try requireContains(readme, "`Documentation/zigux/phase13-contributor-workflow-guide.md`");
    try requireContains(readme, "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`");
    try requireContains(readme, "`Documentation/zigux/phase13-release-coordination-matrix.md`");
    try requireContains(readme, "`Documentation/zigux/phase13-release-notes-survey.md`");
    try requireContains(readme, "`Documentation/zigux/phase13-roadmap-traceability.md`");
    try requireContains(readme, "`Documentation/zigux/phase13-shared-summary-guard-gap.md`");
    try requireContains(readme, "`Documentation/zigux/phase13-notifier-summary-gap.md`");
    try requireContains(readme, "`scripts/zigux/check-phase13-shared-summary-surfaces.py`");
    try requireContains(readme, "`scripts/zigux/check-phase13-tests-readme-alignment.py`");
    try requireContains(readme, "`scripts/zigux/validate-phase13-release.py`");
    try requireContains(readme, "stable contributor-facing handle");
    try requireContains(readme, "`make -C zigux phase13-validate`");
    try requireContains(readme, "`make -C zigux phase13`");
    try requireContains(readme, "repo-reality gaps");
}

test "review checklist and workflow guide keep the stable handle bounded" {
    const allocator = testing.allocator;
    const checklist = try readRepoFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(checklist);
    const workflow = try readRepoFile(allocator, "Documentation/zigux/phase13-contributor-workflow-guide.md");
    defer allocator.free(workflow);

    try requireContains(checklist, "if the change touches the shared Phase 13 shared-helper packet");
    try requireContains(checklist, "`Documentation/zigux/phase13-contributor-workflow-guide.md`");
    try requireContains(checklist, "`scripts/zigux/README.md`");
    try requireContains(checklist, "`zigux/tests/README.md`");
    try requireContains(checklist, "stable contributor-facing handle");
    try requireContains(checklist, "adjacent notifier evidence");
    try requireContains(checklist, "repo-reality gaps");

    try requireContains(workflow, "## Stable Contributor-Facing Handle");
    try requireContains(workflow, "1. `Documentation/zigux/phase13-contributor-workflow-guide.md`");
    try requireContains(workflow, "2. `scripts/zigux/README.md`");
    try requireContains(workflow, "3. `zigux/tests/README.md`");
    try requireContains(workflow, "Docs-root companion rule");
    try requireContains(workflow, "shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`");
    try requireContains(workflow, "tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`");
    try requireContains(workflow, "release-discipline validator: `python3 scripts/zigux/validate-phase13-release.py`");
    try requireContains(workflow, "not as the stable contributor-facing handle itself");
    try requireContains(workflow, "repo-reality gaps");
}

test "Phase 13 helper split and notifier boundary stay explicit" {
    const allocator = testing.allocator;
    const sequencing = try readRepoFile(allocator, "Documentation/zigux/phase13-shared-helper-lane-sequencing.md");
    defer allocator.free(sequencing);
    const matrix = try readRepoFile(allocator, "Documentation/zigux/phase13-release-coordination-matrix.md");
    defer allocator.free(matrix);

    for ([_][]const u8{
        "`fs/libfs.c`",
        "`lib/devres.c`",
        "`security/landlock/ruleset.c`",
        "`security/landlock/syscalls.c`",
    }) |anchor| {
        try requireContains(sequencing, anchor);
        try requireContains(matrix, anchor);
    }

    try requireContains(sequencing, "not a fifth shared-helper anchor");
    try requireContains(sequencing, "do not treat `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13` as shipped evidence");
    try requireContains(sequencing, "`Documentation/zigux/phase13-notifier-list-survey.md`");
    try requireContains(sequencing, "`scripts/zigux/check-phase13-notifier-packet.py`");
    try requireContains(sequencing, "`zigux/tests/phase13_notifier_list_manifest.json`");
    try requireContains(sequencing, "`zigux/helpers/list_view.zig`");
    try requireContains(sequencing, "`zigux/helpers/hlist_view.zig`");
    try requireNotContains(sequencing, "notifier evidence owns a fifth shared-helper anchor");

    try requireContains(matrix, "PHASE13_STATUS=active");
    try requireContains(matrix, "PHASE13_RELEASE_CLOSED=no");
    try requireContains(matrix, "Keep the Makefile-backed route family recorded as repo-reality gaps");
    try requireContains(matrix, "does not promote adjacent notifier evidence into a fifth helper anchor");
}

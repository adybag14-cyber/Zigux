const std = @import("std");

fn readAlloc(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase15 docs-root reviewability keeps the current handoff alignment explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs_readme = try readAlloc(io_instance.io(), "Documentation/zigux/README.md", 40 * 1024);
    defer std.testing.allocator.free(docs_readme);

    const readiness_doc = try readAlloc(io_instance.io(), "Documentation/zigux/phase15-readiness-gate-survey.md", 16 * 1024);
    defer std.testing.allocator.free(readiness_doc);

    const handoff_doc = try readAlloc(io_instance.io(), "Documentation/zigux/phase15-handoff-next-steps-survey.md", 16 * 1024);
    defer std.testing.allocator.free(handoff_doc);

    try expectContains(docs_readme, "Phase 15 notes");
    try expectContains(docs_readme, "phase15-freeze-map-governance.md");
    try expectContains(docs_readme, "phase15-architecture-council-review-process.md");
    try expectContains(docs_readme, "phase15-parity-scorecard.md");
    try expectContains(docs_readme, "phase15-indefinite-c-policy.md");
    try expectContains(docs_readme, "phase15-readiness-gate-survey.md");
    try expectContains(docs_readme, "phase15-handoff-next-steps-survey.md");
    try expectContains(docs_readme, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(docs_readme, "phase15-evidence-archives/");
    try expectContains(docs_readme, "python3 scripts/zigux/validate-phase15.py");
    try expectContains(docs_readme, "make -C zigux phase15-validate");
    try expectContains(docs_readme, "zigux/tests/phase15_build.zig");
    try expectContains(docs_readme, "make -C zigux phase15");
    try expectContains(docs_readme, "only remaining blocked work is the deep-core status-change evidence");
    try std.testing.expect(std.mem.indexOf(u8, docs_readme, "remaining broader replay drift on current `master`") == null);

    try expectContains(readiness_doc, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(readiness_doc, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectContains(readiness_doc, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(readiness_doc, "python3 scripts/zigux/validate-phase15.py");
    try expectContains(readiness_doc, "make -C zigux phase15-validate");
    try expectContains(readiness_doc, "make -C zigux phase15");
    try expectContains(readiness_doc, "zigux/tests/phase15_docs_root_reviewability.zig");
    try expectContains(readiness_doc, "docs-root Phase 15 summary now matches the dedicated readiness and handoff packet");
    try expectContains(readiness_doc, "phase15-docs-root-summary-alignment");
    try expectContains(readiness_doc, "phase15-deep-core-status-change-blocker");

    try expectContains(handoff_doc, "Documentation/zigux/phase15-freeze-map-governance.md");
    try expectContains(handoff_doc, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(handoff_doc, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectContains(handoff_doc, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(handoff_doc, "python3 scripts/zigux/validate-phase15.py");
    try expectContains(handoff_doc, "make -C zigux phase15-validate");
    try expectContains(handoff_doc, "zigux/tests/phase15_docs_root_reviewability.zig");
    try expectContains(handoff_doc, "make -C zigux phase15");
    try expectContains(handoff_doc, "zig build test --build-file zigux/tests/phase15_build.zig");
    try expectContains(handoff_doc, "docs-root release evidence now matches the dedicated maintenance packet");
    try expectContains(handoff_doc, "phase15-docs-root-summary-alignment");
    try expectContains(handoff_doc, "phase15-deep-core-status-change-blocker");
}

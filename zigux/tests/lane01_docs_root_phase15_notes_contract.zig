const std = @import("std");

const docs_root_path = "Documentation/zigux/README.md";
const docs_root_path_from_tests = "../../Documentation/zigux/README.md";

const phase14_marker = "Phase 14 notes -";
const phase15_marker = "Phase 15 notes -";

const required_markers = [_][]const u8{
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-architecture-council-packet.py`",
    "`scripts/zigux/validate-phase15.py`",
    "the current docs-root Phase 15 reminder packet should stay parked on",
    "keep the Phase 15 reminder bounded below any Architecture Council approval claim",
    "any freeze-map status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`",
    "any claim that dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, or shared-CI Phase 15 routes are already shipped on current `master`",
    "the remaining shared-summary follow-through stays limited to the handoff note, the shared-summary gap note, the scripts-root reminder, and the tests-root reminder",
    "they do not own freeze-map decisions or broader route recovery by themselves",
};

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readDocsRoot() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, docs_root_path, std.testing.allocator, .limited(256 * 1024)) catch |err| switch (err) {
        error.FileNotFound => try std.Io.Dir.cwd().readFileAlloc(std.testing.io, docs_root_path_from_tests, std.testing.allocator, .limited(256 * 1024)),
        else => err,
    };
}

test "docs root Phase 15 reminder keeps governance surfaces explicit" {
    const docs_root = try readDocsRoot();
    defer std.testing.allocator.free(docs_root);

    inline for (required_markers) |marker| {
        try requireContains(docs_root, marker);
    }
}

test "docs root Phase 15 reminder remains after Phase 14" {
    const docs_root = try readDocsRoot();
    defer std.testing.allocator.free(docs_root);

    const phase14_index = std.mem.indexOf(u8, docs_root, phase14_marker) orelse return error.MissingPhase14Notes;
    const phase15_index = std.mem.indexOf(u8, docs_root, phase15_marker) orelse return error.MissingPhase15Notes;

    try std.testing.expect(phase14_index < phase15_index);
}

test "docs root Phase 15 reminder does not claim shipped shared routes" {
    const docs_root = try readDocsRoot();
    defer std.testing.allocator.free(docs_root);

    try requireContains(docs_root, "dedicated `make -C zigux phase15-validate`");
    try requireContains(docs_root, "shared-CI Phase 15 routes are already shipped on current `master`");
}

const std = @import("std");
const testing = std.testing;

const validator_path = "scripts/zigux/validate-phase1-closure.py";
const closure_note_path = "Documentation/zigux/phase1-closure.md";
const docs_readme_path = "Documentation/zigux/README.md";
const scripts_readme_path = "scripts/zigux/README.md";

const delegated_entries = [_]struct {
    const_name: []const u8,
    path: []const u8,
    label: []const u8,
}{
    .{
        .const_name = "STRING_REVIEW_CHECKER_REL",
        .path = "scripts/zigux/check-phase1-string-review-packet.py",
        .label = "phase1-string-review-packet",
    },
    .{
        .const_name = "FIND_BIT_REVIEW_CHECKER_REL",
        .path = "scripts/zigux/check-phase1-find-bit-review-packet.py",
        .label = "phase1-find-bit-review-packet",
    },
    .{
        .const_name = "RBTREE_REVIEW_CHECKER_REL",
        .path = "scripts/zigux/check-phase1-rbtree-review-packet.py",
        .label = "phase1-rbtree-review-packet",
    },
    .{
        .const_name = "DIRECT_OWNER_CHECKER_REL",
        .path = "scripts/zigux/check-phase1-direct-owner-markers.py",
        .label = "phase1-direct-owner-markers",
    },
    .{
        .const_name = "DIRECT_ANCHOR_MANIFEST_GATE_REL",
        .path = "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        .label = "phase1-direct-anchor-manifest-gate",
    },
    .{
        .const_name = "ROUTE_SUMMARY_CHECKER_REL",
        .path = "scripts/zigux/check-phase1-route-summary-counts.py",
        .label = "phase1-route-summary-counts",
    },
    .{
        .const_name = "FIND_BIT_BENCH_ANCHOR_CHECKER_REL",
        .path = "scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        .label = "phase1-find-bit-bench-anchors",
    },
    .{
        .const_name = "BITMAP_DIRECT_ANCHOR_CHECKER_REL",
        .path = "scripts/zigux/check-phase1-bitmap-direct-anchors.py",
        .label = "phase1-bitmap-direct-anchors",
    },
    .{
        .const_name = "SHARED_REMINDER_CHECKER_REL",
        .path = "scripts/zigux/check-phase1-shared-reminder-packet.py",
        .label = "phase1-shared-reminder-packet",
    },
};

const delegated_roster_markers = [_][]const u8{
    "(STRING_REVIEW_CHECKER_REL, \"phase1-string-review-packet\")",
    "(FIND_BIT_REVIEW_CHECKER_REL, \"phase1-find-bit-review-packet\")",
    "(RBTREE_REVIEW_CHECKER_REL, \"phase1-rbtree-review-packet\")",
    "(DIRECT_OWNER_CHECKER_REL, \"phase1-direct-owner-markers\")",
    "(DIRECT_ANCHOR_MANIFEST_GATE_REL, \"phase1-direct-anchor-manifest-gate\")",
    "(ROUTE_SUMMARY_CHECKER_REL, \"phase1-route-summary-counts\")",
    "(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, \"phase1-find-bit-bench-anchors\")",
    "(BITMAP_DIRECT_ANCHOR_CHECKER_REL, \"phase1-bitmap-direct-anchors\")",
    "(SHARED_REMINDER_CHECKER_REL, \"phase1-shared-reminder-packet\")",
};

fn requireContainsOnce(haystack: []const u8, needle: []const u8) !void {
    try testing.expectEqual(@as(usize, 1), std.mem.count(u8, haystack, needle));
}

fn requireOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var search_start: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, haystack[search_start..], needle) orelse {
            std.debug.print("missing or out-of-order marker: {s}\n", .{needle});
            return error.MissingMarker;
        };
        search_start += relative + needle.len;
    }
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(1024 * 1024));
}

test "closure validator names the exact delegated checker files once" {
    const validator_source = try readRepoFile(testing.allocator, validator_path);
    defer testing.allocator.free(validator_source);

    for (delegated_entries) |entry| {
        var const_marker: [160]u8 = undefined;
        const rendered = try std.fmt.bufPrint(
            &const_marker,
            "{s} = Path(\"{s}\")",
            .{ entry.const_name, entry.path },
        );
        try requireContainsOnce(validator_source, rendered);
    }
}

test "closure validator keeps delegated checker roster ordered and complete" {
    const validator_source = try readRepoFile(testing.allocator, validator_path);
    defer testing.allocator.free(validator_source);

    const roster_start = std.mem.indexOf(u8, validator_source, "DELEGATED_CHECKERS = (") orelse
        return error.MissingDelegatedCheckerRoster;
    const roster_end_relative = std.mem.indexOf(u8, validator_source[roster_start..], ")\n\n\ndef repo_root") orelse
        return error.MissingDelegatedCheckerRosterEnd;
    const roster = validator_source[roster_start .. roster_start + roster_end_relative];

    try requireContainsOnce(validator_source, "DELEGATED_CHECKERS = (");
    try testing.expectEqual(delegated_entries.len, std.mem.count(u8, roster, "),\n"));

    inline for (delegated_roster_markers) |marker| {
        try requireContainsOnce(roster, marker);
    }

    try requireOrdered(roster, &delegated_roster_markers);
}

test "closure reminder surfaces keep delegated validation distinct from older Phase 1 wrappers" {
    const closure_note = try readRepoFile(testing.allocator, closure_note_path);
    defer testing.allocator.free(closure_note);
    const docs_readme = try readRepoFile(testing.allocator, docs_readme_path);
    defer testing.allocator.free(docs_readme);
    const scripts_readme = try readRepoFile(testing.allocator, scripts_readme_path);
    defer testing.allocator.free(scripts_readme);

    try requireContainsOnce(
        closure_note,
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    );
    try requireContainsOnce(
        closure_note,
        "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    );
    try requireContainsOnce(
        scripts_readme,
        "`scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet",
    );
    try requireContainsOnce(
        docs_readme,
        "`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks",
    );

    try testing.expectEqual(@as(usize, 0), std.mem.count(
        u8,
        closure_note,
        "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    ));
    try testing.expectEqual(@as(usize, 0), std.mem.count(
        u8,
        scripts_readme,
        "make -C zigux phase1-validate` replay",
    ));
}

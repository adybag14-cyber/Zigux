const std = @import("std");

const GuardKind = enum {
    helper_local_review,
    closure_validator_route,
    benchmark_guard,
    direct_anchor_manifest_gate,
};

const ClosureReviewGuard = struct {
    marker: []const u8,
    command: []const u8,
    kind: GuardKind,
};

const closure_review_guards = [_]ClosureReviewGuard{
    .{
        .marker = "PHASE1_STRING_REVIEW_GUARD",
        .command = "python3 scripts/zigux/check-phase1-string-review-packet.py",
        .kind = .helper_local_review,
    },
    .{
        .marker = "PHASE1_FIND_BIT_REVIEW_GUARD",
        .command = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        .kind = .helper_local_review,
    },
    .{
        .marker = "PHASE1_RBTREE_REVIEW_GUARD",
        .command = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
        .kind = .helper_local_review,
    },
    .{
        .marker = "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE",
        .command = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        .kind = .direct_anchor_manifest_gate,
    },
    .{
        .marker = "PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD",
        .command = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        .kind = .benchmark_guard,
    },
};

const benchmark_closure_markers = [_][]const u8{
    "PHASE1_FIND_BIT_BENCH_GUARD",
    "PHASE1_RBTREE_BENCH_GUARD",
};

const closure_validator_marker = "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py";

fn hasPrefix(haystack: []const u8, needle: []const u8) bool {
    return std.mem.startsWith(u8, haystack, needle);
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn countKind(kind: GuardKind) usize {
    var count: usize = 0;
    for (closure_review_guards) |guard| {
        if (guard.kind == kind) count += 1;
    }
    return count;
}

test "phase1 closure review roster keeps helper-local guard commands explicit" {
    try std.testing.expectEqual(@as(usize, 5), closure_review_guards.len);
    try std.testing.expectEqual(@as(usize, 3), countKind(.helper_local_review));

    for (closure_review_guards) |guard| {
        try std.testing.expect(hasPrefix(guard.marker, "PHASE1_"));
        try std.testing.expect(contains(guard.command, "scripts/zigux/check-phase1-"));
        try std.testing.expect(contains(guard.command, ".py"));
    }
}

test "phase1 closure review roster separates validator route from helper-local guards" {
    try std.testing.expect(contains(closure_validator_marker, "validate-phase1-closure.py"));

    for (closure_review_guards) |guard| {
        try std.testing.expect(!contains(guard.command, "validate-phase1-closure.py"));
        try std.testing.expect(guard.kind != .closure_validator_route);
    }
}

test "phase1 closure review roster keeps direct anchors and bench anchors distinct" {
    try std.testing.expectEqual(@as(usize, 1), countKind(.direct_anchor_manifest_gate));
    try std.testing.expectEqual(@as(usize, 1), countKind(.benchmark_guard));

    try std.testing.expect(contains(closure_review_guards[3].command, "direct-anchor-manifest-gate"));
    try std.testing.expect(contains(closure_review_guards[4].command, "find-bit-bench-anchors"));
    try std.testing.expect(!std.mem.eql(u8, closure_review_guards[3].command, closure_review_guards[4].command));
}

test "phase1 closure review roster carries both benchmark guard families" {
    try std.testing.expectEqual(@as(usize, 2), benchmark_closure_markers.len);

    for (benchmark_closure_markers) |marker| {
        try std.testing.expect(hasPrefix(marker, "PHASE1_"));
        try std.testing.expect(contains(marker, "BENCH_GUARD"));
    }
}

test "phase1 closure review roster does not reopen unrelated closure stacks" {
    const forbidden = [_][]const u8{
        "phase2",
        "workflow-packet",
        "older validator-first",
        "replay-side closure stack",
    };

    for (closure_review_guards) |guard| {
        for (forbidden) |needle| {
            try std.testing.expect(!contains(guard.marker, needle));
            try std.testing.expect(!contains(guard.command, needle));
        }
    }
}

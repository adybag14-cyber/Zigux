const std = @import("std");

const NextStepKind = enum {
    shared_reminder_surface,
    helper_family_tie_breaker,
    validator_first_reopen,
    replay_side_closure_stack,
};

const ClosureSurface = struct {
    name: []const u8,
    marker: []const u8,
};

const phase1_next_safe_step =
    "PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker " ++
    "against the restored closure note, the closure validator, the shared tests-root smoke route, " ++
    "and the helper-specific next_safe_step_note entries in the committed manifest rather than " ++
    "widening back into the older validator-first or replay-side closure stack.";

const allowed_next_steps = [_]NextStepKind{
    .shared_reminder_surface,
    .helper_family_tie_breaker,
};

const rejected_next_steps = [_]NextStepKind{
    .validator_first_reopen,
    .replay_side_closure_stack,
};

const required_surfaces = [_]ClosureSurface{
    .{ .name = "closure note", .marker = "restored closure note" },
    .{ .name = "closure validator", .marker = "closure validator" },
    .{ .name = "shared tests-root smoke route", .marker = "shared tests-root smoke route" },
    .{ .name = "manifest next safe step notes", .marker = "helper-specific next_safe_step_note entries" },
};

const forbidden_reopen_cues = [_][]const u8{
    "validator-first",
    "replay-side closure stack",
};

fn hasNeedle(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn isAllowedNextStep(kind: NextStepKind) bool {
    return switch (kind) {
        .shared_reminder_surface, .helper_family_tie_breaker => true,
        .validator_first_reopen, .replay_side_closure_stack => false,
    };
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: []const u8 = haystack;

    while (std.mem.indexOf(u8, cursor, needle)) |offset| {
        count += 1;
        cursor = cursor[offset + needle.len ..];
    }

    return count;
}

test "phase1 next safe step keeps exactly two forward paths" {
    try std.testing.expect(hasNeedle(phase1_next_safe_step, "sync one shared reminder surface"));
    try std.testing.expect(hasNeedle(phase1_next_safe_step, "one helper-family tie-breaker"));
    try std.testing.expectEqual(@as(usize, 2), allowed_next_steps.len);

    for (allowed_next_steps) |kind| {
        try std.testing.expect(isAllowedNextStep(kind));
    }
}

test "phase1 next safe step remains tied to closure validation surfaces" {
    try std.testing.expectEqual(@as(usize, 4), required_surfaces.len);

    for (required_surfaces) |surface| {
        try std.testing.expect(surface.name.len > 0);
        try std.testing.expect(hasNeedle(phase1_next_safe_step, surface.marker));
    }
}

test "phase1 next safe step keeps manifest notes in scope" {
    try std.testing.expect(hasNeedle(phase1_next_safe_step, "committed manifest"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(phase1_next_safe_step, "next_safe_step_note"));
    try std.testing.expect(!hasNeedle(phase1_next_safe_step, "uncommitted manifest"));
}

test "phase1 next safe step rejects older closure-stack reopening" {
    try std.testing.expectEqual(@as(usize, 2), rejected_next_steps.len);

    for (rejected_next_steps) |kind| {
        try std.testing.expect(!isAllowedNextStep(kind));
    }

    for (forbidden_reopen_cues) |cue| {
        try std.testing.expect(hasNeedle(phase1_next_safe_step, cue));
    }
    try std.testing.expect(hasNeedle(phase1_next_safe_step, "rather than widening back"));
}

test "phase1 next safe step remains a single closure-note marker" {
    try std.testing.expect(std.mem.startsWith(u8, phase1_next_safe_step, "PHASE1_NEXT_SAFE_STEP="));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(phase1_next_safe_step, "PHASE1_NEXT_SAFE_STEP="));
    try std.testing.expect(!hasNeedle(phase1_next_safe_step, "PHASE1_CLOSURE_VALIDATOR="));
}

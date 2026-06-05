const std = @import("std");
const options = @import("lane17_phase1_closure_review_marker_options");

const workflow = options.workflow_text;
const closure_note = options.closure_note_text;
const closure_validator = options.closure_validator_text;

const workflow_ladder = [_][]const u8{
    "Self-test current Phase 1 direct-owner checker",
    "Check current Phase 1 direct-owner markers",
    "Self-test current Phase 1 direct-anchor manifest gate",
    "Check current Phase 1 direct-anchor manifest gate",
    "Self-test current Phase 1 string review checker",
    "Check current Phase 1 string review packet",
    "Self-test current Phase 1 find-bit review checker",
    "Check current Phase 1 find-bit review packet",
    "Self-test current Phase 1 bitmap direct-anchor checker",
    "Check current Phase 1 bitmap direct-anchor packet",
    "Self-test current Phase 1 rbtree review checker",
    "Check current Phase 1 rbtree review packet",
    "Self-test current Phase 1 route summary checker",
    "Check current Phase 1 route summary packet",
    "Self-test current Phase 1 bench checker",
    "Check current Phase 1 bench packet",
    "Self-test current Phase 1 bench live-check workflow guard",
    "Check current Phase 1 bench live-check workflow guard packet",
    "Self-test current Phase 1 find-bit bench anchor checker",
    "Check current Phase 1 find-bit bench anchor packet",
    "Self-test current Phase 1 shared reminder checker",
    "Check current Phase 1 shared reminder packet",
    "Self-test current Phase 1 closure validator",
    "Check current Phase 1 closure packet",
};

const workflow_runs = [_][]const u8{
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\n",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n",
    "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test\n",
    "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\n",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test\n",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py\n",
    "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test\n",
    "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py\n",
    "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test\n",
    "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py\n",
    "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test\n",
    "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py\n",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n",
    "run: python3 scripts/zigux/validate-phase1-closure.py\n",
};

const closure_review_markers = [_][]const u8{
    "`PHASE1_BITMAP_COMPLEMENT_TAIL_REVIEW=helper-local complement-tail masking stays explicit through the direct bitmap tests",
    "`PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay owned by the shared Phase 1 parity fixture and replay",
    "`PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW=helper-local Linux-style find_next_or_bit tail and past-end alias proof plus find_*clump8 tail-byte and exhausted-caller-byte alias proof",
    "Current `master` also keeps the companion `cached_root_transition_serials` witness shared instead of helper-local only",
    "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route",
};

const validator_markers = [_][]const u8{
    "\"bitmap_partial_xor_review\"",
    "\"bitmap_complement_tail_review\"",
    "\"find_bit_linux_alias_tail_review\"",
    "\"direct_anchor_manifest_gate\"",
    "DIRECT_ANCHOR_MANIFEST_GATE_REL",
    "BITMAP_DIRECT_ANCHOR_CHECKER_REL",
    "FIND_BIT_REVIEW_CHECKER_REL",
    "RBTREE_REVIEW_CHECKER_REL",
    "SHARED_REMINDER_CHECKER_REL",
};

fn count(text: []const u8, needle: []const u8) usize {
    var total: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, text, index, needle)) |found| {
        total += 1;
        index = found + needle.len;
    }
    return total;
}

fn expectOnce(text: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), count(text, needle));
}

fn expectAbsent(text: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 0), count(text, needle));
}

test "Phase 1 workflow still runs the closure review ladder in order" {
    var previous_index: usize = 0;
    for (workflow_ladder) |step| {
        try expectOnce(workflow, step);
        const index = std.mem.indexOf(u8, workflow, step) orelse return error.MissingWorkflowStep;
        try std.testing.expect(index >= previous_index);
        previous_index = index + step.len;
    }

    for (workflow_runs) |run_line| {
        try expectOnce(workflow, run_line);
    }
}

test "workflow keeps closure validation before Phase 3 and smoke handoff" {
    const closure_index = std.mem.indexOf(u8, workflow, "Check current Phase 1 closure packet") orelse return error.MissingClosurePacketStep;
    const phase3_index = std.mem.indexOf(u8, workflow, "Self-test current Phase 3 interop packet") orelse return error.MissingPhase3Step;
    const smoke_index = std.mem.indexOf(u8, workflow, "Run current Phase 1 shared tests-root smoke") orelse return error.MissingSharedSmokeStep;
    try std.testing.expect(closure_index < phase3_index);
    try std.testing.expect(phase3_index < smoke_index);

    try expectAbsent(workflow, "run: make -C zigux phase1\n");
    try expectAbsent(workflow, "run: make -C zigux phase1-validate\n");
    try expectAbsent(workflow, "run: make -C zigux phase1-test\n");
    try expectAbsent(workflow, "run: make -C zigux phase1-bench\n");
    try expectAbsent(workflow, "validate-phase1.py");
}

test "closure note keeps newer review markers visible" {
    for (closure_review_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, closure_note, marker) != null);
    }

    try expectAbsent(closure_note, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
    try expectAbsent(closure_note, "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`");
}

test "closure validator knows the same review marker surface" {
    for (validator_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, closure_validator, marker) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, closure_validator, "DELEGATED_CHECKERS = (") != null);
    try std.testing.expect(std.mem.indexOf(u8, closure_validator, "PHASE1_CLOSURE_SELF_TEST=pass") != null);
}

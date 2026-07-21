const std = @import("std");
const workflow_options = @import("workflow_options");

const workflow_text = workflow_options.workflow_text;

const Marker = struct {
    label: []const u8,
    text: []const u8,
};

const phase3_shared_tests = Marker{
    .label = "phase3_shared_tests",
    .text = "      - name: Run current Phase 3 shared tests-root packet\n        run: zig build phase3-test --build-file zigux/tests/build.zig\n",
};

const phase3_dump = Marker{
    .label = "phase3_dump",
    .text = "      - name: Run current Phase 3 ABI dump replay\n        run: zig build phase3-dump --build-file zigux/tests/build.zig\n",
};

const phase1_smoke = Marker{
    .label = "phase1_smoke",
    .text = "      - name: Run current Phase 1 shared tests-root smoke\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
};

const phase4_warning_self_test = Marker{
    .label = "phase4_warning_self_test",
    .text = "      - name: Self-test current Phase 4 repo-reality warning checker\n        run: zig run scripts/zigux/check_phase4_repo_reality_warning.zig -- --self-test\n",
};

const phase4_warning_check = Marker{
    .label = "phase4_warning_check",
    .text = "      - name: Check current Phase 4 repo-reality warning packet\n        run: zig run scripts/zigux/check_phase4_repo_reality_warning.zig\n",
};

const phase4_reversible_self_test = Marker{
    .label = "phase4_reversible_self_test",
    .text = "      - name: Self-test current Phase 4 reversible-delivery pin checker\n        run: zig run scripts/zigux/check_phase4_reversible_delivery_pins.zig -- --self-test\n",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn requireOnce(marker: Marker) !usize {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow_text, marker.text));
    return std.mem.indexOf(u8, workflow_text, marker.text) orelse error.MissingWorkflowMarker;
}

fn requireBefore(left: Marker, right: Marker) !void {
    const left_index = try requireOnce(left);
    const right_index = try requireOnce(right);
    try std.testing.expect(left_index < right_index);
}

test "phase1 smoke remains the handoff between phase3 shared checks and phase4 warnings" {
    try requireBefore(phase3_shared_tests, phase3_dump);
    try requireBefore(phase3_dump, phase1_smoke);
    try requireBefore(phase1_smoke, phase4_warning_self_test);
    try requireBefore(phase4_warning_self_test, phase4_warning_check);
    try requireBefore(phase4_warning_check, phase4_reversible_self_test);
}

test "phase1 smoke handoff keeps the narrow shared route and does not widen to aggregate aliases" {
    const smoke_index = try requireOnce(phase1_smoke);
    const phase4_index = try requireOnce(phase4_warning_self_test);
    const handoff = workflow_text[smoke_index..phase4_index];

    try std.testing.expectEqual(@as(usize, 1), countOccurrences(handoff, "phase1-host-tools-smoke"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(handoff, "zig build smoke --build-file zigux/tests/build.zig"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(handoff, "zig build test --build-file zigux/tests/build.zig"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(handoff, "make -C zigux phase1"));
}

test "phase4 warning packet is the first post-phase1 workflow gate" {
    const smoke_index = try requireOnce(phase1_smoke);
    const warning_index = try requireOnce(phase4_warning_self_test);
    const post_smoke = workflow_text[smoke_index + phase1_smoke.text.len .. warning_index];

    try std.testing.expectEqual(@as(usize, 0), countOccurrences(post_smoke, "      - name:"));
    try requireBefore(phase4_warning_self_test, phase4_warning_check);
}

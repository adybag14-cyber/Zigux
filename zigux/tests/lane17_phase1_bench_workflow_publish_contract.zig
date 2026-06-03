const std = @import("std");
const testing = std.testing;

const Step = struct {
    name: []const u8,
    run: []const u8,
};

const bench_self_test = Step{
    .name = "Self-test current Phase 1 bench checker",
    .run = "python3 scripts/zigux/check-phase1-bench.py --self-test",
};

const bench_live_check = Step{
    .name = "Check current Phase 1 bench packet",
    .run = "python3 scripts/zigux/check-phase1-bench.py",
};

const find_bit_self_test = Step{
    .name = "Self-test current Phase 1 find-bit bench anchor checker",
    .run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
};

const find_bit_live_check = Step{
    .name = "Check current Phase 1 find-bit bench anchor packet",
    .run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
};

const current_missing_live_check =
    \\      - name: Self-test current Phase 1 bench checker
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
    \\
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    \\
    \\      - name: Check current Phase 1 find-bit bench anchor packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
;

const published_live_check =
    \\      - name: Self-test current Phase 1 bench checker
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
    \\
    \\      - name: Check current Phase 1 bench packet
    \\        run: python3 scripts/zigux/check-phase1-bench.py
    \\
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    \\
    \\      - name: Check current Phase 1 find-bit bench anchor packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
;

const duplicate_live_check =
    published_live_check ++
    \\
    \\      - name: Check current Phase 1 bench packet
    \\        run: python3 scripts/zigux/check-phase1-bench.py
    ;

const self_test_reused_for_live_check =
    \\      - name: Self-test current Phase 1 bench checker
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
    \\
    \\      - name: Check current Phase 1 bench packet
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
    \\
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    \\
    \\      - name: Check current Phase 1 find-bit bench anchor packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
;

const live_check_after_find_bit =
    \\      - name: Self-test current Phase 1 bench checker
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
    \\
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    \\
    \\      - name: Check current Phase 1 find-bit bench anchor packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
    \\
    \\      - name: Check current Phase 1 bench packet
    \\        run: python3 scripts/zigux/check-phase1-bench.py
;

fn blockFor(comptime step: Step) []const u8 {
    return "      - name: " ++ step.name ++ "\n        run: " ++ step.run;
}

fn endsStepAtBoundary(haystack: []const u8, end: usize) bool {
    return end == haystack.len or haystack[end] == '\n';
}

fn countStep(haystack: []const u8, comptime step: Step) usize {
    const needle = blockFor(step);
    var found: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative| {
        const absolute = offset + relative;
        const end = absolute + needle.len;
        if (endsStepAtBoundary(haystack, end)) {
            found += 1;
        }
        offset = end;
    }
    return found;
}

fn indexOfStep(workflow: []const u8, comptime step: Step) ?usize {
    return std.mem.indexOf(u8, workflow, blockFor(step));
}

fn requireOne(workflow: []const u8, comptime step: Step) !usize {
    const block = blockFor(step);
    try testing.expectEqual(@as(usize, 1), countStep(workflow, step));
    return std.mem.indexOf(u8, workflow, block).?;
}

fn requireAbsent(workflow: []const u8, comptime step: Step) !void {
    try testing.expectEqual(@as(usize, 0), countStep(workflow, step));
}

fn expectPublishedOrder(workflow: []const u8) !void {
    const bench_self_test_index = try requireOne(workflow, bench_self_test);
    const bench_live_check_index = try requireOne(workflow, bench_live_check);
    const find_bit_self_test_index = try requireOne(workflow, find_bit_self_test);
    const find_bit_live_check_index = try requireOne(workflow, find_bit_live_check);

    try testing.expect(bench_self_test_index < bench_live_check_index);
    try testing.expect(bench_live_check_index < find_bit_self_test_index);
    try testing.expect(find_bit_self_test_index < find_bit_live_check_index);
}

test "current master workflow slice still demonstrates the missing live bench packet gap" {
    try requireAbsent(current_missing_live_check, bench_live_check);
    try testing.expect(indexOfStep(current_missing_live_check, bench_self_test).? < indexOfStep(current_missing_live_check, find_bit_self_test).?);
}

test "published workflow splice requires the live bench packet before find-bit anchors" {
    try expectPublishedOrder(published_live_check);
}

test "duplicate live bench packet steps fail the exact-count contract" {
    try testing.expectEqual(@as(usize, 2), countStep(duplicate_live_check, bench_live_check));
}

test "live bench packet cannot reuse the self-test command" {
    try testing.expectEqual(@as(usize, 0), countStep(self_test_reused_for_live_check, bench_live_check));
    try testing.expect(std.mem.indexOf(u8, self_test_reused_for_live_check, "      - name: Check current Phase 1 bench packet\n        run: python3 scripts/zigux/check-phase1-bench.py --self-test") != null);
}

test "live bench packet must not drift after the find-bit anchor pair" {
    const bench_live_check_index = try requireOne(live_check_after_find_bit, bench_live_check);
    const find_bit_live_check_index = try requireOne(live_check_after_find_bit, find_bit_live_check);
    try testing.expect(find_bit_live_check_index < bench_live_check_index);
}

const std = @import("std");

const bench_self_test_name = "Self-test current Phase 1 bench checker";
const bench_live_check_name = "Check current Phase 1 bench packet";
const bench_self_test_command = "python3 scripts/zigux/check-phase1-bench.py --self-test";
const bench_live_check_command = "python3 scripts/zigux/check-phase1-bench.py";
const find_bit_self_test_name = "Self-test current Phase 1 find-bit bench anchor checker";

const expected_slice =
    \\      - name: Self-test current Phase 1 bench checker
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
    \\
    \\      - name: Check current Phase 1 bench packet
    \\        run: python3 scripts/zigux/check-phase1-bench.py
    \\
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
;

test "phase1 bench workflow command pair accepts intended live check slice" {
    try expectBenchCommandPair(expected_slice);
}

test "phase1 bench workflow command pair rejects missing live check" {
    const missing_live_check =
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    ;

    try std.testing.expectError(error.MissingBenchLiveCheckName, expectBenchCommandPair(missing_live_check));
}

test "phase1 bench workflow command pair rejects self-test command reused for live check" {
    const self_test_reused =
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    ;

    try std.testing.expectError(error.MissingBenchLiveCheckCommand, expectBenchCommandPair(self_test_reused));
}

test "phase1 bench workflow command pair rejects reordered live check" {
    const reordered_live_check =
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
        \\
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    ;

    try std.testing.expectError(error.BenchLiveCheckBeforeSelfTest, expectBenchCommandPair(reordered_live_check));
}

test "phase1 bench workflow command pair rejects duplicate live check" {
    const duplicate_live_check = expected_slice ++
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
    ;

    try std.testing.expectError(error.DuplicateBenchLiveCheckName, expectBenchCommandPair(duplicate_live_check));
}

fn expectBenchCommandPair(workflow_slice: []const u8) !void {
    const self_test_name_index = findUnique(workflow_slice, bench_self_test_name) orelse return error.MissingBenchSelfTestName;
    const live_check_name_count = countOccurrences(workflow_slice, bench_live_check_name);
    if (live_check_name_count == 0) return error.MissingBenchLiveCheckName;
    if (live_check_name_count > 1) return error.DuplicateBenchLiveCheckName;
    const live_check_name_index = std.mem.indexOf(u8, workflow_slice, bench_live_check_name).?;
    const find_bit_self_test_index = findUnique(workflow_slice, find_bit_self_test_name) orelse return error.MissingFindBitSelfTestName;

    if (live_check_name_index < self_test_name_index) return error.BenchLiveCheckBeforeSelfTest;
    if (find_bit_self_test_index < live_check_name_index) return error.FindBitSelfTestBeforeBenchLiveCheck;

    const self_test_command_index = std.mem.indexOf(u8, workflow_slice, bench_self_test_command) orelse return error.MissingBenchSelfTestCommand;
    const live_check_command_index = findExactLiveCommand(workflow_slice) orelse return error.MissingBenchLiveCheckCommand;

    if (self_test_command_index < self_test_name_index or live_check_name_index < self_test_command_index) {
        return error.BenchSelfTestCommandOutsideStep;
    }
    if (live_check_command_index < live_check_name_index or find_bit_self_test_index < live_check_command_index) {
        return error.BenchLiveCheckCommandOutsideStep;
    }
}

fn findUnique(haystack: []const u8, needle: []const u8) ?usize {
    const first_index = std.mem.indexOf(u8, haystack, needle) orelse return null;
    const after_first = haystack[first_index + needle.len ..];
    if (std.mem.indexOf(u8, after_first, needle) != null) {
        return null;
    }
    return first_index;
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var cursor: usize = 0;
    var count: usize = 0;

    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative_index| {
        count += 1;
        cursor += relative_index + needle.len;
    }

    return count;
}

fn findExactLiveCommand(workflow_slice: []const u8) ?usize {
    var cursor: usize = 0;
    var found_index: ?usize = null;

    while (std.mem.indexOf(u8, workflow_slice[cursor..], bench_live_check_command)) |relative_index| {
        const index = cursor + relative_index;
        const command_end = index + bench_live_check_command.len;
        const next_byte = if (command_end < workflow_slice.len) workflow_slice[command_end] else '\n';

        if (next_byte == '\n' or next_byte == '\r') {
            if (found_index != null) return null;
            found_index = index;
        }
        cursor = command_end;
    }

    return found_index;
}

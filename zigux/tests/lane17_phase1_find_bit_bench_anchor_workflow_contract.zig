const std = @import("std");

const bench_self_test_name = "Self-test current Phase 1 bench checker";
const find_bit_self_test_name = "Self-test current Phase 1 find-bit bench anchor checker";
const find_bit_self_test_run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test";
const find_bit_check_name = "Check current Phase 1 find-bit bench anchor packet";
const find_bit_check_run = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py";
const shared_reminder_self_test_name = "Self-test current Phase 1 shared reminder checker";

const WorkflowStep = struct {
    name: []const u8,
    run: []const u8,
};

const ParsedSteps = struct {
    steps: [8]WorkflowStep = undefined,
    count: usize = 0,

    fn append(self: *ParsedSteps, step: WorkflowStep) !void {
        if (self.count == self.steps.len) return error.TooManySteps;
        self.steps[self.count] = step;
        self.count += 1;
    }

    fn slice(self: *const ParsedSteps) []const WorkflowStep {
        return self.steps[0..self.count];
    }
};

const ContractError = error{
    TooManySteps,
    MissingBenchSelfTest,
    MissingFindBitBenchSelfTest,
    MissingFindBitBenchCheck,
    MissingSharedReminderSelfTest,
    DuplicateFindBitBenchSelfTest,
    DuplicateFindBitBenchCheck,
    FindBitSelfTestBeforeBenchSelfTest,
    FindBitCheckBeforeSelfTest,
    FindBitCheckAfterSharedReminder,
    FindBitSelfTestCommandDrift,
    FindBitCheckCommandDrift,
};

fn fieldValue(line: []const u8, prefix: []const u8) ?[]const u8 {
    const trimmed = std.mem.trimStart(u8, line, " ");
    if (!std.mem.startsWith(u8, trimmed, prefix)) return null;
    return std.mem.trim(u8, trimmed[prefix.len..], " ");
}

fn parseWorkflowSlice(text: []const u8) ContractError!ParsedSteps {
    var parsed = ParsedSteps{};
    var current_name: ?[]const u8 = null;

    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (fieldValue(line, "- name: ")) |name| {
            current_name = name;
            continue;
        }
        if (fieldValue(line, "run: ")) |run| {
            if (current_name) |name| {
                try parsed.append(.{ .name = name, .run = run });
                current_name = null;
            }
        }
    }

    return parsed;
}

fn findStep(steps: []const WorkflowStep, name: []const u8) ?usize {
    for (steps, 0..) |step, index| {
        if (std.mem.eql(u8, step.name, name)) return index;
    }
    return null;
}

fn countStep(steps: []const WorkflowStep, name: []const u8) usize {
    var count: usize = 0;
    for (steps) |step| {
        if (std.mem.eql(u8, step.name, name)) count += 1;
    }
    return count;
}

fn requireFindBitBenchWorkflowPair(text: []const u8) ContractError!void {
    const parsed = try parseWorkflowSlice(text);
    const steps = parsed.slice();
    const bench_index = findStep(steps, bench_self_test_name) orelse return ContractError.MissingBenchSelfTest;
    const find_bit_self_index = findStep(steps, find_bit_self_test_name) orelse return ContractError.MissingFindBitBenchSelfTest;
    const find_bit_check_index = findStep(steps, find_bit_check_name) orelse return ContractError.MissingFindBitBenchCheck;
    const shared_reminder_index = findStep(steps, shared_reminder_self_test_name) orelse return ContractError.MissingSharedReminderSelfTest;

    if (countStep(steps, find_bit_self_test_name) != 1) return ContractError.DuplicateFindBitBenchSelfTest;
    if (countStep(steps, find_bit_check_name) != 1) return ContractError.DuplicateFindBitBenchCheck;
    if (find_bit_self_index <= bench_index) return ContractError.FindBitSelfTestBeforeBenchSelfTest;
    if (find_bit_check_index <= find_bit_self_index) return ContractError.FindBitCheckBeforeSelfTest;
    if (shared_reminder_index <= find_bit_check_index) return ContractError.FindBitCheckAfterSharedReminder;
    if (!std.mem.eql(u8, steps[find_bit_self_index].run, find_bit_self_test_run)) return ContractError.FindBitSelfTestCommandDrift;
    if (!std.mem.eql(u8, steps[find_bit_check_index].run, find_bit_check_run)) return ContractError.FindBitCheckCommandDrift;
}

test "Lane 17 accepts the live Phase 1 find-bit bench anchor workflow pair" {
    try requireFindBitBenchWorkflowPair(
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
        \\
        \\      - name: Check current Phase 1 find-bit bench anchor packet
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
        \\
        \\      - name: Self-test current Phase 1 shared reminder checker
        \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
    );
}

test "find-bit bench anchor check must follow its self-test" {
    try std.testing.expectError(
        ContractError.FindBitCheckBeforeSelfTest,
        requireFindBitBenchWorkflowPair(
            \\      - name: Self-test current Phase 1 bench checker
            \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
            \\
            \\      - name: Check current Phase 1 find-bit bench anchor packet
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
            \\
            \\      - name: Self-test current Phase 1 find-bit bench anchor checker
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
            \\
            \\      - name: Self-test current Phase 1 shared reminder checker
            \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
        ),
    );
}

test "find-bit bench anchor check cannot drift into the self-test command" {
    try std.testing.expectError(
        ContractError.FindBitCheckCommandDrift,
        requireFindBitBenchWorkflowPair(
            \\      - name: Self-test current Phase 1 bench checker
            \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
            \\
            \\      - name: Self-test current Phase 1 find-bit bench anchor checker
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
            \\
            \\      - name: Check current Phase 1 find-bit bench anchor packet
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
            \\
            \\      - name: Self-test current Phase 1 shared reminder checker
            \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
        ),
    );
}

test "duplicate find-bit bench anchor checks fail closed" {
    try std.testing.expectError(
        ContractError.DuplicateFindBitBenchCheck,
        requireFindBitBenchWorkflowPair(
            \\      - name: Self-test current Phase 1 bench checker
            \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
            \\
            \\      - name: Self-test current Phase 1 find-bit bench anchor checker
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
            \\
            \\      - name: Check current Phase 1 find-bit bench anchor packet
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
            \\
            \\      - name: Check current Phase 1 find-bit bench anchor packet
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
            \\
            \\      - name: Self-test current Phase 1 shared reminder checker
            \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
        ),
    );
}

test "find-bit bench anchor check must stay before the shared reminder packet" {
    try std.testing.expectError(
        ContractError.FindBitCheckAfterSharedReminder,
        requireFindBitBenchWorkflowPair(
            \\      - name: Self-test current Phase 1 bench checker
            \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
            \\
            \\      - name: Self-test current Phase 1 find-bit bench anchor checker
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
            \\
            \\      - name: Self-test current Phase 1 shared reminder checker
            \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
            \\
            \\      - name: Check current Phase 1 find-bit bench anchor packet
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
        ),
    );
}

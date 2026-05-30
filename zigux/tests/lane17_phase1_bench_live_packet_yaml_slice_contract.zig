const std = @import("std");

const bench_self_test_name = "Self-test current Phase 1 bench checker";
const bench_live_name = "Check current Phase 1 bench packet";
const bench_live_run = "python3 scripts/zigux/check-phase1-bench.py";
const find_bit_self_test_name = "Self-test current Phase 1 find-bit bench anchor checker";

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
    MissingBenchLivePacket,
    MissingFindBitBenchSelfTest,
    DuplicateBenchLivePacket,
    BenchLiveBeforeSelfTest,
    BenchLiveAfterFindBitBenchSelfTest,
    BenchLiveCommandDrift,
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

fn requireBenchLiveYamlSlice(text: []const u8) ContractError!void {
    const parsed = try parseWorkflowSlice(text);
    const steps = parsed.slice();
    const self_index = findStep(steps, bench_self_test_name) orelse return ContractError.MissingBenchSelfTest;
    const live_index = findStep(steps, bench_live_name) orelse return ContractError.MissingBenchLivePacket;
    const find_bit_index = findStep(steps, find_bit_self_test_name) orelse return ContractError.MissingFindBitBenchSelfTest;

    if (countStep(steps, bench_live_name) != 1) return ContractError.DuplicateBenchLivePacket;
    if (live_index <= self_index) return ContractError.BenchLiveBeforeSelfTest;
    if (find_bit_index <= live_index) return ContractError.BenchLiveAfterFindBitBenchSelfTest;
    if (!std.mem.eql(u8, steps[live_index].run, bench_live_run)) return ContractError.BenchLiveCommandDrift;
}

test "Lane 17 accepts the exact YAML splice for the live Phase 1 bench packet" {
    try requireBenchLiveYamlSlice(
        \\      - name: Self-test current Phase 1 bench checker
        \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
        \\
        \\      - name: Check current Phase 1 bench packet
        \\        run: python3 scripts/zigux/check-phase1-bench.py
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    );
}

test "current missing live bench packet gap is rejected from workflow text" {
    try std.testing.expectError(
        ContractError.MissingBenchLivePacket,
        requireBenchLiveYamlSlice(
            \\      - name: Self-test current Phase 1 bench checker
            \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
            \\
            \\      - name: Self-test current Phase 1 find-bit bench anchor checker
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
        ),
    );
}

test "live bench packet cannot be inserted with the self-test command" {
    try std.testing.expectError(
        ContractError.BenchLiveCommandDrift,
        requireBenchLiveYamlSlice(
            \\      - name: Self-test current Phase 1 bench checker
            \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
            \\
            \\      - name: Check current Phase 1 bench packet
            \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
            \\
            \\      - name: Self-test current Phase 1 find-bit bench anchor checker
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
        ),
    );
}

test "live bench packet cannot be moved after the find-bit bench anchor" {
    try std.testing.expectError(
        ContractError.BenchLiveAfterFindBitBenchSelfTest,
        requireBenchLiveYamlSlice(
            \\      - name: Self-test current Phase 1 bench checker
            \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
            \\
            \\      - name: Self-test current Phase 1 find-bit bench anchor checker
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
            \\
            \\      - name: Check current Phase 1 bench packet
            \\        run: python3 scripts/zigux/check-phase1-bench.py
        ),
    );
}

test "duplicate live bench packet YAML steps fail closed" {
    try std.testing.expectError(
        ContractError.DuplicateBenchLivePacket,
        requireBenchLiveYamlSlice(
            \\      - name: Self-test current Phase 1 bench checker
            \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
            \\
            \\      - name: Check current Phase 1 bench packet
            \\        run: python3 scripts/zigux/check-phase1-bench.py
            \\
            \\      - name: Check current Phase 1 bench packet
            \\        run: python3 scripts/zigux/check-phase1-bench.py
            \\
            \\      - name: Self-test current Phase 1 find-bit bench anchor checker
            \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
        ),
    );
}

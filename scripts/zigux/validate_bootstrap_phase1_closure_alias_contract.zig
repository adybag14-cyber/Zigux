const std = @import("std");

const source = @embedFile("validate-bootstrap.py");

fn contains(needle: []const u8) bool {
    return std.mem.indexOf(u8, source, needle) != null;
}

fn countOccurrences(needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, source, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

fn requireOrdered(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "validate-bootstrap keeps the Phase 1 closure command in the exact-count roster" {
    try std.testing.expect(contains("WORKFLOW_EXACT_RUN_COUNTS = {"));
    try std.testing.expectEqual(@as(usize, 2), countOccurrences("'python3 scripts/zigux/validate-phase1-closure.py'"));
    try requireOrdered(
        "WORKFLOW_EXACT_RUN_COUNTS = {",
        "'python3 scripts/zigux/validate-phase1-closure.py': 1,",
    );
}

test "Phase 1 closure alias path still falls back through the named workflow step" {
    try std.testing.expect(contains("def count_step_command_matches(workflow_text: str, step_name: str, command: str) -> int:"));
    try std.testing.expect(contains("step_blocks = workflow_text.split('\\n      - name: ')"));
    try std.testing.expect(contains("if lines[0].strip() != step_name:"));
    try std.testing.expect(contains("if count == 0 and command == 'python3 scripts/zigux/validate-phase1-closure.py':"));
    try std.testing.expect(contains("count = count_step_command_matches(text, 'Validate Phase 1 closure', command)"));
    try requireOrdered(
        "count = sum(1 for line in lines if line == expected_line)",
        "count = count_step_command_matches(text, 'Validate Phase 1 closure', command)",
    );
}

test "alias matcher accepts direct run, run_path, and command-leaf workflow forms" {
    try std.testing.expect(contains("direct_line = f'run: {command}'"));
    try std.testing.expect(contains("or command in step_text"));
    try std.testing.expect(contains("or f'run_path(\"{command_path}\"' in step_text"));
    try std.testing.expect(contains("or f\"run_path('{command_path}'\" in step_text"));
    try std.testing.expect(contains("or command_leaf in step_text"));
    try std.testing.expect(contains("matches += 1"));
}

test "workflow alias drift still reports the exact command count issue" {
    try std.testing.expect(contains("issues.append("));
    try std.testing.expect(contains("f'workflow_exact_run:{command}:count={count}:expected={expected_count}'"));
    try requireOrdered(
        "count = count_step_command_matches(text, 'Validate Phase 1 closure', command)",
        "f'workflow_exact_run:{command}:count={count}:expected={expected_count}'",
    );
}

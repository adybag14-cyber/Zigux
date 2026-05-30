const std = @import("std");

const checker_source = @embedFile("check-phase1-bench.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, checker_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, checker_source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "runtime gate reports expectation-file failures before Zig execution" {
    try expectBefore("EXPECTATIONS_JSON_ERROR={exc.msg}", "zig = find_zig(args.zig)");
    try expectBefore("EXPECTATIONS_JSON_LINE={exc.lineno}", "result = subprocess.run");

    try expectContains("PHASE1_BENCH_CHECK=fail");
    try expectContains("EXPECTATIONS_JSON_ERROR={exc.msg}");
    try expectContains("EXPECTATIONS_JSON_LINE={exc.lineno}");
    try expectContains("EXPECTATIONS_JSON_COLUMN={exc.colno}");
}

test "runtime gate validates bench source before invoking the benchmark" {
    try expectBefore("validate_bench_source", "result = subprocess.run");
    try expectBefore("PHASE1_BENCH_SOURCE", "result = subprocess.run");

    try expectContains("PHASE1_BENCH_SOURCE");
    try expectContains("SOURCE_MARKERS");
    try expectContains("PHASE1_BENCH_CHECK=fail");
}

test "runtime gate preserves Zig command and output mismatch diagnostics" {
    try expectBefore("result = subprocess.run", "kind, payload = validate_output(expectations, result.stdout)");
    try expectBefore("BENCH_COMMAND_EXIT={result.returncode}", "kind, payload = validate_output(expectations, result.stdout)");
    try expectBefore("kind, payload = validate_output(expectations, result.stdout)", "PHASE1_BENCH_CHECK=pass");

    try expectContains("BENCH_COMMAND_EXIT={result.returncode}");
    try expectContains("PHASE1_BENCH_EXPECTATIONS=");
    try expectContains("PHASE1_BENCH_SOURCE=");
    try expectContains("PHASE1_BENCH_ZIG={zig}");
}

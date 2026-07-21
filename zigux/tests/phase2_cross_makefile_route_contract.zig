const std = @import("std");
const testing = std.testing;

const route = "make -C zigux phase2-cross";
const phase2_cross_target = "phase2-cross:";
const phase2_validate_target =
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep";
const direct_cross_checker = "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig";
const alignment_checker = "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig";

const makefile_packet =
    \\.PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2
    \\
    \\phase2-cross:
    \\    $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig -- --self-test
    \\    $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig
    \\    $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig -- --self-test
    \\    $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig
    \\
    \\phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
    \\    $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tests_readme_alignment.zig -- --self-test
    \\    $(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tests_readme_alignment.zig
;

const cross_fixture_packet =
    \\{
    \\  "phase": "Phase 2",
    \\  "status": "active",
    \\  "route": "make -C zigux phase2-cross",
    \\  "archive_target_scope": [
    \\    "x86_64-linux"
    \\  ],
    \\  "cross_targets": [
    \\    {
    \\      "target": "x86_64-linux",
    \\      "review_status": "pinned bootstrap archive",
    \\      "validation_mode": "archive_required",
    \\      "route": "make -C zigux phase2-cross"
    \\    },
    \\    {
    \\      "target": "aarch64-linux",
    \\      "review_status": "route contract only",
    \\      "validation_mode": "route_contract_only",
    \\      "route": "make -C zigux phase2-cross"
    \\    }
    \\  ]
    \\}
;

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |offset| {
        count += 1;
        cursor += offset + needle.len;
    }
    return count;
}

fn countExactLine(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

test "phase2-cross make route keeps both cross checkers exactly once" {
    try testing.expectEqual(@as(usize, 1), countExactLine(makefile_packet, phase2_cross_target));
    try testing.expectEqual(@as(usize, 1), countExactLine(makefile_packet, direct_cross_checker ++ " --self-test"));
    try testing.expectEqual(@as(usize, 1), countExactLine(makefile_packet, direct_cross_checker));
    try testing.expectEqual(@as(usize, 1), countExactLine(makefile_packet, alignment_checker ++ " --self-test"));
    try testing.expectEqual(@as(usize, 1), countExactLine(makefile_packet, alignment_checker));
}

test "phase2-cross route checkers stay ordered before phase2-validate" {
    const target_index = std.mem.indexOf(u8, makefile_packet, phase2_cross_target).?;
    const direct_self_test_index = std.mem.indexOf(u8, makefile_packet, direct_cross_checker ++ " --self-test").?;
    const direct_check_index = std.mem.indexOf(u8, makefile_packet, "\n    " ++ direct_cross_checker ++ "\n").?;
    const alignment_self_test_index = std.mem.indexOf(u8, makefile_packet, alignment_checker ++ " --self-test").?;
    const alignment_check_index = std.mem.indexOf(u8, makefile_packet, "\n    " ++ alignment_checker ++ "\n").?;
    const validate_index = std.mem.indexOf(u8, makefile_packet, phase2_validate_target).?;

    try testing.expect(target_index < direct_self_test_index);
    try testing.expect(direct_self_test_index < direct_check_index);
    try testing.expect(direct_check_index < alignment_self_test_index);
    try testing.expect(alignment_self_test_index < alignment_check_index);
    try testing.expect(alignment_check_index < validate_index);
}

test "phase2-validate continues to depend on phase2-cross" {
    try testing.expectEqual(@as(usize, 1), countExactLine(makefile_packet, phase2_validate_target));
    try testing.expect(std.mem.indexOf(u8, phase2_validate_target, "phase2-cross") != null);
}

test "fixture packet names the route for every current cross target" {
    try testing.expectEqual(@as(usize, 3), countNeedle(cross_fixture_packet, "\"route\": \"" ++ route ++ "\""));
    try testing.expectEqual(@as(usize, 1), countNeedle(cross_fixture_packet, "\"target\": \"x86_64-linux\""));
    try testing.expectEqual(@as(usize, 1), countNeedle(cross_fixture_packet, "\"target\": \"aarch64-linux\""));
    try testing.expectEqual(@as(usize, 1), countNeedle(cross_fixture_packet, "\"validation_mode\": \"archive_required\""));
    try testing.expectEqual(@as(usize, 1), countNeedle(cross_fixture_packet, "\"validation_mode\": \"route_contract_only\""));
}

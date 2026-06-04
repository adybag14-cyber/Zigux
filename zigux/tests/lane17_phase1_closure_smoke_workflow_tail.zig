const std = @import("std");
const sources = @import("lane17_phase1_closure_smoke_workflow_tail_sources");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn expectExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingMarker;
    const remaining = haystack[first_index + needle.len ..];
    try std.testing.expect(std.mem.indexOf(u8, remaining, needle) == null);
}

const phase1_closure_check =
    "      - name: Check current Phase 1 closure packet\n" ++
    "        run: python3 scripts/zigux/validate-phase1-closure.py";
const phase3_interop_selftest =
    "      - name: Self-test current Phase 3 interop packet\n" ++
    "        run: python3 scripts/zigux/validate_phase3_selftest.py";
const phase3_interop_check =
    "      - name: Check current Phase 3 interop packet\n" ++
    "        run: python3 scripts/zigux/run-phase3-checks.py";
const phase3_shared_tests =
    "      - name: Run current Phase 3 shared tests-root packet\n" ++
    "        run: zig build phase3-test --build-file zigux/tests/build.zig";
const phase3_abi_dump =
    "      - name: Run current Phase 3 ABI dump replay\n" ++
    "        run: zig build phase3-dump --build-file zigux/tests/build.zig";
const phase1_shared_smoke =
    "      - name: Run current Phase 1 shared tests-root smoke\n" ++
    "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig";

test "closure check hands off to phase3 before the shared phase1 smoke tail" {
    const workflow = sources.workflow_text;

    try expectOrdered(workflow, phase1_closure_check, phase3_interop_selftest);
    try expectOrdered(workflow, phase3_interop_selftest, phase3_interop_check);
    try expectOrdered(workflow, phase3_interop_check, phase3_shared_tests);
    try expectOrdered(workflow, phase3_shared_tests, phase3_abi_dump);
    try expectOrdered(workflow, phase3_abi_dump, phase1_shared_smoke);

    try expectExactlyOnce(workflow, "run: python3 scripts/zigux/validate-phase1-closure.py\n");
    try expectExactlyOnce(workflow, "run: python3 scripts/zigux/validate_phase3_selftest.py\n");
    try expectExactlyOnce(workflow, "run: python3 scripts/zigux/run-phase3-checks.py\n");
    try expectExactlyOnce(workflow, "run: zig build phase3-test --build-file zigux/tests/build.zig\n");
    try expectExactlyOnce(workflow, "run: zig build phase3-dump --build-file zigux/tests/build.zig\n");
    try expectExactlyOnce(workflow, "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n");
}

test "phase1 shared smoke remains narrow and does not reopen phase1 make routes" {
    const workflow = sources.workflow_text;

    try expectContains(workflow, "      - name: Self-test current Phase 1 closure validator\n");
    try expectContains(workflow, "      - name: Check current Phase 1 closure packet\n");
    try expectContains(workflow, "      - name: Run current Phase 1 shared tests-root smoke\n");

    try expectNotContains(workflow, "run: make -C zigux phase1\n");
    try expectNotContains(workflow, "run: make -C zigux phase1-validate\n");
    try expectNotContains(workflow, "run: make -C zigux phase1-test\n");
    try expectNotContains(workflow, "run: make -C zigux phase1-bench\n");
}

test "phase1 smoke stays downstream of phase3 rather than inside the closure validator pair" {
    const workflow = sources.workflow_text;

    try expectOrdered(
        workflow,
        "      - name: Self-test current Phase 1 closure validator\n" ++
            "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        phase1_closure_check,
    );
    try expectOrdered(workflow, phase1_closure_check, phase1_shared_smoke);
    try expectOrdered(workflow, phase3_shared_tests, phase1_shared_smoke);
}

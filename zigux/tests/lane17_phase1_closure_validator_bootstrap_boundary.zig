const std = @import("std");
const sources = @import("lane17_phase1_closure_validator_bootstrap_boundary_sources");

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

test "bootstrap runs closure validator as the phase1 handoff after shared reminder" {
    const workflow = sources.workflow_text;

    try expectOrdered(
        workflow,
        "      - name: Check current Phase 2 closure packet\n        run: python3 scripts/zigux/validate-phase2-closure.py",
        "      - name: Self-test current Phase 1 direct-owner checker\n        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    );
    try expectOrdered(
        workflow,
        "      - name: Check current Phase 1 shared reminder packet\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "      - name: Self-test current Phase 1 closure validator\n        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    );
    try expectOrdered(
        workflow,
        "      - name: Self-test current Phase 1 closure validator\n        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "      - name: Check current Phase 1 closure packet\n        run: python3 scripts/zigux/validate-phase1-closure.py",
    );
    try expectOrdered(
        workflow,
        "      - name: Check current Phase 1 closure packet\n        run: python3 scripts/zigux/validate-phase1-closure.py",
        "      - name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py",
    );

    try expectExactlyOnce(workflow, "run: python3 scripts/zigux/validate-phase1-closure.py --self-test");
    try expectExactlyOnce(workflow, "run: python3 scripts/zigux/validate-phase1-closure.py\n");
    try expectNotContains(workflow, "run: make -C zigux phase1\n");
    try expectNotContains(workflow, "run: make -C zigux phase1-validate\n");
}

test "closure note keeps validator and shared smoke as the narrow current route" {
    const closure = sources.closure_note_text;

    try expectContains(closure, "`PHASE1_STATUS=parked`");
    try expectContains(closure, "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`");
    try expectContains(closure, "`PHASE1_HELPER_COUNT=13`");
    try expectContains(closure, "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`");
    try expectContains(closure, "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectContains(closure, "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`");
    try expectContains(closure, "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker");

    try expectContains(closure, ".github/workflows/zigux-bootstrap.yml");
    try expectContains(closure, "scripts/zigux/check-phase1-shared-reminder-packet.py");
    try expectContains(closure, "scripts/zigux/validate-phase1-closure.py");
    try expectContains(closure, "zigux/tests/phase1_host_tools_smoke.zig");

    try expectNotContains(closure, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
    try expectNotContains(closure, "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`");
}

test "validator source owns the same files and forbids stale phase1 make routes" {
    const validator = sources.validator_text;

    try expectContains(validator, "PHASE1_CLOSURE_REL = Path(\"Documentation/zigux/phase1-closure.md\")");
    try expectContains(validator, "WORKFLOW_REL = Path(\".github/workflows/zigux-bootstrap.yml\")");
    try expectContains(validator, "SHARED_REMINDER_CHECKER_REL = Path(\"scripts/zigux/check-phase1-shared-reminder-packet.py\")");
    try expectContains(validator, "PHASE1_SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")");
    try expectContains(validator, "\"closure_validator\": \"`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`\"");
    try expectContains(validator, "\"validator_state\": \"`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`\"");
    try expectContains(validator, "\"phase1-validate:\"");
    try expectContains(validator, "\"phase1-test:\"");
    try expectContains(validator, "\"phase1-bench:\"");
    try expectContains(validator, "phase1:");

    try expectNotContains(validator, "PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master");
    try expectNotContains(validator, "allow_missing_phase1");
}

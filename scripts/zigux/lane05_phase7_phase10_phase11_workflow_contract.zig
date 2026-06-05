const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingMarker,
    MarkerOutOfOrder,
};

const ordered_workflow_markers = [_][]const u8{
    "run: zig test samples/zigux/runtime_trace_events.zig\n",
    "run: zig test samples/zigux/runtime_trace_events_unregistered_gate.zig\n",
    "run: zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig\n",
    "run: zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig\n",
    "run: zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig\n",
    "run: zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig\n",
    "run: zig test zigux/tests/runtime_trace_events_survey.zig\n",
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test\n",
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py\n",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test\n",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py\n",
    "run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test\n",
    "run: python3 scripts/zigux/check-phase10-bootstrap-route.py\n",
    "run: make -C zigux phase10-validate\n",
    "run: make -C zigux phase10-test\n",
    "run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test\n",
    "run: python3 scripts/zigux/check-phase11-build-inventory.py\n",
    "run: make -C zigux phase11-validate\n",
    "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test\n",
};

const descriptive_step_markers = [_][]const u8{
    "Run current Phase 9 trace-events runtime sample tests",
    "Run current Phase 9 trace-events survey witness",
    "Self-test current Phase 7 shared-control gap checker",
    "Check current Phase 7 make-wrapper selftest alignment packet",
    "Self-test current Phase 10 bootstrap route checker",
    "Run Phase 10 helper tests",
    "Self-test current Phase 11 build inventory checker",
    "Validate current Phase 11 support bundle",
    "Self-test current Phase 12 build-only surface checker",
};

fn requireContains(haystack: []const u8, needle: []const u8) ContractError!usize {
    return std.mem.indexOf(u8, haystack, needle) orelse ContractError.MissingMarker;
}

fn requireOrdered(haystack: []const u8, markers: []const []const u8) ContractError!void {
    var previous: usize = 0;
    for (markers, 0..) |marker, index| {
        const position = try requireContains(haystack, marker);
        if (index != 0 and position <= previous) {
            return ContractError.MarkerOutOfOrder;
        }
        previous = position;
    }
}

fn validatePhase7Phase10Phase11Workflow(workflow: []const u8) ContractError!void {
    for (&descriptive_step_markers) |marker| {
        _ = try requireContains(workflow, marker);
    }
    try requireOrdered(workflow, &ordered_workflow_markers);
}

pub fn main(init: std.process.Init) !void {
    const allocator = std.heap.page_allocator;

    const workflow = try std.Io.Dir.cwd().readFileAlloc(init.io, workflow_path, allocator, .limited(1024 * 1024));
    defer allocator.free(workflow);

    validatePhase7Phase10Phase11Workflow(workflow) catch |err| {
        std.debug.print("LANE05_PHASE7_PHASE10_PHASE11_WORKFLOW_CONTRACT=fail\n", .{});
        std.debug.print("LANE05_PHASE7_PHASE10_PHASE11_WORKFLOW_CONTRACT_NOTE={s}\n", .{@errorName(err)});
        return err;
    };

    std.debug.print("LANE05_PHASE7_PHASE10_PHASE11_WORKFLOW_CONTRACT=pass\n", .{});
    std.debug.print("LANE05_PHASE7_PHASE10_PHASE11_WORKFLOW_CONTRACT_MARKER_COUNT={d}\n", .{ordered_workflow_markers.len + descriptive_step_markers.len});
}

test "accepts current Phase 9 runtime tail through Phase 11 route cluster" {
    const workflow =
        \\      - name: Run current Phase 9 trace-events runtime sample tests
        \\        run: zig test samples/zigux/runtime_trace_events.zig
        \\
        \\      - name: Run current Phase 9 unregistered gate companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_unregistered_gate.zig
        \\
        \\      - name: Run current Phase 9 exit rollback guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig
        \\
        \\      - name: Run current Phase 9 registration reentry companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig
        \\
        \\      - name: Run current Phase 9 reinit rollback guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig
        \\
        \\      - name: Run current Phase 9 reinit reexit guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig
        \\
        \\      - name: Run current Phase 9 trace-events survey witness
        \\        run: zig test zigux/tests/runtime_trace_events_survey.zig
        \\
        \\      - name: Self-test current Phase 7 shared-control gap checker
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test
        \\
        \\      - name: Check current Phase 7 shared-control gap packet
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py
        \\
        \\      - name: Self-test current Phase 7 make-wrapper selftest alignment checker
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test
        \\
        \\      - name: Check current Phase 7 make-wrapper selftest alignment packet
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py
        \\
        \\      - name: Self-test current Phase 10 bootstrap route checker
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test
        \\
        \\      - name: Check current Phase 10 bootstrap route
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py
        \\
        \\      - name: Validate Phase 10 checker-backed review packet
        \\        run: make -C zigux phase10-validate
        \\
        \\      - name: Run Phase 10 helper tests
        \\        run: make -C zigux phase10-test
        \\
        \\      - name: Self-test current Phase 11 build inventory checker
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test
        \\
        \\      - name: Check current Phase 11 build inventory packet
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py
        \\
        \\      - name: Validate current Phase 11 support bundle
        \\        run: make -C zigux phase11-validate
        \\
        \\      - name: Self-test current Phase 12 build-only surface checker
        \\        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
        \\
    ;

    try validatePhase7Phase10Phase11Workflow(workflow);
}

test "rejects missing Phase 7 handoff after Phase 9 runtime witnesses" {
    const workflow =
        \\      - name: Run current Phase 9 trace-events runtime sample tests
        \\        run: zig test samples/zigux/runtime_trace_events.zig
        \\      - name: Run current Phase 9 unregistered gate companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_unregistered_gate.zig
        \\      - name: Run current Phase 9 exit rollback guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig
        \\      - name: Run current Phase 9 registration reentry companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig
        \\      - name: Run current Phase 9 reinit rollback guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig
        \\      - name: Run current Phase 9 reinit reexit guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig
        \\      - name: Run current Phase 9 trace-events survey witness
        \\        run: zig test zigux/tests/runtime_trace_events_survey.zig
        \\      - name: Self-test current Phase 10 bootstrap route checker
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test
        \\      - name: Check current Phase 10 bootstrap route
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py
        \\      - name: Validate Phase 10 checker-backed review packet
        \\        run: make -C zigux phase10-validate
        \\      - name: Run Phase 10 helper tests
        \\        run: make -C zigux phase10-test
        \\      - name: Self-test current Phase 11 build inventory checker
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test
        \\      - name: Check current Phase 11 build inventory packet
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py
        \\      - name: Validate current Phase 11 support bundle
        \\        run: make -C zigux phase11-validate
        \\      - name: Self-test current Phase 12 build-only surface checker
        \\        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
        \\
    ;

    try std.testing.expectError(ContractError.MissingMarker, validatePhase7Phase10Phase11Workflow(workflow));
}

test "rejects Phase 11 validation before Phase 10 routes complete" {
    const workflow =
        \\      - name: Run current Phase 9 trace-events runtime sample tests
        \\        run: zig test samples/zigux/runtime_trace_events.zig
        \\      - name: Run current Phase 9 unregistered gate companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_unregistered_gate.zig
        \\      - name: Run current Phase 9 exit rollback guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig
        \\      - name: Run current Phase 9 registration reentry companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig
        \\      - name: Run current Phase 9 reinit rollback guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig
        \\      - name: Run current Phase 9 reinit reexit guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig
        \\      - name: Run current Phase 9 trace-events survey witness
        \\        run: zig test zigux/tests/runtime_trace_events_survey.zig
        \\      - name: Self-test current Phase 7 shared-control gap checker
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test
        \\      - name: Check current Phase 7 shared-control gap packet
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py
        \\      - name: Self-test current Phase 7 make-wrapper selftest alignment checker
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test
        \\      - name: Check current Phase 7 make-wrapper selftest alignment packet
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py
        \\      - name: Self-test current Phase 10 bootstrap route checker
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test
        \\      - name: Check current Phase 10 bootstrap route
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py
        \\      - name: Self-test current Phase 11 build inventory checker
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test
        \\      - name: Check current Phase 11 build inventory packet
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py
        \\      - name: Validate current Phase 11 support bundle
        \\        run: make -C zigux phase11-validate
        \\      - name: Validate Phase 10 checker-backed review packet
        \\        run: make -C zigux phase10-validate
        \\      - name: Run Phase 10 helper tests
        \\        run: make -C zigux phase10-test
        \\      - name: Self-test current Phase 12 build-only surface checker
        \\        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
        \\
    ;

    try std.testing.expectError(ContractError.MarkerOutOfOrder, validatePhase7Phase10Phase11Workflow(workflow));
}

test "rejects Phase 12 entry before Phase 11 validation" {
    const workflow =
        \\      - name: Run current Phase 9 trace-events runtime sample tests
        \\        run: zig test samples/zigux/runtime_trace_events.zig
        \\      - name: Run current Phase 9 unregistered gate companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_unregistered_gate.zig
        \\      - name: Run current Phase 9 exit rollback guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig
        \\      - name: Run current Phase 9 registration reentry companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig
        \\      - name: Run current Phase 9 reinit rollback guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_reinit_rollback_guard.zig
        \\      - name: Run current Phase 9 reinit reexit guard companion tests
        \\        run: zig test samples/zigux/runtime_trace_events_reinit_reexit_guard.zig
        \\      - name: Run current Phase 9 trace-events survey witness
        \\        run: zig test zigux/tests/runtime_trace_events_survey.zig
        \\      - name: Self-test current Phase 7 shared-control gap checker
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test
        \\      - name: Check current Phase 7 shared-control gap packet
        \\        run: python3 scripts/zigux/check-phase7-shared-control-gap.py
        \\      - name: Self-test current Phase 7 make-wrapper selftest alignment checker
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test
        \\      - name: Check current Phase 7 make-wrapper selftest alignment packet
        \\        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py
        \\      - name: Self-test current Phase 10 bootstrap route checker
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test
        \\      - name: Check current Phase 10 bootstrap route
        \\        run: python3 scripts/zigux/check-phase10-bootstrap-route.py
        \\      - name: Validate Phase 10 checker-backed review packet
        \\        run: make -C zigux phase10-validate
        \\      - name: Run Phase 10 helper tests
        \\        run: make -C zigux phase10-test
        \\      - name: Self-test current Phase 11 build inventory checker
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test
        \\      - name: Check current Phase 11 build inventory packet
        \\        run: python3 scripts/zigux/check-phase11-build-inventory.py
        \\      - name: Self-test current Phase 12 build-only surface checker
        \\        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
        \\      - name: Validate current Phase 11 support bundle
        \\        run: make -C zigux phase11-validate
        \\
    ;

    try std.testing.expectError(ContractError.MarkerOutOfOrder, validatePhase7Phase10Phase11Workflow(workflow));
}

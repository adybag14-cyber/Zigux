const std = @import("std");

const max_file_size = 512 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_file_size),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse {
        std.debug.print("missing ordered marker: {s}\n", .{first});
        return error.MissingMarker;
    };
    const second_index = std.mem.indexOf(u8, haystack, second) orelse {
        std.debug.print("missing ordered marker: {s}\n", .{second});
        return error.MissingMarker;
    };
    try std.testing.expect(first_index < second_index);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) != null) {
        std.debug.print("unexpected marker: {s}\n", .{needle});
        return error.UnexpectedMarker;
    }
}

test "workflow uses current closure validator instead of stale phase1 validator path" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "Self-test current Phase 1 closure validator");
    try expectContains(workflow, "python3 scripts/zigux/validate-phase1-closure.py --self-test");
    try expectContains(workflow, "Check current Phase 1 closure packet");
    try expectContains(workflow, "python3 scripts/zigux/validate-phase1-closure.py");
    try expectContains(workflow, "Run current Phase 1 shared tests-root smoke");
    try expectContains(workflow, "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig");
    try expectAbsent(workflow, "python3 scripts/zigux/validate-phase1.py");

    try expectOrdered(
        workflow,
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    );
    try expectOrdered(
        workflow,
        "python3 scripts/zigux/validate-phase1-closure.py",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    );
}

test "closure validator records validate-phase1.py as a gap packet and rejects stale missing-state claims" {
    const validator = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py");
    try expectContains(validator, "PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master");
    try expectContains(validator, "PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig");
    try expectContains(validator, "PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py");
    try expectContains(validator, "FORBIDDEN_CLOSURE_MARKERS");
    try expectContains(validator, "PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master");
}

test "bootstrap ledger still names the original Lane 07 target path for traceability" {
    const ledger = try readRepoFile(std.testing.allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer std.testing.allocator.free(ledger);

    try expectContains(ledger, "7. `test(zigux): add phase-1 helper harness and workflow gate`");
    try expectContains(ledger, "- `zigux/tests/phase1_helpers.zig`");
    try expectContains(ledger, "- `zigux/tests/build.zig`");
    try expectContains(ledger, "- `scripts/zigux/validate-phase1.py`");
    try expectContains(ledger, "- `.github/workflows/zigux-bootstrap.yml`");
}

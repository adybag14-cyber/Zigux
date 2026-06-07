const std = @import("std");
const testing = std.testing;

const RequiredMakefileMarkers = [_][]const u8{
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase3-validate:",
    "phase3:",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "phase14-validate:",
};

const ForbiddenMakefileMarkers = [_][]const u8{
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
};

const WorkflowPhase1ClosureCommands = [_][]const u8{
    "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "python3 scripts/zigux/check-phase1-bench.py --self-test",
    "python3 scripts/zigux/check-phase1-bench.py",
    "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "python3 scripts/zigux/validate-phase1-closure.py",
    "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

fn repoFile(allocator: std.mem.Allocator, relative: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        relative,
        allocator,
        .limited(8 * 1024 * 1024),
    );
}

fn expectContainsExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse {
        std.debug.print("missing required marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
    if (std.mem.indexOfPos(u8, haystack, first + needle.len, needle) != null) {
        std.debug.print("duplicate marker: {s}\n", .{needle});
        return error.DuplicateMarker;
    }
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) != null) {
        std.debug.print("forbidden marker present: {s}\n", .{needle});
        return error.ForbiddenMarkerPresent;
    }
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOfPos(u8, haystack, cursor, needle) orelse {
            std.debug.print("missing ordered marker: {s}\n", .{needle});
            return error.MissingOrderedMarker;
        };
        cursor = found + needle.len;
    }
}

fn expectQuotedPythonString(haystack: []const u8, value: []const u8) !void {
    var quoted_buffer: [256]u8 = undefined;
    const quoted = try std.fmt.bufPrint(&quoted_buffer, "\"{s}\"", .{value});
    try expectContainsExactlyOnce(haystack, quoted);
}

test "Phase 1 closure validator pins the Makefile boundary roster" {
    const validator = try repoFile(testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer testing.allocator.free(validator);

    try expectContainsExactlyOnce(validator, "EXPECTED_MAKEFILE_MARKERS = (");
    try expectContainsExactlyOnce(validator, "FORBIDDEN_MAKEFILE_MARKERS = (");
    try expectContainsExactlyOnce(validator, "for marker in EXPECTED_MAKEFILE_MARKERS:");
    try expectContainsExactlyOnce(validator, "for marker in FORBIDDEN_MAKEFILE_MARKERS:");
    try expectContainsExactlyOnce(validator, "f\"{ZIGUX_MAKEFILE_REL.as_posix()}:required\"");
    try expectContainsExactlyOnce(validator, "f\"{ZIGUX_MAKEFILE_REL.as_posix()}:forbidden_marker:actual_count={count}:{marker}\"");

    for (RequiredMakefileMarkers) |marker| {
        try expectQuotedPythonString(validator, marker);
    }
    for (ForbiddenMakefileMarkers) |marker| {
        try expectQuotedPythonString(validator, marker);
    }
}

test "live Makefile keeps required later-phase routes and no old Phase 1 wrappers" {
    const makefile = try repoFile(testing.allocator, "zigux/Makefile");
    defer testing.allocator.free(makefile);

    for (RequiredMakefileMarkers) |marker| {
        try expectContainsExactlyOnce(makefile, marker);
    }
    for (ForbiddenMakefileMarkers) |marker| {
        try expectAbsent(makefile, marker);
    }

    try expectContainsExactlyOnce(makefile, ".PHONY:");
    try expectContainsExactlyOnce(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContainsExactlyOnce(makefile, "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump");
}

test "bootstrap workflow runs Phase 1 closure checks before later handoff routes" {
    const workflow = try repoFile(testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer testing.allocator.free(workflow);

    try expectOrdered(workflow, &WorkflowPhase1ClosureCommands);
    try expectContainsExactlyOnce(workflow, "Run current Phase 1 shared tests-root smoke");
    try expectContainsExactlyOnce(workflow, "Run current Phase 3 shared tests-root packet");
    try expectAbsent(workflow, "make -C zigux phase1");
    try expectAbsent(workflow, "zig build phase1-bench");
}

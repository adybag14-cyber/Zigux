const std = @import("std");

const VALIDATOR = "scripts/zigux/validate-phase2.py";

const REQUIRED_PATH_MARKERS = [_][]const u8{
    "\"scripts/zigux/check-phase2-cross.py\",",
    "\"scripts/zigux/check-phase2-cross-selftest-alignment.py\",",
    "\"zigux/tests/fixtures/phase2_cross_targets.json\",",
    "TOOLCHAIN_POLICY = \"scripts/zigux/zig-toolchain-policy.json\"",
    "MAKEFILE = \"zigux/Makefile\"",
};

const REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "\"run: python3 scripts/zigux/check-phase2-cross.py --self-test\",",
    "\"run: python3 scripts/zigux/check-phase2-cross.py\",",
    "\"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\",",
    "\"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\",",
};

const REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "\"phase2-cross:\",",
    "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py\",",
    "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py\",",
};

fn readValidator(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        VALIDATOR,
        allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "aggregate Phase 2 validator still names the direct cross packet files" {
    const source = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (REQUIRED_PATH_MARKERS) |marker| {
        try expectContains(source, marker);
    }
}

test "bootstrap workflow roster keeps the direct cross checks paired" {
    const source = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (REQUIRED_WORKFLOW_LINES) |marker| {
        try expectContains(source, marker);
    }
    try expectOrdered(
        source,
        "\"run: python3 scripts/zigux/check-phase2-cross.py --self-test\",",
        "\"run: python3 scripts/zigux/check-phase2-cross.py\",",
    );
    try expectOrdered(
        source,
        "\"run: python3 scripts/zigux/check-phase2-cross.py\",",
        "\"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\",",
    );
    try expectOrdered(
        source,
        "\"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\",",
        "\"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\",",
    );
}

test "Makefile validation roster keeps phase2-cross checker body visible" {
    const source = try readValidator(std.testing.allocator);
    defer std.testing.allocator.free(source);

    for (REQUIRED_MAKEFILE_LINES) |marker| {
        try expectContains(source, marker);
    }
    try expectOrdered(
        source,
        "\"phase2-cross:\",",
        "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py\",",
    );
    try expectOrdered(
        source,
        "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py\",",
        "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py\",",
    );
}

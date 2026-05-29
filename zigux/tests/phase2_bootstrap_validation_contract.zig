const std = @import("std");

const required_paths = [_][]const u8{
    "zigux-alpha/README.md",
    "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-bootstrap.py",
    "scripts/zigux/zig-toolchain-policy.json",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
};

const workflow_lines = [_][]const u8{
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py --self-test",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: make -C zigux phase6-validate",
    "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    "run: python3 scripts/zigux/validate-bootstrap.py",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

fn expectSequenceAfter(haystack: []const u8, anchor: []const u8, sequence: []const []const u8) !void {
    var cursor = (std.mem.indexOf(u8, haystack, anchor) orelse return error.AnchorMarkerMissing) + anchor.len;
    for (sequence) |item| {
        const index = std.mem.indexOfPos(u8, haystack, cursor, item) orelse return error.SequenceMarkerMissing;
        cursor = index + item.len;
    }
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    if (needle.len == 0) return 0;

    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

test "phase 2 bootstrap validation contract keeps required bootstrap surfaces visible" {
    const allocator = std.testing.allocator;
    const validate_bootstrap = try readRepoFile(allocator, "scripts/zigux/validate-bootstrap.py");
    defer allocator.free(validate_bootstrap);

    try expectContains(validate_bootstrap, "REQUIRED_PATHS = (");
    try expectContains(validate_bootstrap, "WORKFLOW = \".github/workflows/zigux-bootstrap.yml\"");
    try expectContains(validate_bootstrap, "BOOTSTRAP_VALIDATION=pass");
    try expectContains(validate_bootstrap, "BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}");

    for (required_paths) |path| {
        try expectContains(validate_bootstrap, path);
    }

    try expectBefore(
        validate_bootstrap,
        "scripts/zigux/check-zig-toolchain.py",
        "scripts/zigux/validate-bootstrap.py",
    );
    try expectBefore(
        validate_bootstrap,
        "scripts/zigux/check-lane05-local-first-archive-workflow.py",
        "scripts/zigux/check-lane05-stage-helper-selftest.py",
    );
}

test "phase 2 bootstrap validation contract keeps workflow packet checks aligned" {
    const allocator = std.testing.allocator;
    const validate_bootstrap = try readRepoFile(allocator, "scripts/zigux/validate-bootstrap.py");
    defer allocator.free(validate_bootstrap);
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try expectContains(validate_bootstrap, "REQUIRED_WORKFLOW_LINES = (");
    try expectContains(validate_bootstrap, "BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}");

    for (workflow_lines) |line| {
        try expectContains(validate_bootstrap, line);
        try expectContains(workflow, line);
    }

    try expectSequenceAfter(validate_bootstrap, "REQUIRED_WORKFLOW_LINES = (", workflow_lines[0..]);
}

test "phase 2 bootstrap validation contract keeps fail-closed self-test cases visible" {
    const allocator = std.testing.allocator;
    const validate_bootstrap = try readRepoFile(allocator, "scripts/zigux/validate-bootstrap.py");
    defer allocator.free(validate_bootstrap);

    const required_failure_codes = [_][]const u8{
        "MISSING_REQUIRED_PATH",
        "MISSING_README_MARKER",
        "MISSING_ROADMAP_MARKER",
        "MISSING_LEDGER_MARKER",
        "MISSING_FREEZE_MAP_MARKER",
        "MISSING_WORKFLOW_LINE",
        "DUPLICATE_WORKFLOW_LINE",
    };

    for (required_failure_codes) |code| {
        try expectContains(validate_bootstrap, code);
    }

    try expectContains(validate_bootstrap, "BOOTSTRAP_VALIDATION_SELF_TEST=pass");
    try expectContains(validate_bootstrap, "BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT={checks}");
    try expectContains(validate_bootstrap, "scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(validate_bootstrap, "scripts/zigux/check-lane05-stage-helper-selftest.py");
    try expectContains(validate_bootstrap, "scripts/zigux/zig-toolchain-policy.json");
    try std.testing.expect(countOccurrences(validate_bootstrap, "checks += 1") >= 15);
}

const std = @import("std");

fn readFileAlloc(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(
        std.mem.indexOf(u8, haystack, needle) != null,
    );
}

fn requireBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "validate-bootstrap owns the bootstrap workflow replay packet" {
    const allocator = std.testing.allocator;
    const validator = try readFileAlloc(allocator, "scripts/zigux/validate-bootstrap.py");
    defer allocator.free(validator);

    try requireContains(validator, "REQUIRED_WORKFLOW_LINES = (");
    try requireContains(validator, "\"run: python3 scripts/zigux/check-zig-toolchain.py --self-test\"");
    try requireContains(validator, "\"run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\"");
    try requireContains(validator, "\"run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\"");
    try requireContains(validator, "\"run: python3 scripts/zigux/install-zig.py --self-test\"");
    try requireContains(validator, "\"run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\"");
    try requireContains(validator, "\"run: python3 scripts/zigux/validate-bootstrap.py --self-test\"");
    try requireContains(validator, "\"run: python3 scripts/zigux/validate-bootstrap.py\"");
    try requireContains(validator, "MISSING_WORKFLOW_LINE");
    try requireContains(validator, "DUPLICATE_WORKFLOW_LINE");
    try requireContains(validator, "count_exact_lines(workflow, marker)");
}

test "workflow keeps bootstrap validator after toolchain and archive checks" {
    const allocator = std.testing.allocator;
    const workflow = try readFileAlloc(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try requireContains(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --self-test");
    try requireContains(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only");
    try requireContains(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try requireContains(workflow, "run: python3 scripts/zigux/install-zig.py --self-test");
    try requireContains(workflow, "run: python3 scripts/zigux/validate-bootstrap.py --self-test");
    try requireContains(workflow, "run: python3 scripts/zigux/validate-bootstrap.py");

    try requireBefore(
        workflow,
        "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
        "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    );
    try requireBefore(
        workflow,
        "name: Self-test current bootstrap validator",
        "name: Validate current bootstrap packet",
    );
}

test "scripts root points reviewers at validator and toolchain surfaces" {
    const allocator = std.testing.allocator;
    const scripts_readme = try readFileAlloc(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);

    try requireContains(scripts_readme, "# scripts/zigux");
    try requireContains(scripts_readme, "scripts/zigux/check-zig-toolchain.py");
    try requireContains(scripts_readme, "scripts/zigux/check-phase2-toolchain-pinning.py");
    try requireContains(scripts_readme, "python3 scripts/zigux/check-zig-toolchain.py --policy-only");
    try requireContains(scripts_readme, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
}

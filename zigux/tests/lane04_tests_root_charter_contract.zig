const std = @import("std");

const readme_path = "zigux/tests/README.md";

fn readReadme(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        readme_path,
        allocator,
        .limited(256 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "tests root preserves shared harness charter" {
    const readme = try readReadme(std.testing.allocator);
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "home of reusable Zigux parity and differential validation harnesses");
    try expectContains(readme, "hold shared harness logic before subsystem-specific tests spread through the tree");
    try expectContains(readme, "keep product-facing validation code separate from ad hoc experiments");
    try expectContains(readme, "helper parity, ABI assertions, and rollback readiness");
}

test "differential anchors stay visible from the root" {
    const readme = try readReadme(std.testing.allocator);
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "zigux/tests/atomic64_diff.zig");
    try expectContains(readme, "zigux/tests/runtime_atomic64_diff.zig");
    try expectContains(readme, "zigux/tests/bitmap_diff.zig");
    try expectContains(readme, "Phase 4");
}

test "harness entrypoints remain rerunnable from documented routes" {
    const readme = try readReadme(std.testing.allocator);
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "zigux/tests/build.zig");
    try expectContains(readme, "zig build");
    try expectContains(readme, "--build-file");
    try expectContains(readme, "make -C zigux");
}

const std = @import("std");
const testing = std.testing;

const default_workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, default_workflow_path, allocator, .limited(512 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
}

fn requireOrdered(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const next = std.mem.indexOf(u8, haystack[cursor..], marker) orelse {
            std.debug.print("missing ordered marker after byte {d}: {s}\n", .{ cursor, marker });
            return error.MissingOrderedMarker;
        };
        cursor += next + marker.len;
    }
}

fn requireAbsent(haystack: []const u8, forbidden: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, forbidden) != null) {
        std.debug.print("forbidden marker present: {s}\n", .{forbidden});
        return error.ForbiddenMarker;
    }
}

fn requireCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    const actual = std.mem.count(u8, haystack, needle);
    if (actual != expected) {
        std.debug.print("marker count mismatch for {s}: expected {d}, found {d}\n", .{ needle, expected, actual });
        return error.MarkerCountMismatch;
    }
}

fn requireExplicitZigPathActivation(workflow: []const u8) !void {
    try requireCount(workflow, "zig_path=\"$extract_root/zig\"", 3);
    try requireCount(workflow, "\"$zig_path\" version", 1);
    try requireAbsent(workflow, "\n          zig version");
    try requireAbsent(workflow, "\n          zig \"$");
    try requireOrdered(workflow, &.{
        "zig_path=\"$extract_root/zig\"",
        "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"",
        "return 0",
    });
    try requireOrdered(workflow, &.{
        "if [ \"$download_success\" -ne 1 ]; then\n            echo 'failed to install a verified pinned Zig archive",
        "exit 1",
        "zig_path=\"$extract_root/zig\"",
        "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
        "\"$zig_path\" version",
    });
}

test "lane05 setup activation probes the explicit extracted Zig path" {
    const workflow = try readWorkflow(testing.allocator);
    defer testing.allocator.free(workflow);

    try requireExplicitZigPathActivation(workflow);
}

test "lane05 setup activation rejects ambient Zig version probes" {
    const bad_workflow =
        \\if [ "$download_success" -ne 1 ]; then
        \\            echo 'failed to install a verified pinned Zig archive
        \\            exit 1
        \\          fi
        \\          zig_path="$extract_root/zig"
        \\          echo "$extract_root" >> "$GITHUB_PATH"
        \\          zig version
    ;

    try testing.expectError(error.MarkerCountMismatch, requireExplicitZigPathActivation(bad_workflow));
}

test "lane05 setup activation rejects missing final explicit probe" {
    const bad_workflow =
        \\          zig_path="$extract_root/zig"
        \\          if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then
        \\            return 0
        \\          fi
        \\if [ "$download_success" -ne 1 ]; then
        \\            echo 'failed to install a verified pinned Zig archive
        \\            exit 1
        \\          fi
        \\          zig_path="$extract_root/zig"
        \\          echo "$extract_root" >> "$GITHUB_PATH"
    ;

    try testing.expectError(error.MarkerCountMismatch, requireExplicitZigPathActivation(bad_workflow));
}

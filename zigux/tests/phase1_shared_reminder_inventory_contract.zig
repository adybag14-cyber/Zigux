const std = @import("std");

const max_file_size = 512 * 1024;

const required_files = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "scripts/zigux/check-phase1-find-bit-review-packet.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_helpers_build.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/Makefile",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
};

const workflow_shared_reminder_gate = [_][]const u8{
    "      - name: Self-test current Phase 1 shared reminder checker\n",
    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n",
    "      - name: Check current Phase 1 shared reminder packet\n",
    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n",
    "      - name: Self-test current Phase 1 closure validator\n",
    "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n",
    "      - name: Check current Phase 1 closure packet\n",
    "        run: python3 scripts/zigux/validate-phase1-closure.py\n",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(max_file_size),
    );
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    const count = std.mem.count(u8, haystack, needle);
    if (count != 1) {
        std.debug.print("expected exactly one marker, found {d}: {s}\n", .{ count, needle });
        return error.UnexpectedMarkerCount;
    }
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    const count = std.mem.count(u8, haystack, needle);
    if (count != 0) {
        std.debug.print("expected marker to be absent, found {d}: {s}\n", .{ count, needle });
        return error.UnexpectedMarkerCount;
    }
}

fn sliceBetween(haystack: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.MissingStartMarker;
    const body_start = start_index + start.len;
    const end_relative = std.mem.indexOf(u8, haystack[body_start..], end) orelse return error.MissingEndMarker;
    return haystack[body_start .. body_start + end_relative];
}

fn quoted(path: []const u8, buffer: []u8) ![]const u8 {
    return try std.fmt.bufPrint(buffer, "\"{s}\"", .{path});
}

fn tupleEntry(value: []const u8, buffer: []u8) ![]const u8 {
    return try std.fmt.bufPrint(buffer, "\"{s}\",", .{value});
}

fn stripTrailingNewline(value: []const u8) []const u8 {
    if (value.len > 0 and value[value.len - 1] == '\n') {
        return value[0 .. value.len - 1];
    }
    return value;
}

test "shared reminder checker keeps the current required file inventory" {
    const checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase1-shared-reminder-packet.py");
    defer std.testing.allocator.free(checker);

    const inventory = try sliceBetween(checker, "REQUIRED_FILES = (\n", ")\n\nMARKERS = {");
    try expectContainsOnce(checker, "REQUIRED_FILES = (\n");

    var previous_index: usize = 0;
    for (required_files) |path| {
        var marker_buffer: [256]u8 = undefined;
        const marker = try quoted(path, &marker_buffer);
        try expectContainsOnce(inventory, marker);

        const index = std.mem.indexOf(u8, inventory, marker) orelse unreachable;
        try std.testing.expect(index >= previous_index);
        previous_index = index + marker.len;
    }

    try expectNotContains(inventory, "\"scripts/zigux/check-phase1-parity.py\"");
    try expectNotContains(inventory, "\"scripts/zigux/validate-phase1.py\"");
    try expectNotContains(inventory, "\"zigux/tests/phase1_bench.zig\"");
}

test "shared reminder checker owns tests-root and workflow marker buckets" {
    const checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase1-shared-reminder-packet.py");
    defer std.testing.allocator.free(checker);

    try expectContainsOnce(checker, "\"zigux/tests/README.md\": (");
    try expectContainsOnce(checker, "\".github/workflows/zigux-bootstrap.yml\": (");

    for (workflow_shared_reminder_gate) |marker| {
        const stripped = stripTrailingNewline(marker);
        var marker_buffer: [256]u8 = undefined;
        try expectContainsOnce(checker, try tupleEntry(stripped, &marker_buffer));
    }
}

test "workflow runs the shared reminder gate immediately before closure validation" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    var cursor: usize = 0;
    for (workflow_shared_reminder_gate) |marker| {
        const relative = std.mem.indexOf(u8, workflow[cursor..], marker) orelse {
            std.debug.print("missing workflow marker after offset {d}: {s}\n", .{ cursor, marker });
            return error.MissingMarker;
        };
        cursor += relative + marker.len;
    }
}

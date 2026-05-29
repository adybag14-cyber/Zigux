const std = @import("std");

const max_file_size = 512 * 1024;

const Gate = struct {
    name: []const u8,
    command: []const u8,
};

const phase1_workflow_gate_roster = [_]Gate{
    .{
        .name = "direct-owner self-test",
        .command = "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    },
    .{
        .name = "direct-owner packet",
        .command = "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    },
    .{
        .name = "direct-anchor manifest self-test",
        .command = "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    },
    .{
        .name = "direct-anchor manifest packet",
        .command = "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    },
    .{
        .name = "string review self-test",
        .command = "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    },
    .{
        .name = "string review packet",
        .command = "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    },
    .{
        .name = "find-bit review self-test",
        .command = "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    },
    .{
        .name = "find-bit review packet",
        .command = "run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    },
    .{
        .name = "bitmap direct-anchor self-test",
        .command = "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    },
    .{
        .name = "bitmap direct-anchor packet",
        .command = "run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    },
    .{
        .name = "rbtree review self-test",
        .command = "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    },
    .{
        .name = "rbtree review packet",
        .command = "run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    },
    .{
        .name = "route summary self-test",
        .command = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    },
    .{
        .name = "route summary packet",
        .command = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    },
    .{
        .name = "bench checker self-test",
        .command = "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    },
    .{
        .name = "find-bit bench anchor self-test",
        .command = "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    },
    .{
        .name = "find-bit bench anchor packet",
        .command = "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    },
    .{
        .name = "shared reminder self-test",
        .command = "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    },
    .{
        .name = "shared reminder packet",
        .command = "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    },
    .{
        .name = "closure validator self-test",
        .command = "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    },
    .{
        .name = "closure packet",
        .command = "run: python3 scripts/zigux/validate-phase1-closure.py",
    },
    .{
        .name = "shared tests-root smoke",
        .command = "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    },
};

fn expectContains(haystack: []const u8, needle: []const u8) !usize {
    const index = std.mem.indexOf(u8, haystack, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
    return index;
}

fn expectContainsAfter(haystack: []const u8, needle: []const u8, after: usize) !usize {
    const relative = std.mem.indexOf(u8, haystack[after..], needle) orelse {
        std.debug.print("missing marker after offset {d}: {s}\n", .{ after, needle });
        return error.MissingMarker;
    };
    return after + relative;
}

fn expectOccursOnce(haystack: []const u8, needle: []const u8) !void {
    const matches = std.mem.count(u8, haystack, needle);
    if (matches != 1) {
        std.debug.print("expected one occurrence of {s}, got {d}\n", .{ needle, matches });
        return error.UnexpectedMarkerCount;
    }
}

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

test "phase1 workflow gate roster remains ordered" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    var cursor: usize = 0;
    for (phase1_workflow_gate_roster) |gate| {
        const command_line = try std.fmt.allocPrint(std.testing.allocator, "{s}\n", .{gate.command});
        defer std.testing.allocator.free(command_line);

        try expectOccursOnce(workflow, command_line);
        cursor = try expectContainsAfter(workflow, command_line, cursor);
    }
}

test "tests readme still points at the shared phase1 route" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);
    const tests_readme = try readRepoFile(std.testing.allocator, "zigux/tests/README.md");
    defer std.testing.allocator.free(tests_readme);

    const route = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig";
    _ = try expectContains(tests_readme, "## Phase 1 host-tools review packet");
    _ = try expectContains(tests_readme, "current direct-readback Phase 1 reminder packet");
    _ = try expectContains(tests_readme, route);
    _ = try expectContains(workflow, route);
}

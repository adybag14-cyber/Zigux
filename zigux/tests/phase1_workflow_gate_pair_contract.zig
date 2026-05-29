const std = @import("std");

const max_file_size = 512 * 1024;

const GatePair = struct {
    self_test_name: []const u8,
    self_test_command: []const u8,
    packet_name: []const u8,
    packet_command: []const u8,
};

const phase1_gate_pairs = [_]GatePair{
    .{
        .self_test_name = "      - name: Self-test current Phase 1 direct-owner checker\n",
        .self_test_command = "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\n",
        .packet_name = "      - name: Check current Phase 1 direct-owner markers\n",
        .packet_command = "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n",
    },
    .{
        .self_test_name = "      - name: Self-test current Phase 1 direct-anchor manifest gate\n",
        .self_test_command = "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test\n",
        .packet_name = "      - name: Check current Phase 1 direct-anchor manifest gate\n",
        .packet_command = "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\n",
    },
    .{
        .self_test_name = "      - name: Self-test current Phase 1 string review checker\n",
        .self_test_command = "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test\n",
        .packet_name = "      - name: Check current Phase 1 string review packet\n",
        .packet_command = "        run: python3 scripts/zigux/check-phase1-string-review-packet.py\n",
    },
    .{
        .self_test_name = "      - name: Self-test current Phase 1 find-bit review checker\n",
        .self_test_command = "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test\n",
        .packet_name = "      - name: Check current Phase 1 find-bit review packet\n",
        .packet_command = "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py\n",
    },
    .{
        .self_test_name = "      - name: Self-test current Phase 1 bitmap direct-anchor checker\n",
        .self_test_command = "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test\n",
        .packet_name = "      - name: Check current Phase 1 bitmap direct-anchor packet\n",
        .packet_command = "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py\n",
    },
    .{
        .self_test_name = "      - name: Self-test current Phase 1 rbtree review checker\n",
        .self_test_command = "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test\n",
        .packet_name = "      - name: Check current Phase 1 rbtree review packet\n",
        .packet_command = "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py\n",
    },
    .{
        .self_test_name = "      - name: Self-test current Phase 1 route summary checker\n",
        .self_test_command = "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\n",
        .packet_name = "      - name: Check current Phase 1 route summary packet\n",
        .packet_command = "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py\n",
    },
    .{
        .self_test_name = "      - name: Self-test current Phase 1 find-bit bench anchor checker\n",
        .self_test_command = "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\n",
        .packet_name = "      - name: Check current Phase 1 find-bit bench anchor packet\n",
        .packet_command = "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py\n",
    },
    .{
        .self_test_name = "      - name: Self-test current Phase 1 shared reminder checker\n",
        .self_test_command = "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n",
        .packet_name = "      - name: Check current Phase 1 shared reminder packet\n",
        .packet_command = "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n",
    },
    .{
        .self_test_name = "      - name: Self-test current Phase 1 closure validator\n",
        .self_test_command = "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n",
        .packet_name = "      - name: Check current Phase 1 closure packet\n",
        .packet_command = "        run: python3 scripts/zigux/validate-phase1-closure.py\n",
    },
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

fn expectOne(haystack: []const u8, needle: []const u8) !usize {
    const count = std.mem.count(u8, haystack, needle);
    if (count != 1) {
        std.debug.print("expected exactly one marker, found {d}: {s}\n", .{ count, needle });
        return error.UnexpectedMarkerCount;
    }
    return std.mem.indexOf(u8, haystack, needle).?;
}

fn expectAfter(haystack: []const u8, needle: []const u8, after: usize) !usize {
    const relative = std.mem.indexOf(u8, haystack[after..], needle) orelse {
        std.debug.print("missing marker after offset {d}: {s}\n", .{ after, needle });
        return error.MissingMarker;
    };
    return after + relative;
}

test "phase1 workflow self-tests stay paired with their live packets" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    var cursor: usize = 0;
    for (phase1_gate_pairs) |pair| {
        const self_name = try expectAfter(workflow, pair.self_test_name, cursor);
        const self_command = try expectAfter(workflow, pair.self_test_command, self_name + pair.self_test_name.len);
        const packet_name = try expectAfter(workflow, pair.packet_name, self_command + pair.self_test_command.len);
        const packet_command = try expectAfter(workflow, pair.packet_command, packet_name + pair.packet_name.len);

        try std.testing.expectEqual(self_name + pair.self_test_name.len, self_command);
        try std.testing.expectEqual(packet_name + pair.packet_name.len, packet_command);
        cursor = packet_command + pair.packet_command.len;
    }
}

test "phase1 workflow singleton gates keep their explicit positions" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    const route_summary_packet = try expectOne(workflow, "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py\n");
    const bench_self_test = try expectOne(workflow, "        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n");
    const find_bit_bench_self_test = try expectOne(workflow, "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\n");
    const closure_packet = try expectOne(workflow, "        run: python3 scripts/zigux/validate-phase1-closure.py\n");
    const shared_smoke = try expectOne(workflow, "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n");

    try std.testing.expect(route_summary_packet < bench_self_test);
    try std.testing.expect(bench_self_test < find_bit_bench_self_test);
    try std.testing.expect(closure_packet < shared_smoke);
}

const std = @import("std");
const lane05_options = @import("lane05_options");

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        lane05_options.workflow_path,
        allocator,
        .limited(256 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn exactLineIndex(haystack: []const u8, line: []const u8) ?usize {
    var index: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |candidate| {
        if (std.mem.eql(u8, std.mem.trim(u8, candidate, " \t\r"), line)) {
            return index;
        }
        index += 1;
    }
    return null;
}

fn expectLineBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = exactLineIndex(haystack, first) orelse return error.MissingFirstMarker;
    const second_index = exactLineIndex(haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn expectExactLineCount(haystack: []const u8, line: []const u8, expected: usize) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |candidate| {
        if (std.mem.eql(u8, std.mem.trim(u8, candidate, " \t\r"), line)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(expected, count);
}

test "phase 11 inventory gates hand off to phase 12 build-only surface" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const phase11_selftest = "run: python3 scripts/zigux/check-phase11-build-inventory.py --self-test";
    const phase11_check = "run: python3 scripts/zigux/check-phase11-build-inventory.py";
    const phase11_validate = "run: make -C zigux phase11-validate";
    const phase12_selftest = "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test";
    const phase12_check = "run: python3 scripts/zigux/check-build-only-phase12-surface.py";

    try expectExactLineCount(workflow, phase11_selftest, 1);
    try expectExactLineCount(workflow, phase11_check, 1);
    try expectExactLineCount(workflow, phase11_validate, 1);
    try expectExactLineCount(workflow, phase12_selftest, 1);
    try expectExactLineCount(workflow, phase12_check, 1);

    try expectLineBefore(workflow, phase11_selftest, phase11_check);
    try expectLineBefore(workflow, phase11_check, phase11_validate);
    try expectLineBefore(workflow, phase11_validate, phase12_selftest);
    try expectLineBefore(workflow, phase12_selftest, phase12_check);
}

test "phase 12 validation stays ordered before smoke and aggregate routes" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const release_selftest = "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test";
    const release_check = "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py";
    const validate = "run: python3 scripts/zigux/validate-phase12.py";
    const smoke = "run: make -C zigux phase12-smoke";
    const shared = "run: make -C zigux phase12-test";
    const aggregate = "run: make -C zigux phase12";

    try expectExactLineCount(workflow, release_selftest, 1);
    try expectExactLineCount(workflow, release_check, 1);
    try expectExactLineCount(workflow, validate, 1);
    try expectExactLineCount(workflow, smoke, 1);
    try expectExactLineCount(workflow, shared, 1);
    try expectExactLineCount(workflow, aggregate, 1);

    try expectLineBefore(workflow, release_selftest, release_check);
    try expectLineBefore(workflow, release_check, validate);
    try expectLineBefore(workflow, validate, smoke);
    try expectLineBefore(workflow, smoke, shared);
    try expectLineBefore(workflow, shared, aggregate);
}

test "phase 12 libbpf and complex-driver checks precede the phase 14 tail" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const complex_driver = "run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py";
    const cross_compile = "run: python3 scripts/zigux/check-phase12-cross-compile-smoke.py";
    const libbpf_snapshot = "run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py";
    const libbpf_heavy = "run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py";
    const throughput = "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all";
    const phase14 = "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test";

    try expectContains(workflow, "Self-test current Phase 12 complex-driver lane packet checker");
    try expectExactLineCount(workflow, complex_driver, 1);
    try expectExactLineCount(workflow, cross_compile, 1);
    try expectExactLineCount(workflow, libbpf_snapshot, 1);
    try expectExactLineCount(workflow, libbpf_heavy, 1);
    try expectExactLineCount(workflow, throughput, 1);
    try expectExactLineCount(workflow, phase14, 1);

    try expectLineBefore(workflow, complex_driver, cross_compile);
    try expectLineBefore(workflow, cross_compile, libbpf_snapshot);
    try expectLineBefore(workflow, libbpf_snapshot, libbpf_heavy);
    try expectLineBefore(workflow, libbpf_heavy, throughput);
    try expectLineBefore(workflow, throughput, phase14);
}

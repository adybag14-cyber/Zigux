const std = @import("std");

const ordered_checker_steps = [_][]const u8{
    "      - name: Self-test current Phase 2 cross checker\n        run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "      - name: Check current Phase 2 direct cross-route packet\n        run: python3 scripts/zigux/check-phase2-cross.py",
    "      - name: Self-test current Phase 2 cross selftest alignment checker\n        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "      - name: Check current Phase 2 cross alignment packet\n        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
};

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        allocator,
        .limited(512 * 1024),
    ) catch |err| switch (err) {
        error.FileNotFound => std.Io.Dir.cwd().readFileAlloc(
            io_instance.io(),
            "../../.github/workflows/zigux-bootstrap.yml",
            allocator,
            .limited(512 * 1024),
        ),
        else => err,
    };
}

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !usize {
    const count = countNeedle(haystack, needle);
    try std.testing.expectEqual(@as(usize, 1), count);
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingNeedle;
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 0), countNeedle(haystack, needle));
}

test "Phase 2 cross checker workflow steps stay ordered before pinning" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const tests_readme_gate = try requireOnce(
        workflow,
        "      - name: Check current Phase 2 tests README packet\n        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    );
    const toolchain_pinning_gate = try requireOnce(
        workflow,
        "      - name: Self-test current Phase 2 toolchain pinning checker\n        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    );

    var previous = tests_readme_gate;
    for (ordered_checker_steps) |step| {
        const current = try requireOnce(workflow, step);
        try std.testing.expect(current > previous);
        previous = current;
    }
    try std.testing.expect(toolchain_pinning_gate > previous);
}

test "Phase 2 cross make route stays between fixdep and required-route guards" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const fixdep_route = try requireOnce(
        workflow,
        "      - name: Run current Phase 2 fixdep make route\n        run: make -C zigux phase2-fixdep",
    );
    const cross_route = try requireOnce(
        workflow,
        "      - name: Run current Phase 2 cross make route\n        run: make -C zigux phase2-cross",
    );
    const required_routes = try requireOnce(
        workflow,
        "      - name: Self-test current Phase 2 required-make-routes checker\n        run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    );

    try std.testing.expect(cross_route > fixdep_route);
    try std.testing.expect(required_routes > cross_route);
}

test "Phase 2 cross workflow does not revive stale matrix target job" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireAbsent(workflow, "Detect Phase 2 cross-target scope changes");
    try requireAbsent(workflow, "Check bounded Phase 2 cross-target compile");
    try requireAbsent(workflow, "python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}");
    try requireAbsent(workflow, "  phase2-cross:\n");
    try requireAbsent(workflow, "matrix:\n        zig_target:");
}

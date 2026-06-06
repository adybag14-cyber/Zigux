const std = @import("std");
const build_options = @import("build_options");

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    ReorderedMarker,
    StaleTerminalRoute,
};

const aggregate_marker =
    \\      - name: Run current Phase 12 aggregate route
    \\        run: make -C zigux phase12
;

const virtio_syntax_marker =
    \\      - name: Run current Phase 12 virtio_net syntax-lab companion
    \\        run: make -C zigux phase12-virtio-net-syntax-lab-test
;

const phase14_selftest_marker =
    \\      - name: Self-test current Phase 14 shared smoke route checker
    \\        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
;

const phase14_validate_marker =
    \\      - name: Run current Phase 14 validate route
    \\        run: make -C zigux phase14-validate
;

const throughput_marker =
    \\      - name: Run current Phase 12 throughput-parity anchor
    \\        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all
;

fn readWorkflow(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(256 * 1024),
    );
}

fn requireExactlyOnce(workflow: []const u8, marker: []const u8) !usize {
    const first = std.mem.indexOf(u8, workflow, marker) orelse return WorkflowError.MissingMarker;
    const after_first = first + marker.len;
    if (std.mem.indexOf(u8, workflow[after_first..], marker) != null) return WorkflowError.DuplicateMarker;
    return first;
}

fn requireBefore(before: usize, after: usize) !void {
    if (before >= after) return WorkflowError.ReorderedMarker;
}

fn assertBridgeContract(workflow: []const u8) !void {
    const aggregate = try requireExactlyOnce(workflow, aggregate_marker);
    const syntax_lab = try requireExactlyOnce(workflow, virtio_syntax_marker);
    const phase14_selftest = try requireExactlyOnce(workflow, phase14_selftest_marker);
    const phase14_validate = try requireExactlyOnce(workflow, phase14_validate_marker);
    const throughput = try requireExactlyOnce(workflow, throughput_marker);

    try requireBefore(aggregate, syntax_lab);
    try requireBefore(syntax_lab, phase14_selftest);
    try requireBefore(phase14_selftest, phase14_validate);
    try requireBefore(phase14_validate, throughput);

    if (std.mem.indexOf(u8, workflow[phase14_validate..throughput], "make -C zigux phase14-test") != null) {
        return WorkflowError.StaleTerminalRoute;
    }
}

test "lane17 phase12 virtio syntax lab bridges into the phase14 tail" {
    const workflow = try readWorkflow(std.testing.allocator, build_options.workflow_path);
    defer std.testing.allocator.free(workflow);

    try assertBridgeContract(workflow);
}

test "bridge contract fails closed when a required command is missing" {
    const missing_syntax =
        aggregate_marker ++ "\n" ++
        phase14_selftest_marker ++ "\n" ++
        phase14_validate_marker ++ "\n" ++
        throughput_marker ++ "\n";

    try std.testing.expectError(WorkflowError.MissingMarker, assertBridgeContract(missing_syntax));
}

test "bridge contract rejects duplicate terminal anchors" {
    const duplicated_throughput =
        aggregate_marker ++ "\n" ++
        virtio_syntax_marker ++ "\n" ++
        phase14_selftest_marker ++ "\n" ++
        phase14_validate_marker ++ "\n" ++
        throughput_marker ++ "\n" ++
        throughput_marker ++ "\n";

    try std.testing.expectError(WorkflowError.DuplicateMarker, assertBridgeContract(duplicated_throughput));
}

test "bridge contract rejects reordered phase14 handoff markers" {
    const reordered =
        aggregate_marker ++ "\n" ++
        phase14_selftest_marker ++ "\n" ++
        virtio_syntax_marker ++ "\n" ++
        phase14_validate_marker ++ "\n" ++
        throughput_marker ++ "\n";

    try std.testing.expectError(WorkflowError.ReorderedMarker, assertBridgeContract(reordered));
}

test "bridge contract rejects stale broad phase14 terminal routes" {
    const stale_terminal =
        aggregate_marker ++ "\n" ++
        virtio_syntax_marker ++ "\n" ++
        phase14_selftest_marker ++ "\n" ++
        phase14_validate_marker ++ "\n" ++
        "        run: make -C zigux phase14-test\n" ++
        throughput_marker ++ "\n";

    try std.testing.expectError(WorkflowError.StaleTerminalRoute, assertBridgeContract(stale_terminal));
}

const std = @import("std");
const testing = std.testing;

test "docs root keeps the shared phase10 reminder packet explicit" {
    const docs_root = try readFile("Documentation/zigux/README.md");
    defer testing.allocator.free(docs_root);

    try requireAll(docs_root, &.{
        "Phase 10 notes",
        "Documentation/zigux/phase10-closure-evidence.md",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "zigux/tests/phase10_closure_manifest.json",
        "zigux/tests/phase10_build.zig",
        "drivers/virtio/virtio_input_probe_preflight.zig",
        "make -C zigux phase10-validate",
        "make -C zigux phase10-test",
        "make -C zigux phase10",
        "risky transport stays parked behind the shared closure manifest",
    });
    try requireBefore(docs_root, "Phase 10 notes", "Phase 12 notes");
}

test "review checklist and companion notes agree on phase10 route and freeze boundaries" {
    const review_checklist = try readFile("Documentation/zigux/review-checklist.md");
    defer testing.allocator.free(review_checklist);
    const closure_evidence = try readFile("Documentation/zigux/phase10-closure-evidence.md");
    defer testing.allocator.free(closure_evidence);
    const lane_sequencing = try readFile("Documentation/zigux/phase10-virtio-driver-lane-sequencing.md");
    defer testing.allocator.free(lane_sequencing);

    try requireAll(review_checklist, &.{
        "shared Phase 10 virtio closure packet",
        "Documentation/zigux/phase10-closure-evidence.md",
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
        "make -C zigux phase10-validate",
        "make -C zigux phase10-test",
        "make -C zigux phase10",
    });

    try requireAll(closure_evidence, &.{
        "PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport",
        "scripts/zigux/check-phase10-shared-freeze-boundary.py",
        "scripts/zigux/check-phase10-closure-manifest-counts.py",
        "drivers/virtio/virtio_input_probe_preflight.zig",
        "kernel/workqueue.c",
        "kernel/trace/ring_buffer.c",
        "remain separate Phase 14 study-only anchors rather than Phase 10 closure evidence",
    });

    try requireAll(lane_sequencing, &.{
        "shared reminder lane owns the shared packet truthfulness surfaces only",
        "risky-transport follow-through stays outside the shared reminder lane",
        "phase10-virtio-input-registration-lifecycle",
        "phase10-mmio-lifecycle-and-irq-paths",
    });
}

test "tests and scripts roots keep phase10 build evidence bounded" {
    const tests_readme = try readFile("zigux/tests/README.md");
    defer testing.allocator.free(tests_readme);
    const scripts_readme = try readFile("scripts/zigux/README.md");
    defer testing.allocator.free(scripts_readme);
    const phase10_build = try readFile("zigux/tests/phase10_build.zig");
    defer testing.allocator.free(phase10_build);

    try requireAll(tests_readme, &.{
        "Phase 10",
        "Documentation/zigux/phase10-closure-evidence.md",
        "zigux/tests/phase10_closure_manifest.json",
        "zigux/tests/phase10_build.zig",
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    });

    try requireAll(scripts_readme, &.{
        "## Phase 10",
        "scripts/zigux/check-phase10-bootstrap-route.py",
        "scripts/zigux/check-phase10-ring-packet.py",
        "scripts/zigux/check-phase10-input-packet.py",
        "scripts/zigux/check-phase10-mmio-packet.py",
        "scripts/zigux/validate-phase10.py",
        "scripts/zigux/validate-phase10-closure.py",
        "make -C zigux phase10-validate",
        "make -C zigux phase10-test",
        "make -C zigux phase10",
    });

    try requireAll(phase10_build, &.{
        "phase10-virtio-input-probe-preflight",
        "phase10-virtio-ring",
        "phase10-virtio-mmio",
    });
}

fn readFile(comptime path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireAll(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
    }
}

fn requireBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

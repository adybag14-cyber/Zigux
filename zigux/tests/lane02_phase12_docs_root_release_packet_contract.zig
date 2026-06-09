const std = @import("std");
const testing = std.testing;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try expectContains(haystack, needle);
    }
}

fn expectFileContainsAll(path: []const u8, needles: []const []const u8) !void {
    const bytes = try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(512 * 1024),
    );
    defer testing.allocator.free(bytes);
    try expectAll(bytes, needles);
}

fn expectFileContains(path: []const u8, needle: []const u8) !void {
    const bytes = try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(512 * 1024),
    );
    defer testing.allocator.free(bytes);
    try expectContains(bytes, needle);
}

test "docs root and review checklist keep Phase 12 release packet bounded" {
    try expectFileContainsAll("Documentation/zigux/README.md", &.{
        "Phase 12 notes",
        "`Documentation/zigux/phase12-release-sequencing.md`",
        "`Documentation/zigux/phase12-release-readiness-survey.md`",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md`",
        "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
        "`Documentation/zigux/review-checklist.md`",
        "`scripts/zigux/README.md`",
        "`zigux/tests/README.md`",
        "make -C zigux phase12-validate",
        "make -C zigux phase12-smoke",
        "make -C zigux phase12-test",
        "make -C zigux phase12",
        "six-file `virtio_net` smoke-and-test sextet",
        "below DMA-safe receive ownership",
        "deeper transport lifecycle",
    });

    try expectFileContainsAll("Documentation/zigux/review-checklist.md", &.{
        "if the change touches the shared Phase 12 release packet",
        "`scripts/zigux/check-build-only-phase12-surface.py`",
        "`scripts/zigux/check-phase12-release-readiness-packet.py`",
        "`scripts/zigux/validate-phase12.py`",
        "`zigux/Makefile`",
        "make -C zigux phase12-validate",
        "make -C zigux phase12-smoke",
        "make -C zigux phase12-test",
        "make -C zigux phase12",
        "directly readable scripts-side support packet stays explicit as shared reminder evidence",
    });

    try expectFileContainsAll("Documentation/zigux/freeze-map.md", &.{
        "`net/core/skbuff.c`",
        "`kernel/workqueue.c`",
        "`kernel/trace/ring_buffer.c`",
        "study-only anchors",
        "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked",
    });
}

test "Phase 12 release notes keep shared route and driver-local split explicit" {
    const shared_support = [_][]const u8{
        "`scripts/zigux/check-build-only-phase12-surface.py`",
        "`scripts/zigux/check-phase12-release-readiness-packet.py`",
        "`scripts/zigux/validate-phase12.py`",
        "`zigux/tests/phase12_build.zig`",
        "`zigux/Makefile`",
    };
    const returned_routes = [_][]const u8{
        "phase12-validate",
        "phase12-smoke",
        "phase12-test",
        "phase12",
    };
    const split_boundaries = [_][]const u8{
        "six-file `virtio_net`",
        "`virtio_scsi`",
        "NVMe",
        "libbpf",
        "not a release-closure claim",
    };

    try expectFileContainsAll("Documentation/zigux/phase12-release-sequencing.md", &shared_support);
    try expectFileContainsAll("Documentation/zigux/phase12-release-sequencing.md", &returned_routes);
    try expectFileContainsAll("Documentation/zigux/phase12-release-sequencing.md", &split_boundaries);
    try expectFileContains(
        "Documentation/zigux/phase12-release-sequencing.md",
        "bounded `virtio_net` follow-up packet",
    );

    try expectFileContainsAll("Documentation/zigux/phase12-release-readiness-survey.md", &shared_support);
    try expectFileContainsAll("Documentation/zigux/phase12-release-readiness-survey.md", &returned_routes);
    try expectFileContainsAll("Documentation/zigux/phase12-release-readiness-survey.md", &split_boundaries);
    try expectFileContains(
        "Documentation/zigux/phase12-release-readiness-survey.md",
        "release-readiness reading, not a release-closure claim",
    );
}

test "scripts, tests, Makefile, and build root agree on returned Phase 12 route shape" {
    const support_bundle = [_][]const u8{
        "`scripts/zigux/validate-phase12.py`",
        "`scripts/zigux/check-build-only-phase12-surface.py`",
        "`scripts/zigux/check-phase12-release-readiness-packet.py`",
        "make -C zigux phase12-validate",
        "make -C zigux phase12-smoke",
        "make -C zigux phase12-test",
        "make -C zigux phase12",
    };
    try expectFileContainsAll("scripts/zigux/README.md", &support_bundle);
    try expectFileContainsAll("zigux/tests/README.md", &support_bundle);

    const virtio_net_replays = [_][]const u8{
        "phase12_virtio_net_queue_resume.zig",
        "phase12_virtio_net_receive_refill_replay.zig",
        "phase12_virtio_net_transmit_recycle.zig",
        "phase12_virtio_net_post_reset_replay.zig",
        "phase12_virtio_net_throughput_parity.zig",
        "phase12_virtio_net_survey.zig",
    };
    try expectFileContainsAll("zigux/tests/phase12_build.zig", &virtio_net_replays);
    try expectFileContainsAll("zigux/tests/README.md", &virtio_net_replays);
    try expectFileContains("zigux/tests/phase12_build.zig", "const smoke_step = b.step(");
    try expectFileContains("zigux/tests/phase12_build.zig", "const test_step = b.step(");

    try expectFileContainsAll("zigux/Makefile", &.{
        ".PHONY:",
        "phase12-validate",
        "phase12-smoke",
        "phase12-test",
        "phase12:",
        "check-build-only-phase12-surface.py",
        "check-phase12-release-readiness-packet.py",
        "validate-phase12.py --self-test",
        "build smoke --build-file zigux/tests/phase12_build.zig",
        "build test --build-file zigux/tests/phase12_build.zig",
    });
}

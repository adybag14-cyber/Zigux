const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    const io = std.testing.io;
    return std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(128 * 1024),
    );
}

test "phase 8 libbpf-segment compatibility witness keeps the focused verify-routing replay visible" {
    const routed_review_witness = try readRepoFile("zigux/tests/phase8_verify_routing_gap.zig");
    defer std.testing.allocator.free(routed_review_witness);

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            routed_review_witness,
            "phase 8 verify routing witness records the current CPU-index verifier closure",
        ) != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            routed_review_witness,
            "phase 8 verify routing witness records the current direct-readback libbpf survey packet",
        ) != null,
    );

    const routed_review_build = try readRepoFile("zigux/tests/phase8_verify_routing_gap_only_build.zig");
    defer std.testing.allocator.free(routed_review_build);

    try std.testing.expect(
        std.mem.indexOf(u8, routed_review_build, "phase8_verify_routing_gap.zig") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, routed_review_build, "phase8_verify_routing_gap") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            routed_review_build,
            "Run the phase 8 verify routing witness tests.",
        ) != null,
    );
}

test "phase 8 libbpf-segment compatibility witness keeps the shared no-timer poll boundary explicit" {
    const survey = try readRepoFile("Documentation/zigux/phase8-libbpf-segment-survey.md");
    defer std.testing.allocator.free(survey);

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            survey,
            "The timing-adjacent poll boundary is already explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `make -C zigux phase8-perf-buffer-poll-test`; those reminder surfaces keep the packet honest about no standalone timer or clockevent helper behavior and about no broader timeout-sensitive routing behavior.",
        ) != null,
    );

    const bridge_boundary = try readRepoFile(
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    );
    defer std.testing.allocator.free(bridge_boundary);

    try std.testing.expect(
        std.mem.indexOf(u8, bridge_boundary, "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, bridge_boundary, "`python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, bridge_boundary, "standalone timer helper behavior") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, bridge_boundary, "standalone clockevent helper behavior") != null,
    );

    const poll_slice = try readRepoFile("Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer std.testing.allocator.free(poll_slice);

    try std.testing.expect(
        std.mem.indexOf(u8, poll_slice, "no standalone timer helper behavior") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, poll_slice, "no standalone clockevent helper behavior") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, poll_slice, "broader perf-buffer-online-cpu-routing parity") != null,
    );
}

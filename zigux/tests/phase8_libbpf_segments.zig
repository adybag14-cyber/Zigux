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

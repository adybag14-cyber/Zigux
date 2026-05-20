const std = @import("std");

pub fn build(b: *std.Build) void {
    const test_step = b.addTest(.{
        .name = "phase8_verify_routing_gap",
        .root_source_file = b.path("phase8_verify_routing_gap.zig"),
        .target = b.graph.host,
    });

    const run = b.addRunArtifact(test_step);
    const step = b.step("test", "Run the phase 8 verify routing witness tests.");
    step.dependOn(&run.step);
}

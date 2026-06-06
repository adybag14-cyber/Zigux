const std = @import("std");

pub fn build(b: *std.Build) void {
    const root = b.path("phase2_archive_absent_payload_docs_contract.zig");

    const docs_contract = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = root,
        .target = b.graph.host,
    }) });

    const run_docs_contract = b.addRunArtifact(docs_contract);
    const test_step = b.step("test", "Run the Phase 2 archive absent-payload documentation contract");
    test_step.dependOn(&run_docs_contract.step);
    b.default_step.dependOn(test_step);
}

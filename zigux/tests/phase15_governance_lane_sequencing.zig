const std = @import("std");

test "phase 15 governance sequencing note keeps the owner split explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const sequencing_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-governance-lane-sequencing.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(sequencing_note);

    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "PHASE15_SEQUENCE=governance-lane-anti-overlap") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "P15-Y06") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "Documentation/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "scripts/zigux/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "Documentation/zigux/review-checklist.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "zigux/tests/README.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "Documentation/zigux/phase15-readiness-gate-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "Documentation/zigux/phase15-freeze-map-governance.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "Documentation/zigux/phase15-architecture-council-review-process.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "Documentation/zigux/phase15-parity-scorecard.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "Documentation/zigux/phase15-handoff-next-steps-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "Documentation/zigux/phase15-indefinite-c-policy.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "zigux/tests/phase15_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "keep every Phase 15 governance run parked unless a named reopen trigger fires") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "do not consume packet-local backlog") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "Do not use this lane to change any deep-core blocker disposition") != null);
}

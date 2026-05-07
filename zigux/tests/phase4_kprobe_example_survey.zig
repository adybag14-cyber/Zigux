const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor_path: []const u8,
    anchor_blob_sha: []const u8,
    sample_path: []const u8,
    sample_present: bool,
    current_replay: []const u8,
    survey_note: []const u8,
    survey_owner: []const u8,
    rollback_owner: []const u8,
    shared_gate_evidence_packet_present: bool,
    validation_entrypoint: []const u8,
    review_prompts: []const []const u8,
    non_goals: []const []const u8,
};

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isDigit(byte) and (byte < 'a' or byte > 'f')) return false;
    }
    return true;
}

test "phase4 kprobe gap manifest keeps the parked survey explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_kprobe_example_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("validation-perf", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("samples/kprobes/kprobe_example.c", manifest.anchor_path);
    try std.testing.expect(isLowerHexSha(manifest.anchor_blob_sha));
    try std.testing.expectEqualStrings("samples/zigux/kprobe_example.zig", manifest.sample_path);
    try std.testing.expect(!manifest.sample_present);
    try std.testing.expectEqualStrings(
        "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
        manifest.current_replay,
    );
    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
        manifest.survey_note,
    );
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.survey_owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.rollback_owner);
    try std.testing.expect(!manifest.shared_gate_evidence_packet_present);
    try std.testing.expectEqualStrings(
        "zig test zigux/tests/phase4_kprobe_example_survey.zig",
        manifest.validation_entrypoint,
    );
    try std.testing.expectEqual(@as(usize, 4), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.non_goals.len);
}

test "phase4 kprobe gap survey note stays honest about the parked boundary" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_kprobe_example_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    const required_markers = [_][]const u8{
        "PHASE4_KPROBE_STATUS=parked_gap_survey",
        "PHASE4_LANE_KEY=validation-perf",
        "PHASE4_ANCHOR_PATH=samples/kprobes/kprobe_example.c",
        "PHASE4_SAMPLE_PATH=samples/zigux/kprobe_example.zig",
        "PHASE4_SAMPLE_PRESENT=false",
        "PHASE4_CURRENT_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
        "PHASE4_SURVEY_OWNER=Validation and Perf Team",
        "PHASE4_ROLLBACK_OWNER=Validation and Perf Team",
        "PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=false",
        "`samples/zigux/kprobe_example.zig` is still absent",
        "Land one focused promotion that teaches the shared Phase 4 validator and gate-evidence packet",
    };

    for (required_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, note, marker) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, note, manifest.anchor_blob_sha) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, manifest.validation_entrypoint) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "claiming a shipped Zig starter") != null);
}

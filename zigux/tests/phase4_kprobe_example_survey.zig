const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor_path: []const u8,
    anchor_blob_sha: []const u8,
    sample_path: []const u8,
    sample_present: bool,
    current_replay: []const u8,
    local_lab_replay: []const u8,
    survey_note: []const u8,
    survey_owner: []const u8,
    rollback_owner: []const u8,
    shared_gate_evidence_packet_present: bool,
    validation_entrypoint: []const u8,
    reversible_delivery_evidence: []const u8,
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
    try std.testing.expectEqualStrings("P4-L23", manifest.lane_key);
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
        "make -C zigux phase4-kprobe-example-survey",
        manifest.local_lab_replay,
    );
    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
        manifest.survey_note,
    );
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.survey_owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.rollback_owner);
    try std.testing.expect(manifest.shared_gate_evidence_packet_present);
    try std.testing.expectEqualStrings(
        "zig test zigux/tests/phase4_kprobe_example_survey.zig",
        manifest.validation_entrypoint,
    );
    try std.testing.expectEqualStrings(
        "the dedicated local survey wrapper `make -C zigux phase4-kprobe-example-survey`, the direct validation entrypoint `zig test zigux/tests/phase4_kprobe_example_survey.zig`, and the adjacent shared gate-evidence packet keep the parked kprobe gap reviewable and reversible without claiming a shipped Zig starter",
        manifest.reversible_delivery_evidence,
    );
    try std.testing.expectEqual(@as(usize, 4), manifest.review_prompts.len);
    try std.testing.expectEqualStrings(
        "the survey keeps the Linux anchor path and blob sha explicit while the Zig starter stays absent",
        manifest.review_prompts[0],
    );
    try std.testing.expectEqualStrings(
        "the packet keeps the live make replay command, the dedicated local survey wrapper, and the direct validation entrypoint explicit without implying a shipped Zig sample",
        manifest.review_prompts[1],
    );
    try std.testing.expectEqualStrings(
        "the owner and rollback owner remain Validation and Perf Team while the packet stays adjacent to the shared Phase 4 validator-first route",
        manifest.review_prompts[2],
    );
    try std.testing.expectEqualStrings(
        "the packet now stays explicit in the shared gate-evidence note and the dedicated local survey wrapper without claiming a shipped Zig sample",
        manifest.review_prompts[3],
    );
    try std.testing.expectEqual(@as(usize, 3), manifest.non_goals.len);
    try std.testing.expectEqualStrings("shipped kprobe Zig starter", manifest.non_goals[0]);
    try std.testing.expectEqualStrings(
        "treating adjacent gate-evidence visibility as a shipped Zig starter",
        manifest.non_goals[1],
    );
    try std.testing.expectEqualStrings("approved kprobe perf threshold", manifest.non_goals[2]);
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
        "PHASE4_LANE_KEY=P4-L23",
        "PHASE4_ANCHOR_PATH=samples/kprobes/kprobe_example.c",
        "PHASE4_SAMPLE_PATH=samples/zigux/kprobe_example.zig",
        "PHASE4_SAMPLE_PRESENT=false",
        "PHASE4_CURRENT_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
        "PHASE4_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey",
        "PHASE4_SURVEY_OWNER=Validation and Perf Team",
        "PHASE4_ROLLBACK_OWNER=Validation and Perf Team",
        "PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=true",
        "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=the dedicated local survey wrapper `make -C zigux phase4-kprobe-example-survey`, the direct validation entrypoint `zig test zigux/tests/phase4_kprobe_example_survey.zig`, and the adjacent shared gate-evidence packet keep the parked kprobe gap reviewable and reversible without claiming a shipped Zig starter",
        "zigux/tests/phase4_kprobe_example_manifest.json",
        "zigux/tests/phase4_kprobe_example_survey.zig",
        "shared gate-evidence note now names that same survey note, manifest, replay command, local survey wrapper, direct validation entrypoint, and reversible-delivery evidence",
        "the dedicated local survey wrapper now reruns this parked packet through `make -C zigux phase4-kprobe-example-survey`, and together with the direct validation entrypoint `zig test zigux/tests/phase4_kprobe_example_survey.zig` plus the adjacent shared gate-evidence packet it serves as the reversible-delivery evidence for the parked gap",
        "`samples/zigux/kprobe_example.zig` is still absent",
        "dedicated local survey wrapper until a future bounded lane intentionally opens either the Zig starter or a broader validation-surface promotion",
        "treating adjacent gate-evidence visibility as a shipped Zig starter",
        "claiming approved hard perf thresholds for the kprobe anchor",
    };

    for (required_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, note, marker) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, note, manifest.anchor_blob_sha) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, manifest.validation_entrypoint) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, manifest.local_lab_replay) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, manifest.reversible_delivery_evidence) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "claiming a shipped Zig starter") != null);
}

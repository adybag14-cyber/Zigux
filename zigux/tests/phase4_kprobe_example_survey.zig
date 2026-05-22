const std = @import("std");

const current_surveyed_commit = "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3";

const SurveySummary = struct {
    kprobe_makefile_replay_present: bool,
    kprobe_anchor_symbol_present: bool,
    zig_sample_present: bool,
    phase4_build_present: bool,
    phase4_validation_matrix_present: bool,
    phase4_gate_evidence_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    current_replay: []const u8,
    isolated_survey_replay: []const u8,
    shared_build_replay: []const u8,
    shared_lab_and_ci_matrix_anchor: []const u8,
    threshold_posture: []const u8,
    reversible_delivery_evidence: []const u8,
    next_bounded_evidence_step: []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

const SiblingManifest = struct {
    phase: []const u8,
    surveyed_commit: []const u8,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or std.mem.eql(u8, status, "ready_next");
}

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

test "phase4 kprobe_example survey manifest records the landed survey packet and remaining sample gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_kprobe_example_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P4-L19", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.rollback_owner);
    try std.testing.expect(isLowerHexSha(current_surveyed_commit));
    try std.testing.expectEqualStrings(current_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/kprobes/kprobe_example.c", manifest.anchor);
    try std.testing.expectEqualStrings("make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m", manifest.current_replay);
    try std.testing.expectEqualStrings(
        "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
        manifest.isolated_survey_replay,
    );
    try std.testing.expectEqualStrings("phase4-kprobe-example-survey-tests", manifest.shared_build_replay);
    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
        manifest.shared_lab_and_ci_matrix_anchor,
    );
    try std.testing.expectEqualStrings("c_anchor_only_until_kprobe_example_starter_lands", manifest.threshold_posture);
    try std.testing.expectEqualStrings(
        "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the explicit local_lab_replay marker, the local survey wrapper, the explicit bootstrap-CI posture, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded starter lane intentionally widens this surface",
        manifest.reversible_delivery_evidence,
    );
    try std.testing.expectEqualStrings(
        "Keep this parked packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the dedicated local `make -C zigux phase4-kprobe-example-survey` wrapper, and the direct `zig test zigux/tests/phase4_kprobe_example_survey.zig` validation entrypoint until a later bounded Phase 4 lane lands the actual Zig starter with an updated rollback-readiness contract.",
        manifest.next_bounded_evidence_step,
    );
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("samples/zigux/kprobe_example.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqual(@as(usize, 5), manifest.gaps.len);

    const runtime_atomic64_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(runtime_atomic64_manifest_json);
    const runtime_atomic64_parsed = try std.json.parseFromSlice(
        SiblingManifest,
        std.testing.allocator,
        runtime_atomic64_manifest_json,
        .{ .ignore_unknown_fields = true },
    );
    defer runtime_atomic64_parsed.deinit();
    try std.testing.expectEqualStrings("Phase 4", runtime_atomic64_parsed.value.phase);
    try std.testing.expectEqualStrings(current_surveyed_commit, runtime_atomic64_parsed.value.surveyed_commit);

    const perf_baseline_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_perf_baseline_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(perf_baseline_manifest_json);
    const perf_baseline_parsed = try std.json.parseFromSlice(
        SiblingManifest,
        std.testing.allocator,
        perf_baseline_manifest_json,
        .{ .ignore_unknown_fields = true },
    );
    defer perf_baseline_parsed.deinit();
    try std.testing.expectEqualStrings("Phase 4", perf_baseline_parsed.value.phase);
    try std.testing.expectEqualStrings(current_surveyed_commit, perf_baseline_parsed.value.surveyed_commit);

    const anchor = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/kprobes/kprobe_example.c",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(anchor);
    const kprobes_makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/kprobes/Makefile",
        std.testing.allocator,
        .limited(8 * 1024),
    );
    defer std.testing.allocator.free(kprobes_makefile);
    const phase4_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase4_build);
    const phase4_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-validation-matrix.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase4_matrix);
    const phase4_gate_evidence = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-gate-evidence.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase4_gate_evidence);
    const kprobe_gap_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(kprobe_gap_note);

    const zig_sample_present = blk: {
        std.Io.Dir.cwd().access(io_instance.io(), "samples/zigux/kprobe_example.zig", .{}) catch |err| switch (err) {
            error.FileNotFound => break :blk false,
            else => return err,
        };
        break :blk true;
    };

    const live_summary = SurveySummary{
        .kprobe_makefile_replay_present = std.mem.indexOf(u8, kprobes_makefile, "obj-$(CONFIG_SAMPLE_KPROBES) += kprobe_example.o") != null,
        .kprobe_anchor_symbol_present = std.mem.indexOf(u8, anchor, "static char symbol[KSYM_NAME_LEN] = \"kernel_clone\";") != null,
        .zig_sample_present = zig_sample_present,
        .phase4_build_present = std.mem.indexOf(u8, phase4_build, "phase4_kprobe_example_survey.zig") != null and
            std.mem.indexOf(u8, phase4_build, manifest.shared_build_replay) != null and
            std.mem.indexOf(u8, phase4_build, "phase4-kprobe-example-survey") != null,
        .phase4_validation_matrix_present = std.mem.indexOf(u8, phase4_matrix, manifest.shared_lab_and_ci_matrix_anchor) != null and
            std.mem.indexOf(u8, phase4_matrix, "phase4_kprobe_example_manifest.json") != null and
            std.mem.indexOf(u8, phase4_matrix, "phase4_kprobe_example_survey.zig") != null and
            std.mem.indexOf(u8, phase4_matrix, manifest.shared_build_replay) != null and
            std.mem.indexOf(u8, phase4_matrix, manifest.isolated_survey_replay) != null and
            std.mem.indexOf(u8, phase4_matrix, manifest.threshold_posture) != null and
            std.mem.indexOf(u8, phase4_matrix, manifest.current_replay) != null and
            std.mem.indexOf(u8, phase4_matrix, "samples/zigux/kprobe_example.zig") != null,
        .phase4_gate_evidence_present = std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true") != null and
            std.mem.indexOf(u8, phase4_gate_evidence, "kprobe_gap_packet_presence_drift") != null and
            std.mem.indexOf(u8, phase4_gate_evidence, "kprobe_validation_entrypoint_drift") != null and
            std.mem.indexOf(u8, phase4_gate_evidence, "kprobe_next_step_drift") != null,
    };
    try std.testing.expectEqualDeep(live_summary, manifest.survey_summary);
    try std.testing.expect(std.mem.indexOf(u8, kprobe_gap_note, manifest.shared_lab_and_ci_matrix_anchor) != null);
    try std.testing.expect(std.mem.indexOf(u8, kprobe_gap_note, manifest.reversible_delivery_evidence) != null);
    try std.testing.expect(std.mem.indexOf(u8, kprobe_gap_note, manifest.next_bounded_evidence_step) != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_validator_promotion_gap = false;
    var saw_sample_gap = false;
    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));
        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        }
        if (std.mem.eql(u8, gap.id, "phase4-kprobe-example-shared-validator-promotion")) {
            saw_validator_promotion_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("scripts/zigux/validate-phase4.py", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "phase4-kprobe-example-survey-tests") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "validate-phase4.py") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase4-kprobe-example-zig-sample")) {
            saw_sample_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/kprobe_example.zig", gap.zigux_destination);
        }
        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 4), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expect(saw_validator_promotion_gap);
    try std.testing.expect(saw_sample_gap);
    try std.testing.expect(std.mem.indexOf(u8, anchor, "kernel_clone") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_build, "phase4-kprobe-example-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_build, "phase4-kprobe-example-survey") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, manifest.shared_lab_and_ci_matrix_anchor) != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_matrix, "shared `phase4-kprobe-example-survey-tests` replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true") != null);
    try std.testing.expect(std.mem.indexOf(u8, kprobe_gap_note, manifest.shared_lab_and_ci_matrix_anchor) != null);
}

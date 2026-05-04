const std = @import("std");

const archived_surveyed_commit = "1851d34766b4bc833344b3be89e4f079234212fa";

const SurveySummary = struct {
    libbpf_c_lines: usize,
    preexisting_phase8_test_files: usize,
    preexisting_phase8_build_present: bool,
    preexisting_phase8_libbpf_manifest_present: bool,
    preexisting_phase8_libbpf_survey_present: bool,
    preexisting_phase8_libbpf_note_present: bool,
    preexisting_type_names_zig_present: bool,
    preexisting_cpu_mask_zig_present: bool,
    preexisting_logging_zig_present: bool,
    preexisting_pin_path_zig_present: bool,
    preexisting_file_path_handle_bridge_zig_present: bool,
    preexisting_perf_buffer_poll_zig_present: bool,
    preexisting_phase12_build_present: bool,
    preexisting_phase12_libbpf_survey_present: bool,
    preexisting_phase12_survey_note_present: bool,
    preexisting_phase12_docs_root_packet_present: bool,
    preexisting_phase12_reviewability_gate_present: bool,
    preexisting_phase12_snapshot_checker_present: bool,
    preexisting_phase12_packet_checker_present: bool,
    preexisting_phase12_focused_replay_checker_present: bool,
    preexisting_phase12_focused_replay_build_present: bool,
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
    surveyed_commit: []const u8,
    anchor: []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn hasGap(manifest: Manifest, id: []const u8, status: []const u8, destination: []const u8) bool {
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id) and
            std.mem.eql(u8, gap.status, status) and
            std.mem.eql(u8, gap.zigux_destination, destination))
        {
            return true;
        }
    }
    return false;
}

test "phase12 libbpf survey manifest records the bounded heavy-helper packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_libbpf_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings(archived_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", manifest.anchor);
    try std.testing.expect(manifest.survey_summary.libbpf_c_lines >= 14000);
    try std.testing.expectEqual(@as(usize, 7), manifest.survey_summary.preexisting_phase8_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase8_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase8_libbpf_manifest_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase8_libbpf_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase8_libbpf_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_type_names_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_cpu_mask_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_logging_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_pin_path_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_file_path_handle_bridge_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_perf_buffer_poll_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_libbpf_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_survey_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_docs_root_packet_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_reviewability_gate_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_snapshot_checker_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_packet_checker_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_focused_replay_checker_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase12_focused_replay_build_present);
    try std.testing.expectEqual(@as(usize, 17), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var deferred_count: usize = 0;

    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_object_model")) {
            blocked_count += 1;
        } else if (std.mem.eql(u8, gap.status, "deferred_high_risk")) {
            deferred_count += 1;
        }
    }

    try std.testing.expectEqual(@as(usize, 12), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expectEqual(@as(usize, 4), deferred_count);

    try std.testing.expect(hasGap(
        manifest,
        "phase12-build-gate",
        "starter_landed",
        "zigux/tests/phase12_build.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-make-target",
        "starter_landed",
        "zigux/Makefile",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-segment-manifest-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/manifest.json",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-type-name-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/type_names.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-cpu-mask-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-file-path-handle-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-map-reuse-compatibility-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-file-path-and-handle-bridge-boundary",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-perf-buffer-online-cpu-routing-boundary",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/cpu_mask.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-survey-gate",
        "starter_landed",
        "zigux/tests/phase12_libbpf_segments.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-reviewability-gate",
        "starter_landed",
        "zigux/tests/phase12_libbpf_reviewability.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-survey-note",
        "starter_landed",
        "Documentation/zigux/phase12-libbpf-segment-survey.md",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-logging-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/logging.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-pin-path-helper-foundation",
        "starter_landed",
        "tools/lib/bpf/zigux_segments/pin_path.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-skeleton-population",
        "blocked_on_object_model",
        "tools/lib/bpf/zigux_segments/skeleton.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-object-and-elf-loader",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/object_loader.zig",
    ));
    try std.testing.expect(hasGap(
        manifest,
        "phase12-libbpf-btf-relocation-and-program-load",
        "deferred_high_risk",
        "tools/lib/bpf/zigux_segments/relocation.zig",
    ));
}

test "phase12 libbpf survey note records rollback and archived surveyed head" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-libbpf-segment-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "## Rollback And Reversible Delivery") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, archived_surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_LANE_KEY=P12-L16") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "owner: `BPF Tooling Lane`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback owner: `BPF Tooling Lane`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "fallback path: keep `tools/lib/bpf/libbpf.c` as the source of truth") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`perf_buffer_poll.zig` helper slice on its bounded helper footing") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "reversible delivery evidence: this Phase 12 packet only adds `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, and this survey note around preexisting helper foundations") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "rollback drill: run `python3 scripts/zigux/check-phase12-build-inventory.py --self-test`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "repair `scripts/zigux/check-phase12-libbpf-snapshot.py` plus `zigux/tests/fixtures/phase12_libbpf_snapshot.json` first") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12-libbpf-segment-survey-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12-libbpf-reviewability-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/check-phase12-build-inventory.py --self-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/check-phase12-build-inventory.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/check-phase12-libbpf-snapshot.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/check-phase12-libbpf-packet.py --self-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/check-phase12-libbpf-packet.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/check-phase12-libbpf-focused-replay.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase12_libbpf_only_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "focused libbpf-only replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared build-inventory, bounded libbpf snapshot, bounded libbpf packet-alignment, and focused replay checks all fail closed before the shared validator or bundled replay claim aligned evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "python3 scripts/zigux/validate-phase12.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase12-validate") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig build test --build-file zigux/tests/phase12_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the bounded file-path-and-handle helper packet now also mirrors the libbpf token-preparation recovery split more faithfully") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the legacy Phase 8 segment catalog now records the bounded `perf_buffer_poll.zig` helper as a landed helper-first slice") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "perf-buffer-online-cpu-routing stays deferred even though the bounded parser helper already lives in `cpu_mask.zig` and the bounded wait-result and ready-buffer bookkeeping helper already lives in `perf_buffer_poll.zig`") != null);
}

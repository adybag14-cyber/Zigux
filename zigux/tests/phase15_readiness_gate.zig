const std = @import("std");

const RepoEvidence = struct {
    freeze_map_present: bool,
    review_checklist_present: bool,
    review_process_present: bool,
    parity_scorecard_present: bool,
    indefinite_c_policy_present: bool,
    handoff_next_steps_present: bool,
    phase15_build_present: bool,
    phase15_validator_script_present: bool,
    phase15_validate_target_present: bool,
    phase15_make_target_present: bool,
    shared_ci_phase15_present: bool,
    phase15_replay_green_at_reviewed_head: bool,
    docs_root_phase15_summary_aligned_at_reviewed_head: bool,
    current_master_provenance_refresh_required: bool,
    deep_core_status_change_ready: bool,
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
    roadmap_phase_title: []const u8,
    roadmap_requirements: []const []const u8,
    bootstrap_ledger_anchor: []const u8,
    ledger_scope: []const []const u8,
    repo_evidence: RepoEvidence,
    remaining_gaps: []const Gap,
    next_step: []const u8,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

fn isLowerHex40(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        const is_digit = byte >= '0' and byte <= '9';
        const is_lower_hex = byte >= 'a' and byte <= 'f';
        if (!is_digit and !is_lower_hex) return false;
    }
    return true;
}

test "phase 15 readiness manifest records the roadmap, ledger, and reviewed-head repo posture" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_readiness_gate_manifest.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const readiness_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-readiness-gate-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(readiness_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expect(isLowerHex40(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("Full-Parity Blockers and Long-Term Governance", manifest.roadmap_phase_title);
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_requirements.len);
    try std.testing.expectEqualStrings("freeze map", manifest.roadmap_requirements[0]);
    try std.testing.expectEqualStrings("Architecture Council review process", manifest.roadmap_requirements[1]);
    try std.testing.expectEqualStrings("parity scorecard", manifest.roadmap_requirements[2]);
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirements[3]);
    try std.testing.expect(std.mem.indexOf(u8, manifest.bootstrap_ledger_anchor, "freeze map") != null);
    try std.testing.expectEqual(@as(usize, 3), manifest.ledger_scope.len);
    try std.testing.expectEqualStrings("Documentation/zigux/README.md", manifest.ledger_scope[0]);
    try std.testing.expectEqualStrings("Documentation/zigux/review-checklist.md", manifest.ledger_scope[1]);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.ledger_scope[2]);

    const readiness_provenance = try std.fmt.allocPrint(
        std.testing.allocator,
        "survey provenance last refreshed against reviewed `master` head `{s}`",
        .{manifest.surveyed_commit},
    );
    defer std.testing.allocator.free(readiness_provenance);

    try std.testing.expect(std.mem.indexOf(u8, readiness_note, readiness_provenance) != null);

    try std.testing.expect(manifest.repo_evidence.freeze_map_present);
    try std.testing.expect(manifest.repo_evidence.review_checklist_present);
    try std.testing.expect(manifest.repo_evidence.review_process_present);
    try std.testing.expect(manifest.repo_evidence.parity_scorecard_present);
    try std.testing.expect(manifest.repo_evidence.indefinite_c_policy_present);
    try std.testing.expect(manifest.repo_evidence.handoff_next_steps_present);
    try std.testing.expect(manifest.repo_evidence.phase15_build_present);
    try std.testing.expect(manifest.repo_evidence.phase15_validator_script_present);
    try std.testing.expect(manifest.repo_evidence.phase15_validate_target_present);
    try std.testing.expect(manifest.repo_evidence.phase15_make_target_present);
    try std.testing.expect(manifest.repo_evidence.shared_ci_phase15_present);
    try std.testing.expect(manifest.repo_evidence.phase15_replay_green_at_reviewed_head);
    try std.testing.expect(manifest.repo_evidence.docs_root_phase15_summary_aligned_at_reviewed_head);
    try std.testing.expect(manifest.repo_evidence.current_master_provenance_refresh_required);
    try std.testing.expect(!manifest.repo_evidence.deep_core_status_change_ready);

    try std.testing.expectEqual(@as(usize, 1), manifest.remaining_gaps.len);

    const gap = manifest.remaining_gaps[0];
    try std.testing.expect(isAllowedStatus(gap.status));
    try std.testing.expectEqualStrings("phase15-deep-core-status-change-blocker", gap.id);
    try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", gap.zigux_destination);
    try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "freeze-in-C posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.next_step, "shared Phase 15 replay drifts") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.next_step, "reviewed-provenance head for this packet needs refresh") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.next_step, "deep-core blocker posture changes") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.next_step, "python3 scripts/zigux/validate-phase15.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.next_step, "make -C zigux phase15-validate") != null);
}

test "phase 15 readiness note keeps the roadmap and ledger comparison explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const readiness_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-readiness-gate-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(readiness_note);

    const docs_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(docs_readme);

    const workflow = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(workflow);

    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "## Roadmap Versus Ledger") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "## Readiness at Reviewed Head") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "## Remaining Readiness Gaps") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "## Readiness Gate") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "Full-Parity Blockers and Long-Term Governance") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "docs(zigux): add documentation root, review checklist, and freeze map") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "docs-root Phase 15 summary now matches the dedicated readiness and handoff packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "The dedicated replay surfaces were green at reviewed `master` head") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "Later repo movement still requires a fresh bounded provenance refresh") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "phase15-docs-root-summary-alignment") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "phase15-deep-core-status-change-blocker") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "scripts/zigux/validate-phase15.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "make -C zigux phase15-validate") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "make -C zigux phase15") != null);
    try std.testing.expect(std.mem.indexOf(u8, readiness_note, "zig build test --build-file zigux/tests/phase15_build.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, docs_readme, "only remaining blocked work is the deep-core status-change evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_readme, "remaining broader replay drift on current `master`") == null);

    try std.testing.expect(std.mem.indexOf(u8, workflow, "Validate Phase 14 shared smoke packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 14 internal bridge tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 15 governance tests") != null);
}

test "phase 15 readiness survey stays aligned with the landed governance bundle" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const freeze_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(freeze_map);

    const review_process = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(review_process);

    const parity_scorecard = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-parity-scorecard.md",
        std.testing.allocator,
        .limited(40 * 1024),
    );
    defer std.testing.allocator.free(parity_scorecard);

    const indefinite_c_policy = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(indefinite_c_policy);

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "## Governance For Freeze-Map Changes") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_process, "## Required Review Packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, parity_scorecard, "## Roadmap Handoff Evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, indefinite_c_policy, "## When the indefinite-C policy applies") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase15-validate") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase15-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase15: phase15-validate phase15-test") != null);
}

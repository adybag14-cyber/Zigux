const std = @import("std");

const Requirement = struct {
    id: []const u8,
    summary: []const u8,
    required_terms: []const []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const ExceptionPosture = struct {
    silent_exception_path: []const u8,
    only_allowed_exception: []const u8,
    retained_closeout_state: []const u8,
    blocker_requirement: []const u8,
    required_reopen_inputs: []const []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    surveyed_commit_mode: []const u8,
    surveyed_commit_mode_reason: []const u8,
    roadmap_requirement: []const u8,
    anchors: []const []const u8,
    supporting_artifacts: []const []const u8,
    indefinite_c_requirements: []const Requirement,
    exception_posture: ExceptionPosture,
    reopen_trigger_catalog: []const []const u8,
    gaps: []const Gap,
};

const FreezeMapManifest = struct {
    freeze_in_c_targets: []const []const u8,
    study_only_targets: []const []const u8,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_stay_in_c_evidence");
}

fn expectContains(io: std.Io, path: []const u8, snippets: []const []const u8) !void {
    const contents = try std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(contents);

    for (snippets) |snippet| {
        try std.testing.expect(std.mem.indexOf(u8, contents, snippet) != null);
    }
}

test "phase 15 indefinite-C policy manifest records current policy, exception, and blocker evidence" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_indefinite_c_policy.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P15-Y04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-09", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("dated_master_readback", manifest.surveyed_commit_mode);
    try std.testing.expectEqualStrings(
        "The indefinite-C policy packet reports current stay-in-C governance posture at the bounded packet level, so it now uses an explicit dated master-readback marker instead of implying exact post-commit branch-head parity.",
        manifest.surveyed_commit_mode_reason,
    );
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 15), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.indefinite_c_requirements.len);
    try std.testing.expectEqualStrings("forbidden", manifest.exception_posture.silent_exception_path);
    try std.testing.expectEqualStrings("architecture_council_reopen_request", manifest.exception_posture.only_allowed_exception);
    try std.testing.expectEqualStrings("retired_from_active_discussion", manifest.exception_posture.retained_closeout_state);
    try std.testing.expectEqualStrings("existing_blocker_remains_recorded_until_reopen_approved", manifest.exception_posture.blocker_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.exception_posture.required_reopen_inputs.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.reopen_trigger_catalog.len);
    try std.testing.expectEqualStrings("narrower_followup_answers_blocker", manifest.reopen_trigger_catalog[0]);
    try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", manifest.reopen_trigger_catalog[1]);
    try std.testing.expectEqualStrings("ownership_or_validation_changed", manifest.reopen_trigger_catalog[2]);
    try std.testing.expectEqual(@as(usize, 8), manifest.gaps.len);

    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.anchors[0]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", manifest.supporting_artifacts[3]);
    try std.testing.expectEqualStrings("Documentation/zigux/README.md", manifest.supporting_artifacts[5]);
    try std.testing.expectEqualStrings("scripts/zigux/README.md", manifest.supporting_artifacts[6]);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase15-scripts-readme-alignment.py", manifest.supporting_artifacts[7]);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase15-review-process-handoff.py", manifest.supporting_artifacts[8]);
    try std.testing.expectEqualStrings("zigux/tests/README.md", manifest.supporting_artifacts[9]);
    try std.testing.expectEqualStrings(".github/workflows/zigux-bootstrap.yml", manifest.supporting_artifacts[10]);
    try std.testing.expectEqualStrings("zigux/Makefile", manifest.supporting_artifacts[11]);
    try std.testing.expectEqualStrings("zigux/tests/phase15_build.zig", manifest.supporting_artifacts[12]);
    try std.testing.expectEqualStrings("zigux/tests/phase15_indefinite_c_blocker_evidence.zig", manifest.supporting_artifacts[13]);
    try std.testing.expectEqualStrings("zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig", manifest.supporting_artifacts[14]);

    try std.testing.expectEqualStrings("new bounded seam inventory", manifest.exception_posture.required_reopen_inputs[0]);
    try std.testing.expectEqualStrings("updated validation plan", manifest.exception_posture.required_reopen_inputs[1]);
    try std.testing.expectEqualStrings("fresh linked evidence", manifest.exception_posture.required_reopen_inputs[2]);
    try std.testing.expectEqualStrings("Architecture Council review request", manifest.exception_posture.required_reopen_inputs[3]);

    var saw_source_of_truth = false;
    var saw_recordkeeping = false;
    var saw_allowed_work = false;
    var saw_exception_path = false;
    var saw_reopen_gate = false;
    var saw_reopen_trigger_catalog = false;

    for (manifest.indefinite_c_requirements, 0..) |requirement, i| {
        try std.testing.expect(requirement.id.len > 0);
        try std.testing.expect(requirement.summary.len > 0);
        try std.testing.expect(requirement.required_terms.len >= 2);

        if (std.mem.eql(u8, requirement.id, "indefinite-c-source-of-truth")) {
            saw_source_of_truth = true;
            try std.testing.expectEqualStrings("product source of truth", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("remains in C indefinitely", requirement.required_terms[1]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-recordkeeping")) {
            saw_recordkeeping = true;
            try std.testing.expectEqualStrings("current status bucket", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("requested decision bucket", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("decision record ID", requirement.required_terms[2]);
            try std.testing.expectEqualStrings("lane owner", requirement.required_terms[3]);
            try std.testing.expectEqualStrings("rollback owner", requirement.required_terms[4]);
            try std.testing.expectEqualStrings("validation gate summary", requirement.required_terms[5]);
            try std.testing.expectEqualStrings("latest blocker disposition", requirement.required_terms[6]);
            try std.testing.expectEqualStrings("evidence archive path", requirement.required_terms[7]);
            try std.testing.expectEqualStrings("retained discussion state", requirement.required_terms[8]);
            try std.testing.expectEqualStrings("parity scorecard link or blocker record", requirement.required_terms[9]);
            try std.testing.expectEqualStrings("explicit non-goals", requirement.required_terms[10]);
            try std.testing.expectEqualStrings("written rationale", requirement.required_terms[11]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-allowed-work")) {
            saw_allowed_work = true;
            try std.testing.expectEqualStrings("explicit stay-in-C outcome", requirement.required_terms[1]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-exception-path")) {
            saw_exception_path = true;
            try std.testing.expectEqualStrings("no silent exception path", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("Architecture Council reopen request", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("existing blocker remains recorded", requirement.required_terms[2]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-reopen-gate")) {
            saw_reopen_gate = true;
            try std.testing.expectEqualStrings("new bounded seam inventory", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("Architecture Council review request", requirement.required_terms[3]);
        } else if (std.mem.eql(u8, requirement.id, "indefinite-c-reopen-trigger-catalog")) {
            saw_reopen_trigger_catalog = true;
            try std.testing.expectEqual(manifest.reopen_trigger_catalog.len, requirement.required_terms.len);
            try std.testing.expectEqualStrings("narrower_followup_answers_blocker", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("ownership_or_validation_changed", requirement.required_terms[2]);
            for (manifest.reopen_trigger_catalog, requirement.required_terms) |catalog_item, required_term| {
                try std.testing.expectEqualStrings(catalog_item, required_term);
            }
        }

        for (manifest.indefinite_c_requirements[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, requirement.id, other.id));
        }
    }

    try std.testing.expect(saw_source_of_truth);
    try std.testing.expect(saw_recordkeeping);
    try std.testing.expect(saw_allowed_work);
    try std.testing.expect(saw_exception_path);
    try std.testing.expect(saw_reopen_gate);
    try std.testing.expect(saw_reopen_trigger_catalog);
}

test "phase 15 indefinite-C policy doc and linked artifacts keep exception and blocker posture explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    try expectContains(io_instance.io(), "Documentation/zigux/phase15-indefinite-c-policy.md", &.{
        "PHASE15_LANE_KEY=P15-Y04",
        "PHASE15_SLICE=indefinite-c-policy-current-readback-provenance-sync",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        "survey provenance refreshed against dated `master` readback marker `current-master-readback-2026-05-09` on 2026-05-09 because this policy packet reports current stay-in-C governance posture at the bounded packet level instead of implying exact post-commit branch-head parity",
        "exact branch-head parity is not recorded for this packet; the current policy packet therefore uses an explicit dated readback marker instead of implying exact-head provenance",
        "the focused blocker-evidence and lane-owner-alignment replays already shipped in the shared Phase 15 build",
        "scripts/zigux/README.md",
        "scripts/zigux/check-phase15-scripts-readme-alignment.py",
        "scripts/zigux/check-phase15-review-process-handoff.py",
        "zigux/tests/README.md",
        ".github/workflows/zigux-bootstrap.yml",
        "zigux/Makefile",
        "zigux/tests/phase15_build.zig",
        "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
        "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
        "## When the indefinite-C policy applies",
        "## Required recorded fields",
        "## Allowed work after an indefinite-C outcome",
        "## Exception posture",
        "## Reopen conditions",
        "## Reopen Trigger Catalog",
        "current status bucket",
        "requested decision bucket",
        "Documentation/zigux/README.md",
        "lane owner",
        "validation gate summary",
        "retained discussion state",
        "parity scorecard link or blocker record",
        "explicit non-goals",
        "written rationale",
        "product source of truth",
        "remains in C indefinitely",
        "explicit stay-in-C outcome",
        "no silent exception path",
        "Architecture Council reopen request",
        "existing blocker remains recorded",
        "silent exception path: `forbidden`",
        "only allowed exception: `architecture_council_reopen_request`",
        "retained closeout state: `retired_from_active_discussion`",
        "blocker requirement: `existing_blocker_remains_recorded_until_reopen_approved`",
        "These reopen inputs are the only machine-checkable path out of the retained stay-in-C closeout.",
        "retired_from_active_discussion",
        "narrower_followup_answers_blocker",
        "evidence_packet_stale_or_contradictory",
        "ownership_or_validation_changed",
    });

    try expectContains(io_instance.io(), "Documentation/zigux/freeze-map.md", &.{
        "the existing C implementation remains the product source of truth",
        "if evidence is not overwhelming, keep the code in C and document why",
    });

    try expectContains(io_instance.io(), "Documentation/zigux/phase15-architecture-council-review-process.md", &.{
        "`keep_in_c`",
        "latest blocker disposition",
        "no Architecture Council approval is currently recorded",
    });

    try expectContains(io_instance.io(), "Documentation/zigux/phase15-parity-scorecard.md", &.{
        "explicit stay-in-C outcome",
        "latest blocker disposition",
        "evidence archive path",
    });

    try expectContains(io_instance.io(), "Documentation/zigux/review-checklist.md", &.{
        "if a freeze-map anchor is closing review with a stay-in-C outcome, are the retained discussion state, the current blocker, and reopen triggers explicit?",
        "if the target stays in C, does the change record that ongoing policy honestly",
    });

    try expectContains(io_instance.io(), "Documentation/zigux/README.md", &.{
        "Phase 15 notes",
        "`Documentation/zigux/phase15-indefinite-c-policy.md`",
        "`zigux/tests/phase15_indefinite_c_policy.json`",
        "`zigux/tests/phase15_indefinite_c_policy.zig`",
        "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
        "`make -C zigux phase15-validate`",
        "`make -C zigux phase15`",
        "no Architecture Council approval is recorded yet",
    });

    try expectContains(io_instance.io(), "scripts/zigux/README.md", &.{
        "Phase 15 flow",
        "phase15-indefinite-c-policy.md",
        "check-phase15-scripts-readme-alignment.py",
        "check-phase15-review-process-handoff.py",
        "phase15_indefinite_c_policy.json",
        "phase15_indefinite_c_blocker_evidence.zig",
        "phase15_indefinite_c_policy.zig",
        "phase15_indefinite_c_lane_owner_alignment.zig",
        "phase15_build.zig",
        "make -C zigux phase15-validate",
        "make -C zigux phase15",
    });

    try expectContains(io_instance.io(), "zigux/tests/README.md", &.{
        "keep the parked Phase 15 governance packet explicit in the tests root too",
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        "zigux/tests/phase15_indefinite_c_policy.json",
        "zigux/tests/phase15_indefinite_c_policy.zig",
        "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
        "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
        "make -C zigux phase15-validate",
        "make -C zigux phase15",
        "without implying any Architecture Council approval for a freeze-map status change",
    });
}

test "phase 15 indefinite-C evidence archives and build wiring stay aligned with the policy slice" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const archive_paths = [_][]const u8{
        "Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md",
        "Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md",
        "Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md",
        "Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md",
    };

    for (archive_paths) |path| {
        try expectContains(io_instance.io(), path, &.{
            "current status bucket: `freeze_in_c`",
            "requested decision bucket: `pending_no_request`",
            "decision record ID",
            "parity scorecard link or blocker record",
            "replay command: `zig build test --build-file zigux/tests/phase15_build.zig`",
            "latest blocker disposition:",
            "retained discussion state after closeout: `retired_from_active_discussion`",
            "rollback ownership, lane ownership, or validation gates",
            "## Explicit Non-goals",
            "written rationale",
        });
    }

    try expectContains(io_instance.io(), "zigux/tests/phase15_build.zig", &.{
        "phase15_indefinite_c_policy.zig",
        "phase15-indefinite-c-policy-tests",
        "phase15_indefinite_c_blocker_evidence.zig",
        "phase15-indefinite-c-blocker-evidence-tests",
        "phase15_indefinite_c_lane_owner_alignment.zig",
        "phase15-indefinite-c-lane-owner-alignment-tests",
    });
}

test "phase 15 indefinite-C policy anchor set stays aligned with the authoritative freeze map" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const policy_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_indefinite_c_policy.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(policy_json);

    const freeze_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_freeze_map_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(freeze_manifest_json);

    const freeze_map_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(freeze_map_doc);

    const policy_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(policy_doc);

    const parsed_policy = try std.json.parseFromSlice(Manifest, std.testing.allocator, policy_json, .{});
    defer parsed_policy.deinit();

    const parsed_freeze_manifest = try std.json.parseFromSlice(FreezeMapManifest, std.testing.allocator, freeze_manifest_json, .{});
    defer parsed_freeze_manifest.deinit();

    try std.testing.expectEqual(parsed_freeze_manifest.value.freeze_in_c_targets.len, parsed_policy.value.anchors.len);

    for (parsed_freeze_manifest.value.freeze_in_c_targets, 0..) |freeze_target, i| {
        try std.testing.expectEqualStrings(freeze_target, parsed_policy.value.anchors[i]);
        try std.testing.expect(std.mem.indexOf(u8, freeze_map_doc, freeze_target) != null);
        try std.testing.expect(std.mem.indexOf(u8, policy_doc, freeze_target) != null);
    }

    for (parsed_freeze_manifest.value.study_only_targets) |study_only_target| {
        try std.testing.expect(std.mem.indexOf(u8, policy_doc, study_only_target) == null);

        for (parsed_policy.value.anchors) |policy_anchor| {
            try std.testing.expect(!std.mem.eql(u8, study_only_target, policy_anchor));
        }
    }
}

test "phase 15 indefinite-C policy gaps stay bounded and blocker-focused" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_indefinite_c_policy.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    var landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_note = false;
    var saw_manifest = false;
    var saw_test = false;
    var saw_build = false;
    var saw_sync_followup = false;
    var saw_exception_followup = false;
    var saw_provenance_followup = false;
    var saw_blocker = false;

    for (parsed.value.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_stay_in_c_evidence")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-policy-note")) {
            saw_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", gap.zigux_destination);
        } else if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-policy-manifest")) {
            saw_manifest = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_indefinite_c_policy.json", gap.zigux_destination);
        } else if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-policy-test")) {
            saw_test = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_indefinite_c_policy.zig", gap.zigux_destination);
        } else if (std.mem.eql(u8, gap.id, "phase15-build-gate-indefinite-c-policy")) {
            saw_build = true;
            try std.testing.expectEqualStrings("zigux/tests/phase15_build.zig", gap.zigux_destination);
        } else if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-field-sync-followup")) {
            saw_sync_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared scripts-root validator-first route") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reopen-trigger catalog") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "blocker-evidence replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "lane-owner-alignment replay") != null);
        } else if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-exception-posture-manifest-sync")) {
            saw_exception_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase15_indefinite_c_policy.json", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "no-silent-exception") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "retained closeout") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "retained-blocker") != null);
        } else if (std.mem.eql(u8, gap.id, "phase15-indefinite-c-readback-provenance-sync")) {
            saw_provenance_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase15-indefinite-c-policy.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "older exact-head provenance claim") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dated master-readback marker") != null);
        } else if (std.mem.eql(u8, gap.id, "phase15-deep-core-status-change-blocker")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "long-term C-owned posture") != null);
        }

        for (parsed.value.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 7), landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_manifest);
    try std.testing.expect(saw_test);
    try std.testing.expect(saw_build);
    try std.testing.expect(saw_sync_followup);
    try std.testing.expect(saw_exception_followup);
    try std.testing.expect(saw_provenance_followup);
    try std.testing.expect(saw_blocker);
}

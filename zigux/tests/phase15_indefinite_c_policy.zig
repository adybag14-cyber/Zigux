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

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    roadmap_requirement: []const u8,
    anchors: []const []const u8,
    supporting_artifacts: []const []const u8,
    indefinite_c_requirements: []const Requirement,
    gaps: []const Gap,
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
    try std.testing.expectEqualStrings("7b5519444e8f73f84c68dc3e63580fcaef06ffb6", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("policy for code that remains in C indefinitely", manifest.roadmap_requirement);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.supporting_artifacts.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.indefinite_c_requirements.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.gaps.len);

    try std.testing.expectEqualStrings("kernel/sched/core.c", manifest.anchors[0]);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-parity-scorecard.md", manifest.supporting_artifacts[3]);

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
            try std.testing.expectEqualStrings("narrower_followup_answers_blocker", requirement.required_terms[0]);
            try std.testing.expectEqualStrings("evidence_packet_stale_or_contradictory", requirement.required_terms[1]);
            try std.testing.expectEqualStrings("ownership_or_validation_changed", requirement.required_terms[2]);
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
        "survey provenance refreshed against verified `master` head `7b5519444e8f73f84c68dc3e63580fcaef06ffb6`",
        "## When the indefinite-C policy applies",
        "## Required recorded fields",
        "## Allowed work after an indefinite-C outcome",
        "## Exception posture",
        "## Reopen conditions",
        "## Reopen Trigger Catalog",
        "current status bucket",
        "requested decision bucket",
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
        "if the target stays in C, does the change record that ongoing policy honestly",
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
    });
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reopen-trigger catalog") != null);
        } else if (std.mem.eql(u8, gap.id, "phase15-deep-core-status-change-blocker")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "long-term C-owned posture") != null);
        }

        for (parsed.value.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 5), landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_manifest);
    try std.testing.expect(saw_test);
    try std.testing.expect(saw_build);
    try std.testing.expect(saw_sync_followup);
    try std.testing.expect(saw_blocker);
}
const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

const Handoff = struct {
    current_mode: []const u8,
    replay_commands: []const []const u8,
    blocker_posture_requirement: []const u8,
    next_step: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    roadmap_requirement: []const u8,
    anchor: []const u8,
    current_approval_state: []const u8,
    ownership_evidence_fields: []const []const u8,
    trigger_conditions: []const []const u8,
    required_review_packet_fields: []const []const u8,
    reopen_trigger_catalog: []const []const u8,
    decision_buckets: []const []const u8,
    handoff: Handoff,
};

test "phase 15 architecture council review-process doc and manifest stay aligned on the parked governance packet boundary" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(docs_readme);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);

    const survey_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(survey_doc);

    const script_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(script_readme);

    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(makefile);

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P15-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-06", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Architecture Council review process", manifest.roadmap_requirement);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-architecture-council-review-process.md", manifest.anchor);
    try std.testing.expectEqualStrings("no_freeze_map_status_change_approved", manifest.current_approval_state);
    try std.testing.expectEqualStrings("keep_in_c", manifest.decision_buckets[0]);
    try std.testing.expectEqualStrings("bounded_dual_implementation", manifest.decision_buckets[2]);
    try std.testing.expectEqualStrings("maintenance_mode", manifest.handoff.current_mode);
    try std.testing.expectEqual(@as(usize, 3), manifest.handoff.replay_commands.len);
    try std.testing.expectEqualStrings("make -C zigux phase15-validate", manifest.handoff.replay_commands[0]);
    try std.testing.expectEqualStrings("zig build test --build-file zigux/tests/phase15_build.zig", manifest.handoff.replay_commands[1]);
    try std.testing.expectEqualStrings("make -C zigux phase15", manifest.handoff.replay_commands[2]);
    try std.testing.expectEqualStrings("deep_core_blocker_posture_change", manifest.handoff.blocker_posture_requirement);
    try std.testing.expectEqualStrings("wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another Phase 15 slice", manifest.handoff.next_step);

    try expectContains(docs_readme, "Phase 15 notes");
    try expectContains(docs_readme, "`Documentation/zigux/phase15-architecture-council-review-process.md`");
    try expectContains(docs_readme, "`zigux/tests/phase15_build.zig`");
    try expectContains(docs_readme, "no Architecture Council approval is recorded yet");

    try expectContains(review_checklist, "if the change touches the shared Phase 15 governance packet");
    try expectContains(review_checklist, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(review_checklist, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(review_checklist, "zigux/tests/phase15_architecture_council_review_process_manifest.json");
    try expectContains(review_checklist, "zigux/tests/phase15_architecture_council_review_process.zig");

    try expectContains(survey_doc, "## Trigger Conditions");
    try expectContains(survey_doc, "## Required Review Packet");
    try expectContains(survey_doc, "## Decision Buckets");
    try expectContains(survey_doc, "## Reopen Trigger Catalog");
    try expectContains(survey_doc, "## Current Approval Posture");
    try expectContains(survey_doc, "## Maintenance-Mode Handoff");
    try expectContains(survey_doc, "`PHASE15_LANE_KEY=P15-L08`");
    try expectContains(survey_doc, "survey provenance refreshed against current `master` readback on 2026-05-06");
    try expectContains(survey_doc, "maintenance handoff: this review-process slice is parked in maintenance mode until one of the named reopen triggers fires or the deep-core blocker posture changes");
    try expectContains(survey_doc, "current review-process evidence is limited to named `phase`");
    try expectContains(survey_doc, "`validation gate summary`");
    try expectContains(survey_doc, "`indefinite-C policy link or non-applicability note`");
    try expectContains(survey_doc, "rollback-threshold");
    try expectContains(survey_doc, "retained-discussion-state");
    try expectContains(survey_doc, "reopen-trigger records");
    try expectContains(survey_doc, "current lane posture: `maintenance_mode`");
    try expectContains(survey_doc, "`make -C zigux phase15-validate`");
    try expectContains(survey_doc, "`zig build test --build-file zigux/tests/phase15_build.zig`");
    try expectContains(survey_doc, "`make -C zigux phase15`");
    try expectContains(survey_doc, "deep-core blocker posture changes enough to justify a new bounded review-process follow-up");
    try expectContains(survey_doc, "next future target: wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another Phase 15 slice");
    try expectContains(survey_doc, "landed `phase15-roadmap-minimum-field-sync`");
    try expectContains(survey_doc, "landed `phase15-lane-owner-alignment-replay-visible`");

    try expectContains(script_readme, "Phase 15 flow");
    try expectContains(script_readme, "check-phase15-review-process-handoff.py");
    try expectContains(script_readme, "phase15_build.zig");

    try expectContains(tests_readme, "keep the parked Phase 15 governance packet explicit in the tests root too");
    try expectContains(tests_readme, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(tests_readme, "zigux/tests/phase15_architecture_council_review_process.zig");
    try expectContains(tests_readme, "zigux/tests/phase15_build.zig");

    try expectContains(makefile, "PHONY += phase15-validate phase15-test phase15");
    try expectContains(makefile, "phase15-validate:");
    try expectContains(makefile, "scripts/zigux/check-phase15-review-process-handoff.py --self-test");
    try expectContains(makefile, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(makefile, "phase15-test:");
    try expectContains(makefile, "zigux/tests/phase15_build.zig");

    try expectContains(manifest_json, "\"lane_key\": \"P15-L08\"");
    try expectContains(manifest_json, "\"surveyed_commit\": \"current-master-readback-2026-05-06\"");
    try expectContains(manifest_json, "\"handoff\"");
    try expectContains(manifest_json, "\"current_mode\": \"maintenance_mode\"");
    try expectContains(manifest_json, "make -C zigux phase15-validate");
    try expectContains(manifest_json, "zig build test --build-file zigux/tests/phase15_build.zig");
    try expectContains(manifest_json, "make -C zigux phase15");
    try expectContains(manifest_json, "deep_core_blocker_posture_change");
    try expectContains(manifest_json, "phase15-roadmap-minimum-field-sync");
    try expectContains(manifest_json, "phase15-lane-owner-alignment-replay-visible");
}

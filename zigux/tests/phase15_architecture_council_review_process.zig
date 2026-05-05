const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

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

    const manifest_doc = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_doc);

    try expectContains(docs_readme, "Phase 15 notes");
    try expectContains(docs_readme, "`Documentation/zigux/freeze-map.md`");
    try expectContains(docs_readme, "`Documentation/zigux/phase15-freeze-map-governance.md`");
    try expectContains(docs_readme, "`Documentation/zigux/phase15-architecture-council-review-process.md`");
    try expectContains(docs_readme, "`Documentation/zigux/phase15-parity-scorecard.md`");
    try expectContains(docs_readme, "`Documentation/zigux/phase15-indefinite-c-policy.md`");
    try expectContains(docs_readme, "`scripts/zigux/check-phase15-scripts-readme-alignment.py`");
    try expectContains(docs_readme, "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`");
    try expectContains(docs_readme, "`zigux/tests/phase15_build.zig`");
    try expectContains(docs_readme, "`make -C zigux phase15`");
    try expectContains(docs_readme, "no Architecture Council approval is recorded yet");

    try expectContains(
        review_checklist,
        "if the change touches the shared Phase 15 governance packet",
    );
    try expectContains(review_checklist, "Documentation/zigux/freeze-map.md");
    try expectContains(
        review_checklist,
        "Documentation/zigux/phase15-freeze-map-governance.md",
    );
    try expectContains(
        review_checklist,
        "Documentation/zigux/phase15-architecture-council-review-process.md",
    );
    try expectContains(review_checklist, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectContains(review_checklist, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(review_checklist, "Documentation/zigux/review-checklist.md");
    try expectContains(review_checklist, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(
        review_checklist,
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    );
    try expectContains(review_checklist, "zigux/tests/phase15_freeze_map_governance.zig");
    try expectContains(review_checklist, "zigux/tests/phase15_parity_scorecard.zig");
    try expectContains(
        review_checklist,
        "zigux/tests/phase15_architecture_council_review_process.zig",
    );
    try expectContains(review_checklist, "zigux/tests/phase15_indefinite_c_policy.json");
    try expectContains(review_checklist, "zigux/tests/phase15_indefinite_c_policy.zig");
    try expectContains(review_checklist, "zigux/tests/phase15_build.zig");
    try expectContains(review_checklist, "make -C zigux phase15");

    try expectContains(survey_doc, "## Trigger Conditions");
    try expectContains(survey_doc, "## Required Review Packet");
    try expectContains(survey_doc, "## Decision Buckets");
    try expectContains(survey_doc, "## Reopen Trigger Catalog");
    try expectContains(survey_doc, "## Current Approval Posture");
    try expectContains(
        survey_doc,
        "product boundary:\n  - `Documentation/zigux/freeze-map.md`",
    );
    try expectContains(survey_doc, "`Documentation/zigux/phase15-freeze-map-governance.md`");
    try expectContains(survey_doc, "`Documentation/zigux/phase15-architecture-council-review-process.md`");
    try expectContains(survey_doc, "`Documentation/zigux/phase15-parity-scorecard.md`");
    try expectContains(survey_doc, "`Documentation/zigux/phase15-indefinite-c-policy.md`");
    try expectContains(survey_doc, "`Documentation/zigux/review-checklist.md`");
    try expectContains(survey_doc, "`scripts/zigux/check-phase15-review-process-handoff.py`");
    try expectContains(survey_doc, "`zigux/tests/phase15_architecture_council_review_process_manifest.json`");
    try expectContains(survey_doc, "`zigux/tests/phase15_architecture_council_review_process.zig`");
    try expectContains(survey_doc, "`zigux/tests/phase15_build.zig`");
    try expectContains(survey_doc, "`make -C zigux phase15-validate`");
    try expectContains(
        survey_doc,
        "no Architecture Council approval is currently recorded for a freeze-map status change",
    );
    try expectContains(survey_doc, "`retired_from_active_discussion`");
    try expectContains(survey_doc, "current review-process evidence is limited to named `phase`");
    try expectContains(survey_doc, "`current status bucket`");
    try expectContains(survey_doc, "`validation gate summary`");
    try expectContains(survey_doc, "landed `phase15-roadmap-minimum-field-sync`");

    try expectContains(script_readme, "Phase 15 flow");
    try expectContains(
        script_readme,
        "phase15-architecture-council-review-process.md",
    );
    try expectContains(
        script_readme,
        "check-phase15-review-process-handoff.py",
    );
    try expectContains(
        script_readme,
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    );
    try expectContains(
        script_readme,
        "zigux/tests/phase15_architecture_council_review_process.zig",
    );
    try expectContains(script_readme, "phase15_build.zig");
    try expectContains(script_readme, "make -C zigux phase15");

    try expectContains(
        tests_readme,
        "keep the parked Phase 15 governance packet explicit in the tests root too",
    );
    try expectContains(tests_readme, "Documentation/zigux/freeze-map.md");
    try expectContains(
        tests_readme,
        "Documentation/zigux/phase15-freeze-map-governance.md",
    );
    try expectContains(
        tests_readme,
        "Documentation/zigux/phase15-architecture-council-review-process.md",
    );
    try expectContains(tests_readme, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectContains(tests_readme, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(tests_readme, "Documentation/zigux/review-checklist.md");
    try expectContains(tests_readme, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(tests_readme, "zigux/tests/phase15_build.zig");
    try expectContains(tests_readme, "zigux/tests/phase15_freeze_map_governance.zig");
    try expectContains(tests_readme, "zigux/tests/phase15_parity_scorecard.zig");
    try expectContains(
        tests_readme,
        "zigux/tests/phase15_architecture_council_review_process.zig",
    );
    try expectContains(tests_readme, "zigux/tests/phase15_indefinite_c_policy.json");
    try expectContains(tests_readme, "zigux/tests/phase15_indefinite_c_policy.zig");
    try expectContains(tests_readme, "zigux/Makefile");
    try expectContains(
        tests_readme,
        "zig build test --build-file zigux/tests/phase15_build.zig",
    );
    try expectContains(tests_readme, "make -C zigux phase15");

    try expectContains(makefile, "PHONY += phase15-validate phase15-test phase15");
    try expectContains(makefile, "phase15-validate:");
    try expectContains(
        makefile,
        "scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
    );
    try expectContains(makefile, "scripts/zigux/check-phase15-scripts-readme-alignment.py");
    try expectContains(
        makefile,
        "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    );
    try expectContains(makefile, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(makefile, "phase15-test:");
    try expectContains(makefile, "zigux/tests/phase15_build.zig");

    try expectContains(manifest_doc, "\"ownership_evidence_fields\"");
    try expectContains(manifest_doc, "\"phase\"");
    try expectContains(manifest_doc, "\"current status bucket\"");
    try expectContains(manifest_doc, "\"validation gate summary\"");
    try expectContains(manifest_doc, "\"current_repo_handoff\"");
    try expectContains(manifest_doc, "Documentation/zigux/freeze-map.md");
    try expectContains(
        manifest_doc,
        "Documentation/zigux/phase15-freeze-map-governance.md",
    );
    try expectContains(
        manifest_doc,
        "Documentation/zigux/phase15-architecture-council-review-process.md",
    );
    try expectContains(manifest_doc, "Documentation/zigux/phase15-parity-scorecard.md");
    try expectContains(manifest_doc, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(manifest_doc, "Documentation/zigux/review-checklist.md");
    try expectContains(manifest_doc, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(
        manifest_doc,
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    );
    try expectContains(
        manifest_doc,
        "zigux/tests/phase15_architecture_council_review_process.zig",
    );
    try expectContains(manifest_doc, "zigux/tests/phase15_indefinite_c_policy.json");
    try expectContains(manifest_doc, "zigux/tests/phase15_build.zig");
    try expectContains(manifest_doc, "\"current_bounded_lane\"");
    try expectContains(manifest_doc, "scripts-root validator path");
    try expectContains(manifest_doc, "make -C zigux phase15-validate");
    try expectContains(manifest_doc, "tests-root guidance path");
    try expectContains(manifest_doc, "dedicated handoff-checker route");
    try expectContains(manifest_doc, "phase15-roadmap-minimum-field-sync");
}

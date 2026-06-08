const std = @import("std");
const contract_inputs = @import("contract_inputs");

const docs_readme = contract_inputs.docs_readme;
const review_checklist = contract_inputs.review_checklist;
const freeze_map = contract_inputs.freeze_map;
const phase14_manifest = contract_inputs.phase14_manifest;
const phase14_validator = contract_inputs.phase14_validator;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "docs root keeps current phase14 reminder tied to returned freeze companions" {
    try expectContains(docs_readme, "Phase 14 notes");
    try expectContains(docs_readme, "Documentation/zigux/phase14-end-to-end-smoke-survey.md");
    try expectContains(docs_readme, "Documentation/zigux/phase14-core-boundary-traceability.md");
    try expectContains(docs_readme, "Documentation/zigux/phase14-release-boundary-survey.md");
    try expectContains(docs_readme, "Documentation/zigux/phase14-productization-gap-survey.md");
    try expectContains(docs_readme, "Documentation/zigux/phase14-shared-smoke-current-master-gap.md");
    try expectContains(docs_readme, "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md");
    try expectContains(docs_readme, "Documentation/zigux/freeze-map.md");
    try expectContains(docs_readme, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(docs_readme, "scripts/zigux/validate-phase14.py");
    try expectContains(docs_readme, "zigux/tests/phase14_end_to_end_smoke_manifest.json");
    try expectContains(docs_readme, "make -C zigux phase14-validate");
    try expectOrdered(
        docs_readme,
        "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
        "Documentation/zigux/freeze-map.md",
    );
}

test "review checklist and freeze map preserve current phase14 anchor status split" {
    try expectContains(review_checklist, "if the change touches the shared Phase 14 smoke packet");
    try expectContains(review_checklist, "Documentation/zigux/phase14-end-to-end-smoke-survey.md");
    try expectContains(review_checklist, "scripts/zigux/validate-phase14.py");
    try expectContains(review_checklist, "scripts/zigux/check-phase14-release-boundary-exact-counts.py");
    try expectContains(review_checklist, "kernel/workqueue_bridge.zig");
    try expectContains(review_checklist, "zigux/tests/phase14_workqueue_bridge.zig");
    try expectContains(review_checklist, "zigux/tests/phase14_workqueue_reviewability.zig");
    try expectContains(review_checklist, "zigux/tests/phase14_ring_buffer_survey.zig");
    try expectContains(review_checklist, "zigux/tests/phase14_end_to_end_smoke_manifest.json");
    try expectContains(review_checklist, "exact-readback gaps");

    try expectContains(freeze_map, "## Freeze In C Initially");
    try expectContains(freeze_map, "## Study / Boundary Only");
    try expectOrdered(freeze_map, "kernel/rcu/tree.c", "kernel/workqueue.c");
    try expectContains(freeze_map, "kernel/workqueue.c");
    try expectContains(freeze_map, "kernel/trace/ring_buffer.c");
    try expectContains(freeze_map, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(freeze_map, "study-only anchor maintenance");
}

test "phase14 validator and manifest keep docs-root freeze packet executable" {
    try expectContains(phase14_validator, "scripts/zigux/validate-phase14.py");
    try expectContains(phase14_validator, "Documentation/zigux/README.md");
    try expectContains(phase14_validator, "Documentation/zigux/review-checklist.md");
    try expectContains(phase14_validator, "Documentation/zigux/freeze-map.md");
    try expectContains(phase14_validator, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(phase14_validator, "zigux/tests/phase14_end_to_end_smoke_manifest.json");
    try expectContains(phase14_validator, "scripts/zigux/check-phase14-release-boundary-exact-counts.py");
    try expectContains(phase14_validator, "PHASE14_VALIDATION=pass");

    try expectContains(phase14_manifest, "\"shared_smoke_surfaces\": [");
    try expectContains(phase14_manifest, "\"Documentation/zigux/README.md\"");
    try expectContains(phase14_manifest, "\"Documentation/zigux/review-checklist.md\"");
    try expectContains(phase14_manifest, "\"Documentation/zigux/freeze-map.md\"");
    try expectContains(phase14_manifest, "\"Documentation/zigux/phase15-study-only-anchor-accounting.md\"");
    try expectContains(phase14_manifest, "\"zigux/tests/phase14_workqueue_reviewability.zig\"");
    try expectContains(phase14_manifest, "\"zigux/tests/phase14_ring_buffer_survey.zig\"");
    try expectContains(phase14_manifest, "\"smoke_commands\": [");
    try expectContains(phase14_manifest, "\"make -C zigux phase14-validate\"");
    try expectContains(phase14_manifest, "\"phase14_make_smoke_target_present\": false");
}

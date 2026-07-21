const std = @import("std");
const options = @import("phase15_route_gap_boundary_options");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "Phase 15 route boundary options capture shipped wrappers and CI" {
    try expectContains(options.makefile, "phase15-validate:");
    try expectContains(options.makefile, "phase15-test:");
    try expectContains(options.makefile, "phase15: phase15-validate phase15-test");
    try expectContains(options.workflow, "Validate current Phase 15 governance packet");
    try expectContains(options.workflow, "Run current Phase 15 governance tests");
    try expectContains(options.workflow, "Run current Phase 15 aggregate route");
}

test "Phase 15 route boundary options retain no-approval governance" {
    try expectContains(options.docs_root, "PHASE15_ROUTE_RECOVERY_STATUS=landed");
    try expectContains(options.review_checklist, "No Architecture Council approval is recorded by route recovery");
    try expectContains(options.scripts_root, "Documentation/zigux/phase15-route-recovery.md");
    try expectContains(options.readiness_survey, "historical survey findings superseded by this current-state block");
    try expectContains(options.validator, "PHASE15_ROUTE_RECOVERY_NO_APPROVAL_CLAIM=true");
}

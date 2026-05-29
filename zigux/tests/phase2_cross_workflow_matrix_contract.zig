const std = @import("std");
const testing = std.testing;
const options = @import("phase2_cross_workflow_matrix_options");

const workflow = options.workflow;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 cross workflow keeps the bootstrap checker and make route paired" {
    try expectContains(workflow, "name: Self-test current Phase 2 cross checker");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross.py --self-test");
    try expectContains(workflow, "name: Check current Phase 2 direct cross-route packet");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross.py");
    try expectContains(workflow, "name: Self-test current Phase 2 cross selftest alignment checker");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test");
    try expectContains(workflow, "name: Check current Phase 2 cross alignment packet");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try expectContains(workflow, "name: Run current Phase 2 cross make route");
    try expectContains(workflow, "run: make -C zigux phase2-cross");
}

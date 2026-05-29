const std = @import("std");

const max_file_size = 256 * 1024;

fn loadFile(io: std.Io, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectNoLineStartsWith(haystack: []const u8, prefix: []const u8) !void {
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        try std.testing.expect(!std.mem.startsWith(u8, line, prefix));
    }
}

test "phase 15 validator records present packet evidence and blocked wrapper routes" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const validator = try loadFile(io_instance.io(), "scripts/zigux/validate-phase15.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "EXPECTED_DIRECT_PACKET_PATHS");
    try expectContains(validator, "Documentation/zigux/freeze-map.md");
    try expectContains(validator, "Documentation/zigux/review-checklist.md");
    try expectContains(validator, "scripts/zigux/check-phase15-docs-readme-alignment.py");
    try expectContains(validator, "scripts/zigux/check-phase15-architecture-council-packet.py");
    try expectContains(validator, "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py");
    try expectContains(validator, "zigux/tests/phase15_build.zig");
    try expectContains(validator, "zigux/tests/phase15_readiness_gap_matrix.json");

    try expectContains(validator, "EXPECTED_BLOCKED_BROADER_ROUTES");
    try expectContains(validator, "\"missing_make_targets\": [\"phase15-validate\", \"phase15-test\", \"phase15\"]");
    try expectContains(validator, "\"missing_workflow_phase15_route\": True");
    try expectContains(validator, "\"phase15_validate_target_present\": False");
    try expectContains(validator, "\"phase15_test_target_present\": False");
    try expectContains(validator, "\"phase15_aggregate_target_present\": False");
    try expectContains(validator, "\"shared_ci_phase15_present\": False");
}

test "docs root checklist and freeze map keep the validator first boundary explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const docs_root = try loadFile(io_instance.io(), "Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs_root);
    const review_checklist = try loadFile(io_instance.io(), "Documentation/zigux/review-checklist.md");
    defer std.testing.allocator.free(review_checklist);
    const freeze_map = try loadFile(io_instance.io(), "Documentation/zigux/freeze-map.md");
    defer std.testing.allocator.free(freeze_map);

    try expectContains(docs_root, "Phase 15 notes");
    try expectContains(docs_root, "scripts/zigux/validate-phase15.py");
    try expectContains(docs_root, "zigux/tests/phase15_build.zig");
    try expectContains(docs_root, "make -C zigux phase15-validate");
    try expectContains(docs_root, "make -C zigux phase15-test");
    try expectContains(docs_root, "make -C zigux phase15");
    try expectContains(docs_root, "without widening into deep-core delivery or approval claims");

    try expectContains(review_checklist, "without an Architecture Council decision");
    try expectContains(review_checklist, "freeze-map anchor is entering Architecture Council status review");
    try expectContains(review_checklist, "shared reminder surface summarizes the study-only freeze-map anchors");
    try expectContains(review_checklist, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectContains(review_checklist, "kernel/workqueue.c");
    try expectContains(review_checklist, "kernel/trace/ring_buffer.c");

    try expectContains(freeze_map, "shared Phase 15 handoff and gap notes");
    try expectContains(freeze_map, "directly materialized validator");
    try expectContains(freeze_map, "still-missing dedicated `phase15*` wrapper routes");
    try expectContains(freeze_map, "shared-CI companions as repo-reality gaps");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
}

test "repository routes have not silently promoted the phase 15 wrapper boundary" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const makefile = try loadFile(io_instance.io(), "zigux/Makefile");
    defer std.testing.allocator.free(makefile);
    const workflow = try loadFile(io_instance.io(), ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);
    const phase15_build = try loadFile(io_instance.io(), "zigux/tests/phase15_build.zig");
    defer std.testing.allocator.free(phase15_build);

    try expectNoLineStartsWith(makefile, "phase15-validate:");
    try expectNoLineStartsWith(makefile, "phase15-test:");
    try expectNoLineStartsWith(makefile, "phase15:");
    try expectNotContains(makefile, "PHONY += phase15-validate phase15-test phase15");

    try expectNotContains(workflow, "make -C zigux phase15-validate");
    try expectNotContains(workflow, "make -C zigux phase15-test");
    try expectNotContains(workflow, "Validate Phase 15 governance packet");
    try expectNotContains(workflow, "Run Phase 15 governance tests");

    try expectContains(phase15_build, "phase15-freeze-map-governance");
    try expectContains(phase15_build, "phase15-architecture-council-review-process");
    try expectContains(phase15_build, "phase15-readiness-gate");
    try expectNotContains(phase15_build, "phase15-validator-first-route-contract");
}

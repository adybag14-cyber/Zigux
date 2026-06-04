const std = @import("std");

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase 15 docs root keeps validator and build companion present" {
    const allocator = std.testing.allocator;

    const docs_root = try readFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);

    const shared_gap = try readFile(allocator, "Documentation/zigux/phase15-shared-summary-gap.md");
    defer allocator.free(shared_gap);

    const handoff = try readFile(allocator, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    defer allocator.free(handoff);

    const scripts_root = try readFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_root);

    const tests_root = try readFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_root);

    const build_file = try readFile(allocator, "zigux/tests/phase15_build.zig");
    defer allocator.free(build_file);

    try expectContains(docs_root, "scripts/zigux/validate-phase15.py");
    try expectContains(docs_root, "zigux/tests/phase15_build.zig");
    try expectContains(shared_gap, "dedicated validator maintenance gate");
    try expectContains(shared_gap, "dedicated shared build companion");
    try expectContains(handoff, "scripts/zigux/validate-phase15.py");
    try expectContains(handoff, "zigux/tests/phase15_build.zig");
    try expectContains(scripts_root, "directly readable `scripts/zigux/validate-phase15.py` maintenance gate");
    try expectContains(scripts_root, "directly readable `zigux/tests/phase15_build.zig` shared build companion");
    try expectContains(tests_root, "zigux/tests/phase15_architecture_council_review_process_build.zig");
    try expectContains(build_file, "phase15-freeze-map-governance");
    try expectContains(build_file, "phase15-architecture-council-review-process");
    try expectContains(build_file, "phase15-handoff-next-steps");
}

test "phase 15 reminder surfaces keep dedicated wrapper routes gap tracked" {
    const allocator = std.testing.allocator;

    const docs_root = try readFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);

    const freeze_map = try readFile(allocator, "Documentation/zigux/freeze-map.md");
    defer allocator.free(freeze_map);

    const shared_gap = try readFile(allocator, "Documentation/zigux/phase15-shared-summary-gap.md");
    defer allocator.free(shared_gap);

    const handoff = try readFile(allocator, "Documentation/zigux/phase15-handoff-next-steps-survey.md");
    defer allocator.free(handoff);

    const scripts_root = try readFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_root);

    try expectContains(docs_root, "make -C zigux phase15-validate");
    try expectContains(docs_root, "remain blocked route vocabulary rather than shipped replay paths");
    try expectContains(freeze_map, "still-missing dedicated `phase15*` wrapper routes, shared-CI companions");
    try expectContains(shared_gap, "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized");
    try expectContains(shared_gap, "no dedicated Phase 15 validate, test, or aggregate route name");
    try expectContains(handoff, "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body");
    try expectContains(handoff, "no dedicated shared-CI Phase 15 validate, test, or aggregate route");
    try expectContains(scripts_root, "broader dedicated `phase15*` wrapper and shared-CI route names stay repo-reality gaps");
}

test "makefile and bootstrap workflow do not silently ship phase 15 wrappers" {
    const allocator = std.testing.allocator;

    const makefile = try readFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    const workflow = try readFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try expectNotContains(makefile, "\nphase15-validate:");
    try expectNotContains(makefile, "\nphase15-test:");
    try expectNotContains(makefile, "\nphase15:");
    try expectNotContains(workflow, "phase15-validate");
    try expectNotContains(workflow, "phase15-test");
    try expectNotContains(workflow, "phase15 aggregate");
}

const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    const io = std.testing.io;
    return std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(128 * 1024),
    );
}

fn expectExistingPath(path: []const u8) !void {
    const contents = try readRepoFile(path);
    defer std.testing.allocator.free(contents);
}

fn expectMissingPath(path: []const u8) !void {
    try std.testing.expectError(error.FileNotFound, readRepoFile(path));
}

test "phase 8 exec-cmd review witness keeps the surviving shared reminder surfaces explicit" {
    try expectExistingPath(".github/workflows/zigux-bootstrap.yml");
    try expectExistingPath("Documentation/zigux/README.md");
    try expectExistingPath("Documentation/zigux/review-checklist.md");
    try expectExistingPath("scripts/zigux/README.md");
    try expectExistingPath("scripts/zigux/validate-phase8.py");
    try expectExistingPath("zigux/Makefile");
    try expectExistingPath("zigux/tests/README.md");

    const docs_root = try readRepoFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs_root);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "Phase 8 notes") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "tools/lib/subcmd/exec-cmd.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "scripts/zigux/validate-phase8.py") != null);

    const checklist = try readRepoFile("Documentation/zigux/review-checklist.md");
    defer std.testing.allocator.free(checklist);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "if the change touches the parked Phase 8 `exec-cmd` packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "`make -C zigux phase8-validate`") != null);

    const scripts_root = try readRepoFile("scripts/zigux/README.md");
    defer std.testing.allocator.free(scripts_root);
    try std.testing.expect(std.mem.indexOf(u8, scripts_root, "## Phase 8") != null);
    try std.testing.expect(std.mem.indexOf(u8, scripts_root, "scripts/zigux/validate-phase8.py") != null);

    const tests_root = try readRepoFile("zigux/tests/README.md");
    defer std.testing.allocator.free(tests_root);
    try std.testing.expect(std.mem.indexOf(u8, tests_root, "`zigux/tests/phase8_exec_cmd.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_root, "make -C zigux phase8-validate") != null);

    const makefile = try readRepoFile("zigux/Makefile");
    defer std.testing.allocator.free(makefile);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase8-validate:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase8-test:") != null);

    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Validate Phase 8 tooling routes") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 8 tooling tests") != null);
}

test "phase 8 exec-cmd review witness records current missing packet members" {
    try expectExistingPath("zigux/tests/phase8_exec_cmd.zig");

    // Current `master` still carries the shared reminder file, but these older
    // exec-cmd packet members are absent and should not be treated as live proof.
    try expectMissingPath("tools/lib/subcmd/exec-cmd.zig");
    try expectMissingPath("Documentation/zigux/phase8-exec-cmd-slice.md");
    try expectMissingPath("Documentation/zigux/phase8-tooling-lane-sequencing.md");
    try expectMissingPath("scripts/zigux/check-phase8-exec-cmd-packet.py");
    try expectMissingPath("zigux/tests/phase8_exec_cmd_only_build.zig");
}

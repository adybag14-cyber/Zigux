const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";

const kconfig_next_step_markers = [_][]const u8{
    "If the kconfig bridge lane resumes substantive implementation instead of closure upkeep",
    "preserves the live split between request-plan overrides",
    "the non-empty sentinel packet",
    "helper-local explicit-override coverage",
    "add a direct `conf.c` / `confdata.c` provenance anchor once those C sources are readable in-tree again on current `master`",
};

const genksyms_next_step_markers = [_][]const u8{
    "If the `genksyms` lane resumes substantive implementation instead of closure upkeep",
    "start with one smallest same-family step around the still-missing CRC-side evidence recorded in the survey",
    "rather than widening this shared note again",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(96 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 closure next step keeps the parked closure boundary" {
    const closure_note = try readRepoFile(std.testing.allocator, closure_note_path);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Next Step");
    try expectContains(closure_note, "PHASE2_STATUS=parked");
    try expectContains(closure_note, "Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.");
    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");
}

test "phase2 closure next step preserves the kconfig restart boundary" {
    const closure_note = try readRepoFile(std.testing.allocator, closure_note_path);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
    try expectContains(closure_note, "scripts/kconfig/conf.c");
    try expectContains(closure_note, "scripts/kconfig/confdata.c");

    for (kconfig_next_step_markers) |marker| {
        try expectContains(closure_note, marker);
    }
}

test "phase2 closure next step keeps genksyms CRC evidence as the next implementation front" {
    const closure_note = try readRepoFile(std.testing.allocator, closure_note_path);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    try expectContains(closure_note, "scripts/zigux/check-phase2-genksyms-selftest-alignment.py");
    try expectContains(closure_note, "zig test scripts/zigux/genksyms.zig");

    for (genksyms_next_step_markers) |marker| {
        try expectContains(closure_note, marker);
    }
}

const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";

const required_gap_markers = [_][]const u8{
    "## Repo-Reality Gaps",
    "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md",
    "current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`",
    "fixture-backed rather than same-tree differential",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
};

const required_split_markers = [_][]const u8{
    "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`",
    "allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`",
    "helper-local explicit-override roster remains broader by design",
};

const required_next_step_markers = [_][]const u8{
    "Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.",
    "If the kconfig bridge lane resumes substantive implementation instead of closure upkeep",
    "preserves the live split between request-plan overrides, the non-empty sentinel packet, and helper-local explicit-override coverage",
    "add a direct `conf.c` / `confdata.c` provenance anchor once those C sources are readable in-tree again on current `master`",
};

fn readClosureNote(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        closure_note_path,
        allocator,
        .limited(24 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 closure keeps kconfig repo-reality gap explicit" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    for (required_gap_markers) |needle| {
        try expectContains(closure_note, needle);
    }
}

test "phase2 closure preserves the kconfig allconfig split" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    for (required_split_markers) |needle| {
        try expectContains(closure_note, needle);
    }
}

test "phase2 closure next step stays bridge-local before provenance expands" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    for (required_next_step_markers) |needle| {
        try expectContains(closure_note, needle);
    }
}

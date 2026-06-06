const std = @import("std");

const Marker = struct {
    text: []const u8,
};

const FileExpectation = struct {
    path: []const u8,
    markers: []const Marker,
};

const expectations = [_]FileExpectation{
    .{
        .path = "Documentation/zigux/README.md",
        .markers = &.{
            .{ .text = "Phase 13 notes" },
            .{ .text = "`Documentation/zigux/phase13-contributor-workflow-guide.md`" },
            .{ .text = "`Documentation/zigux/phase13-release-coordination-matrix.md`" },
            .{ .text = "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`" },
            .{ .text = "`scripts/zigux/check-phase13-shared-summary-surfaces.py`" },
            .{ .text = "`scripts/zigux/check-phase13-tests-readme-alignment.py`" },
            .{ .text = "`scripts/zigux/validate-phase13-release.py`" },
            .{ .text = "make -C zigux phase13-validate" },
            .{ .text = "repo-reality gaps" },
        },
    },
    .{
        .path = "Documentation/zigux/review-checklist.md",
        .markers = &.{
            .{ .text = "if the change touches the shared Phase 13 shared-helper packet" },
            .{ .text = "`Documentation/zigux/phase13-contributor-workflow-guide.md`" },
            .{ .text = "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`" },
            .{ .text = "`Documentation/zigux/phase13-release-coordination-matrix.md`" },
            .{ .text = "`scripts/zigux/check-phase13-shared-summary-surfaces.py`" },
            .{ .text = "stable contributor-facing handle" },
            .{ .text = "adjacent notifier evidence" },
            .{ .text = "repo-reality gaps" },
        },
    },
    .{
        .path = "Documentation/zigux/phase13-contributor-workflow-guide.md",
        .markers = &.{
            .{ .text = "Stable Contributor-Facing Handle" },
            .{ .text = "`Documentation/zigux/phase13-contributor-workflow-guide.md`" },
            .{ .text = "`scripts/zigux/README.md`" },
            .{ .text = "`zigux/tests/README.md`" },
            .{ .text = "Docs-root companion rule" },
            .{ .text = "Shared contributor edit loop" },
            .{ .text = "rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`" },
            .{ .text = "keep any absent route, replay, or helper recorded as a repo-reality gap" },
        },
    },
    .{
        .path = "Documentation/zigux/phase13-release-coordination-matrix.md",
        .markers = &.{
            .{ .text = "`PHASE13_STATUS=active`" },
            .{ .text = "release-discipline validator: `python3 scripts/zigux/validate-phase13-release.py`" },
            .{ .text = "`fs/libfs.c`" },
            .{ .text = "`lib/devres.c`" },
            .{ .text = "`security/landlock/ruleset.c`" },
            .{ .text = "`security/landlock/syscalls.c`" },
            .{ .text = "adjacent notifier support" },
            .{ .text = "`make -C zigux phase13-validate`" },
            .{ .text = "`make -C zigux phase13`" },
        },
    },
    .{
        .path = "Documentation/zigux/phase13-shared-helper-lane-sequencing.md",
        .markers = &.{
            .{ .text = "Phase 13 Shared Helper Lane Sequencing" },
            .{ .text = "`libfs` still owns the roadmap-backed `fs/libfs.c` anchor" },
            .{ .text = "`devres` owns the currently readable DMA-boundary" },
            .{ .text = "`landlock/ruleset` keeps the shipped helper-local ownership note" },
            .{ .text = "`landlock/syscalls` owns the narrower syscall governance" },
            .{ .text = "adjacent notifier evidence owns only release-surface truthfulness" },
            .{ .text = "do not treat `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13` as shipped evidence" },
        },
    },
    .{
        .path = "scripts/zigux/README.md",
        .markers = &.{
            .{ .text = "## Phase 13" },
            .{ .text = "stable contributor-facing handle" },
            .{ .text = "`scripts/zigux/check-phase13-shared-summary-surfaces.py`" },
            .{ .text = "`scripts/zigux/check-phase13-tests-readme-alignment.py`" },
            .{ .text = "`scripts/zigux/validate-phase13-release.py`" },
            .{ .text = "without promoting the still-missing Phase 13 Makefile routes into the entrypoint" },
            .{ .text = "without promoting it into a fifth helper family" },
        },
    },
    .{
        .path = "zigux/tests/README.md",
        .markers = &.{
            .{ .text = "Keep the stable contributor-facing reminder handle explicit" },
            .{ .text = "`Documentation/zigux/phase13-contributor-workflow-guide.md`" },
            .{ .text = "`scripts/zigux/README.md`" },
            .{ .text = "`zigux/tests/README.md`" },
            .{ .text = "`scripts/zigux/check-phase13-shared-summary-surfaces.py`" },
            .{ .text = "make -C zigux phase13-validate" },
            .{ .text = "repo-reality-gap vocabulary" },
        },
    },
    .{
        .path = "scripts/zigux/check-phase13-shared-summary-surfaces.py",
        .markers = &.{
            .{ .text = "Guard the shipped Phase 13 shared-summary contributor surfaces." },
            .{ .text = "Documentation/zigux/phase13-contributor-workflow-guide.md" },
            .{ .text = "Documentation/zigux/phase13-release-coordination-matrix.md" },
            .{ .text = "Documentation/zigux/review-checklist.md" },
            .{ .text = "scripts/zigux/README.md" },
            .{ .text = "zigux/tests/README.md" },
            .{ .text = "PHASE13_SHARED_SUMMARY_SURFACES=pass" },
        },
    },
    .{
        .path = "scripts/zigux/validate-phase13-release.py",
        .markers = &.{
            .{ .text = "Validate the current Phase 13 release-planning reminder packet" },
            .{ .text = "Documentation/zigux/phase13-contributor-workflow-guide.md" },
            .{ .text = "Documentation/zigux/phase13-release-packet-index.md" },
            .{ .text = "Documentation/zigux/phase13-release-coordination-matrix.md" },
            .{ .text = "scripts/zigux/check-phase13-roadmap-traceability.py" },
            .{ .text = "PHASE13_RELEASE_VALIDATOR=pass" },
            .{ .text = "FORBIDDEN_MARKERS" },
        },
    },
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(2 * 1024 * 1024));
}

fn expectMarkers(haystack: []const u8, file: FileExpectation) !void {
    for (file.markers) |marker| {
        if (std.mem.indexOf(u8, haystack, marker.text) == null) {
            std.debug.print("missing marker in {s}: {s}\n", .{ file.path, marker.text });
            return error.MissingMarker;
        }
    }
}

test "lane02 phase13 docs root packet keeps shared handle and route gaps explicit" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    for (expectations) |file| {
        const content = try readRepoFile(allocator, file.path);
        try expectMarkers(content, file);
    }
}

test "lane02 phase13 docs root routes through the contributor-facing trio" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    const contributor_guide = try readRepoFile(allocator, "Documentation/zigux/phase13-contributor-workflow-guide.md");
    const scripts_readme = try readRepoFile(allocator, "scripts/zigux/README.md");
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");

    const handle = [_][]const u8{
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`scripts/zigux/README.md`",
        "`zigux/tests/README.md`",
    };
    for (handle) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, docs_root, marker) != null);
        try std.testing.expect(std.mem.indexOf(u8, contributor_guide, marker) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, scripts_readme, "stable contributor-facing handle") != null);
    try std.testing.expect(std.mem.indexOf(u8, tests_readme, "stable contributor-facing reminder handle") != null);
}

test "lane02 phase13 docs root preserves helper families and adjacent notifier boundary" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const docs_root = try readRepoFile(allocator, "Documentation/zigux/README.md");
    const matrix = try readRepoFile(allocator, "Documentation/zigux/phase13-release-coordination-matrix.md");
    const sequencing = try readRepoFile(allocator, "Documentation/zigux/phase13-shared-helper-lane-sequencing.md");

    const anchors = [_][]const u8{
        "`fs/libfs.c`",
        "`lib/devres.c`",
        "`security/landlock/ruleset.c`",
        "`security/landlock/syscalls.c`",
    };
    for (anchors) |anchor| {
        try std.testing.expect(std.mem.indexOf(u8, docs_root, anchor) != null);
        try std.testing.expect(std.mem.indexOf(u8, matrix, anchor) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, matrix, "adjacent notifier support") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing, "not a fifth helper family") != null);
    try std.testing.expect(std.mem.indexOf(u8, docs_root, "notifier evidence stays release-surface support") != null);
}

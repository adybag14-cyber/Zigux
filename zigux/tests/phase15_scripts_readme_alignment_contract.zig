const std = @import("std");

const MarkerSet = struct {
    path: []const u8,
    limit: usize = 192 * 1024,
    required: []const []const u8 = &.{},
    forbidden: []const []const u8 = &.{},
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectMarkerSet(markers: MarkerSet) !void {
    const text = try readRepoFile(markers.path, markers.limit);
    defer std.testing.allocator.free(text);

    for (markers.required) |marker| {
        try expectContains(text, marker);
    }

    for (markers.forbidden) |marker| {
        try expectMissing(text, marker);
    }
}

test "scripts README keeps Phase 15 governance reminder in maintenance mode" {
    try expectMarkerSet(.{
        .path = "scripts/zigux/README.md",
        .required = &.{
            "## Phase 15",
            "Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work",
            "without implying Architecture Council approval or a deep-core port-readiness decision",
            "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
            "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
            "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
            "`scripts/zigux/check-phase15-architecture-council-packet.py`",
            "`scripts/zigux/check-phase15-review-process-handoff.py`",
            "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
            "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
            "`scripts/zigux/check-phase15-shared-summary-gap.py`",
            "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
            "`scripts/zigux/validate-phase15.py`",
            "`Documentation/zigux/phase15-freeze-map-governance.md`",
            "`Documentation/zigux/phase15-indefinite-c-policy.md`",
            "`Documentation/zigux/phase15-parity-scorecard.md`",
            "`Documentation/zigux/phase15-readiness-gate-survey.md`",
            "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
            "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
            "`Documentation/zigux/phase15-shared-summary-gap.md`",
            "`zigux/tests/phase15_build.zig`",
            "no Architecture Council approval is currently recorded for a freeze-map status change",
        },
    });
}

test "scripts README keeps Phase 15 wrapper and workflow routes blocked" {
    try expectMarkerSet(.{
        .path = "scripts/zigux/README.md",
        .required = &.{
            "although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`",
            "keep those route names as blocked route vocabulary rather than directly readable replay paths",
            "`.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route",
            "shared-summary gap vocabulary rather than shipped Phase 15 replay evidence",
        },
    });

    try expectMarkerSet(.{
        .path = "zigux/Makefile",
        .limit = 96 * 1024,
        .forbidden = &.{
            "phase15-validate:",
            "phase15-test:",
            "phase15:",
            ".PHONY: phase15",
        },
        .required = &.{
            "phase14-validate",
        },
    });

    try expectMarkerSet(.{
        .path = ".github/workflows/zigux-bootstrap.yml",
        .limit = 128 * 1024,
        .forbidden = &.{
            "Phase 15 validate",
            "Phase 15 test",
            "Run current Phase 15",
        },
    });
}

test "scripts alignment checker fail-closes on the same Phase 15 packet" {
    try expectMarkerSet(.{
        .path = "scripts/zigux/check-phase15-scripts-readme-alignment.py",
        .limit = 96 * 1024,
        .required = &.{
            "README_PHASE15_MARKERS",
            "WORKFLOW_STALE_MARKERS",
            "STALE_PRESENT_ROUTE_MARKERS",
            "REQUIRED_FILES",
            "\"## Phase 15\"",
            "Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work",
            "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
            "`zigux/tests/phase15_build.zig`",
            "the directly readable `scripts/zigux/validate-phase15.py` maintenance gate",
            "keep those route names as blocked route vocabulary rather than directly readable replay paths",
            "no Architecture Council approval is currently recorded for a freeze-map status change",
            "\"phase15-validate:\"",
            "\"phase15-test:\"",
            "\"phase15:\"",
            "\"Phase 15 validate\"",
            "\"Phase 15 test\"",
            "\"Run current Phase 15\"",
        },
    });
}

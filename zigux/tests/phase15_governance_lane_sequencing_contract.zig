const std = @import("std");

const Surface = struct {
    path: []const u8,
    markers: []const []const u8,
};

const owner_packets = [_][]const u8{
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-deep-core-blocker-survey.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-architecture-council-decision-index.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
};

const reminder_surfaces = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
};

const replay_commands = [_][]const u8{
    "python3 scripts/zigux/check-phase15-docs-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "python3 scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase15-architecture-council-packet.py",
    "python3 scripts/zigux/check-phase15-review-process-handoff.py",
    "python3 scripts/zigux/check-phase15-handoff-note-alignment.py",
    "python3 scripts/zigux/check-phase15-shared-summary-gap.py",
    "python3 scripts/zigux/validate-phase15.py",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "zig test zigux/tests/phase15_governance_lane_sequencing.zig",
};

const blocked_route_markers = [_][]const u8{
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    ".github/workflows/zigux-bootstrap.yml",
    "dedicated Phase 15 validate, test, or aggregate route",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsAll(haystack: []const u8, terms: []const []const u8) !void {
    for (terms) |term| {
        try expectContains(haystack, term);
    }
}

fn expectSurface(surface: Surface) !void {
    const text = try readRepoFile(surface.path, 192 * 1024);
    defer std.testing.allocator.free(text);
    try expectContainsAll(text, surface.markers);
}

test "governance sequencing note keeps owner packets and shared-surface limits explicit" {
    const sequencing = try readRepoFile("Documentation/zigux/phase15-governance-lane-sequencing.md", 96 * 1024);
    defer std.testing.allocator.free(sequencing);

    try expectContains(sequencing, "PHASE15_STATUS=governance_lane_sequencing_packet_landed");
    try expectContains(sequencing, "PHASE15_SLICE=architecture-council-governance-lane-boundaries");
    try expectContains(sequencing, "current-master-readback-2026-05-27");
    try expectContains(sequencing, "Phase 15 is a governance tranche, not a hidden deep-core delivery lane.");
    try expectContains(sequencing, "which Architecture Council packet owns freeze-map status review");
    try expectContains(sequencing, "which neighboring packet owns blocked-posture accounting");
    try expectContains(sequencing, "which neighboring packet owns the stay-in-C policy vocabulary");
    try expectContains(sequencing, "which neighboring packet owns the study-only anchor inventory outside blocked status-change rows");

    for (owner_packets) |path| {
        try expectContains(sequencing, path);
    }

    for (reminder_surfaces) |path| {
        try expectContains(sequencing, path);
    }

    try expectContains(sequencing, "they do not own freeze-map status decisions");
    try expectContains(sequencing, "the broader Phase 15 make-wrapper and shared-CI routes still remain gap-tracked");
    try expectContains(sequencing, "blocked current-master gaps rather than silently treating them as direct evidence");
}

test "sequencing rules keep owner packets ahead of broad reminder prose" {
    const sequencing = try readRepoFile("Documentation/zigux/phase15-governance-lane-sequencing.md", 96 * 1024);
    defer std.testing.allocator.free(sequencing);

    const expected_order = [_][]const u8{
        "1. refresh repo reality for the freeze-map anchor set and blocker posture first",
        "2. refresh the dedicated deep-core blocker survey if the roadmap-versus-current-master crosswalk changes",
        "3. refresh the parity scorecard only if a blocker posture, owner, approver set, or evidence path changed",
        "4. refresh the Architecture Council review-process packet only if the request-field inventory, stay-in-C closeout rule, or reopen-evidence rule changed",
        "5. refresh the indefinite-C policy packet only if the stay-in-C vocabulary or reopen-trigger catalog changed",
        "6. refresh readiness, handoff, shared-build, study-only-accounting, shared-summary, and other reminder surfaces only after the owning packet already says the same thing",
    };

    var cursor: usize = 0;
    for (expected_order) |step| {
        const tail = sequencing[cursor..];
        const relative = std.mem.indexOf(u8, tail, step) orelse return error.MissingSequencingStep;
        cursor += relative + step.len;
    }

    try expectContains(sequencing, "This ordering keeps the Architecture Council source-of-truth files ahead of broad reminder prose.");
}

test "governance packet records replay triggers without promoting blocked wrappers" {
    const sequencing = try readRepoFile("Documentation/zigux/phase15-governance-lane-sequencing.md", 96 * 1024);
    defer std.testing.allocator.free(sequencing);

    for (replay_commands) |command| {
        try expectContains(sequencing, command);
    }

    for (blocked_route_markers) |marker| {
        try expectContains(sequencing, marker);
    }

    try expectContains(sequencing, "validator-first replay and the dedicated shared-build replay are directly readable");
    try expectContains(sequencing, "no Architecture Council approval is currently recorded for a freeze-map status change");
    try expectContains(sequencing, "a deep-core status change has been approved");
    try expectContains(sequencing, "a missing focused replay, blocked make-wrapper route, or absent shared-CI companion is already landed on current `master`");
    try expectContains(sequencing, "if this lane reopens, reread");
}

test "adjacent freeze-map governance and validator surfaces agree on the sequencing packet" {
    const surfaces = [_]Surface{
        .{
            .path = "Documentation/zigux/phase15-freeze-map-governance.md",
            .markers = &.{
                "Documentation/zigux/phase15-governance-lane-sequencing.md",
                "scripts/zigux/validate-phase15.py",
                "zigux/tests/phase15_build.zig",
                "zigux/Makefile` still carries no `phase15-validate`, `phase15-test`, or `phase15` routes",
                "blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`",
            },
        },
        .{
            .path = "scripts/zigux/validate-phase15.py",
            .markers = &.{
                "\"Documentation/zigux/phase15-governance-lane-sequencing.md\"",
                "\"phase15_governance_lane_manifest_present\": True",
                "\"phase15_governance_lane_replay_present\": True",
                "\"phase15_makefile_present\": True",
                "\"phase15_validate_target_present\": False",
                "\"shared_ci_phase15_present\": False",
            },
        },
        .{
            .path = "zigux/tests/phase15_build.zig",
            .markers = &.{
                "phase15-governance-lane-sequencing",
                "Run the focused Phase 15 governance-lane sequencing test",
                "phase15_governance_lane_sequencing.zig",
            },
        },
    };

    for (surfaces) |surface| {
        try expectSurface(surface);
    }
}

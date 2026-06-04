const std = @import("std");
const options = @import("phase15_route_gap_boundary_options");

const RequiredSurface = struct {
    name: []const u8,
    body: []const u8,
    required_markers: []const []const u8,
};

const ForbiddenSurface = struct {
    name: []const u8,
    body: []const u8,
    forbidden_markers: []const []const u8,
};

const docs_root_markers = [_][]const u8{
    "Phase 15 notes",
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_build.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "blocked route vocabulary",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
};

const scripts_root_markers = [_][]const u8{
    "## Phase 15",
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_build.zig",
    "broader dedicated `phase15*` wrapper and shared-CI route names stay repo-reality gaps",
    "does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`",
    ".github/workflows/zigux-bootstrap.yml",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
};

const review_checklist_markers = [_][]const u8{
    "if a freeze-map anchor is entering Architecture Council status review",
    "required approver set",
    "rollback owner",
    "evidence archive path",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const readiness_markers = [_][]const u8{
    "PHASE15_STATUS=readiness_gate_survey_landed",
    "zigux/tests/phase15_build.zig",
    "phase15*` Makefile wrappers",
    "workflow routes",
    "make -C zigux phase15-validate` remains blocked route vocabulary",
    "make -C zigux phase15-test` remains blocked route vocabulary",
    "make -C zigux phase15` remains blocked route vocabulary",
    ".github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route",
};

const validator_markers = [_][]const u8{
    "EXPECTED_BLOCKED_BROADER_ROUTES",
    "\"missing_make_targets\": [\"phase15-validate\", \"phase15-test\", \"phase15\"]",
    "\"missing_workflow_phase15_route\": True",
    "\"phase15_build_zig_present\": True",
    "\"phase15_validate_target_present\": False",
    "\"phase15_test_target_present\": False",
    "\"phase15_aggregate_target_present\": False",
    "\"shared_ci_phase15_present\": False",
};

const makefile_forbidden_markers = [_][]const u8{
    "\nphase15-validate:",
    "\nphase15-test:",
    "\nphase15:",
};

const workflow_forbidden_markers = [_][]const u8{
    "Validate Phase 15 governance packet",
    "Run Phase 15 governance tests",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
};

fn expectAllMarkers(surface: RequiredSurface) !void {
    for (surface.required_markers) |marker| {
        if (!std.mem.containsAtLeast(u8, surface.body, 1, marker)) {
            std.debug.print("{s} missing marker: {s}\n", .{ surface.name, marker });
            return error.MissingMarker;
        }
    }
}

fn expectNoMarkers(surface: ForbiddenSurface) !void {
    for (surface.forbidden_markers) |marker| {
        if (std.mem.containsAtLeast(u8, surface.body, 1, marker)) {
            std.debug.print("{s} unexpectedly contains marker: {s}\n", .{ surface.name, marker });
            return error.UnexpectedMarker;
        }
    }
}

test "Phase 15 shared reminders keep route gap explicit" {
    const surfaces = [_]RequiredSurface{
        .{
            .name = "Documentation/zigux/README.md",
            .body = options.docs_root,
            .required_markers = &docs_root_markers,
        },
        .{
            .name = "scripts/zigux/README.md",
            .body = options.scripts_root,
            .required_markers = &scripts_root_markers,
        },
        .{
            .name = "Documentation/zigux/review-checklist.md",
            .body = options.review_checklist,
            .required_markers = &review_checklist_markers,
        },
        .{
            .name = "Documentation/zigux/phase15-readiness-gate-survey.md",
            .body = options.readiness_survey,
            .required_markers = &readiness_markers,
        },
    };

    for (surfaces) |surface| {
        try expectAllMarkers(surface);
    }
}

test "Phase 15 validator models wrappers and workflow routes as absent" {
    try expectAllMarkers(.{
        .name = "scripts/zigux/validate-phase15.py",
        .body = options.validator,
        .required_markers = &validator_markers,
    });
}

test "Phase 15 make and workflow route names have not silently landed" {
    const forbidden = [_]ForbiddenSurface{
        .{
            .name = "zigux/Makefile",
            .body = options.makefile,
            .forbidden_markers = &makefile_forbidden_markers,
        },
        .{
            .name = ".github/workflows/zigux-bootstrap.yml",
            .body = options.workflow,
            .forbidden_markers = &workflow_forbidden_markers,
        },
    };

    for (forbidden) |surface| {
        try expectNoMarkers(surface);
    }
}

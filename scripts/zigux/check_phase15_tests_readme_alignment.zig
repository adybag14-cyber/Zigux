// Ported from check-phase15-tests-readme-alignment.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_TESTS_README_ALIGNMENT_SELF_TEST=pass";

const DIRECT_PACKET_PATHS = [_][]const u8{
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts\\zigux/check_phase15_docs_readme_alignment.zig",
    "scripts\\zigux/check_phase15_scripts_readme_alignment.zig",
    "scripts\\zigux/check_phase15_tests_readme_alignment.zig",
    "scripts\\zigux/check_phase15_review_checklist_study_only_alignment.zig",
    "scripts\\zigux/check_phase15_review_process_handoff.zig",
    "scripts\\zigux/check_phase15_handoff_note_alignment.zig",
    "scripts\\zigux/check_phase15_shared_summary_gap.zig",
    "scripts\\zigux/check_phase15_readiness_gate_packet.zig",
    "scripts\\zigux/validate_phase15.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_build.zig",
};

const MAKEFILE_PATH = "zigux/Makefile";

const REQUIRED_MARKERS = [_][]const u8{
    "Phase 15 governance packet",
    "Keep the current bounded Phase 15 governance reminder explicit through",
    "Keep `scripts\\zigux/check_phase15_docs_readme_alignment.zig`, `scripts\\zigux/check_phase15_scripts_readme_alignment.zig`, `scripts\\zigux/check_phase15_tests_readme_alignment.zig`, `scripts\\zigux/check_phase15_review_checklist_study_only_alignment.zig`, `scripts\\zigux/check_phase15_review_process_handoff.zig`, `scripts\\zigux/check_phase15_handoff_note_alignment.zig`, and `scripts\\zigux/check_phase15_shared_summary_gap.zig` explicit as the shipped reminder guards so the tests-root summary stays in maintenance-mode truthfulness work instead of implying Architecture Council approval or direct deep-core port-readiness.",
    "Keep the directly readable tests-root Phase 15 governance packet explicit through",
    "Current `master` does materialize `zigux/tests/phase15_architecture_council_review_process_build.zig`, so keep that focused build-file replay in the directly readable governance packet instead of undercounting the Architecture Council review-process evidence.",
    "Current `master` does materialize `zigux/tests/phase15_handoff_next_steps_manifest.json`, so keep that handoff-specific manifest in the directly readable governance packet instead of carrying it as a broader repo-reality gap.",
    "Current `master` does materialize `zigux/tests/phase15_handoff_next_steps.zig`, so keep that focused handoff-specific replay in the directly readable governance packet instead of carrying the handoff packet as manifest-only inventory.",
    "Current `master` does materialize `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`, so keep that focused lane-sequencing manifest-plus-replay pair in the directly readable governance packet instead of leaving the Architecture Council maintenance route undercounted.",
    "Current `master` does materialize `zigux/tests/phase15_parity_scorecard.json`, so keep that machine-readable parity scorecard companion explicit beside `zigux/tests/phase15_parity_scorecard.zig` in the directly readable governance packet instead of carrying the scorecard as replay-only evidence.",
    "Current `master` now directly materializes `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, so keep that focused lane-owner replay in the directly readable governance packet instead of carrying it as a broader repo-reality gap.",
    "Current `master` now directly materializes `scripts\\zigux/validate_phase15.zig`, so keep that validator-first maintenance gate explicit beside the directly readable governance packet instead of carrying it as a broader repo-reality gap.",
    "Current `master` does materialize `zigux/tests/phase15_build.zig`, so keep that shared Phase 15 governance build companion explicit beside the directly readable governance packet instead of carrying it as a broader dedicated-build repo-reality gap.",
    "Although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names in the same blocked-route bucket until direct readback proves they have returned.",
    "without implying any Architecture Council approval for a freeze-map status change?",
};

const TESTS_README_PATH = "zigux/tests/README.md";

const VALIDATOR_REL = "scripts\\zigux/validate_phase15.zig";

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    {
        const relative_path = "scripts\\zigux/validate_phase15.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (REQUIRED_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
        }
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    {
        const relative_path = "scripts\\zigux/validate_phase15.zig";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (REQUIRED_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE15_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        try guard.printLine(io, "PHASE15_TESTS_README_ALIGNMENT_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}

const std = @import("std");

const RepoEvidence = struct {
    phase15_validator_script_present: bool,
    phase15_validate_target_present: bool,
    phase15_test_target_present: bool,
    shared_ci_phase15_present: bool,
    phase15_replay_green_on_current_master: bool,
};

const Manifest = struct {
    surveyed_commit_mode: []const u8,
    surveyed_commit: []const u8,
    repo_evidence: RepoEvidence,
    phase15_validate_checkers: []const []const u8,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 15 readiness manifest preserves the parked validator-first route" {
    const manifest_json = try readRepoFile("zigux/tests/phase15_readiness_gate_manifest.json", 8 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("dated_master_readback", manifest.surveyed_commit_mode);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-13", manifest.surveyed_commit);
    try std.testing.expect(manifest.repo_evidence.phase15_validator_script_present);
    try std.testing.expect(manifest.repo_evidence.phase15_validate_target_present);
    try std.testing.expect(manifest.repo_evidence.phase15_test_target_present);
    try std.testing.expect(manifest.repo_evidence.shared_ci_phase15_present);
    try std.testing.expect(manifest.repo_evidence.phase15_replay_green_on_current_master);
    try std.testing.expectEqual(@as(usize, 2), manifest.phase15_validate_checkers.len);
    try std.testing.expectEqualStrings(
        "scripts/zigux/check-phase15-scripts-readme-alignment.py",
        manifest.phase15_validate_checkers[0],
    );
    try std.testing.expectEqualStrings(
        "scripts/zigux/check-phase15-review-process-handoff.py",
        manifest.phase15_validate_checkers[1],
    );
}

test "phase 15 readiness note and replay routes stay aligned" {
    const readiness_note = try readRepoFile("Documentation/zigux/phase15-readiness-gate-survey.md", 24 * 1024);
    defer std.testing.allocator.free(readiness_note);

    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 64 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    const tests_readme = try readRepoFile("zigux/tests/README.md", 64 * 1024);
    defer std.testing.allocator.free(tests_readme);

    const makefile = try readRepoFile("zigux/Makefile", 24 * 1024);
    defer std.testing.allocator.free(makefile);

    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 24 * 1024);
    defer std.testing.allocator.free(workflow);

    try expectContains(readiness_note, "PHASE15_LANE_KEY=P15-L01");
    try expectContains(readiness_note, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(readiness_note, "PHASE15_SURVEYED_HEAD=current-master-readback-2026-05-13");
    try expectContains(readiness_note, "The packet remains parked.");
    try expectContains(readiness_note, "no Architecture Council approval is currently recorded");
    try expectContains(readiness_note, "python3 scripts/zigux/validate-phase15.py");
    try expectContains(readiness_note, "python3 scripts/zigux/check-phase15-shared-summary-gap.py");
    try expectContains(readiness_note, "shared-summary lane `P15-Y06`");
    try expectContains(readiness_note, "zig build test --build-file zigux/tests/phase15_build.zig");
    try expectContains(readiness_note, "make -C zigux phase15-validate");
    try expectContains(readiness_note, "make -C zigux phase15-test");
    try expectContains(readiness_note, "the remaining blocker is still `phase15-deep-core-status-change-blocker`");
    try expectContains(readiness_note, "scripts/zigux/check-phase15-review-process-handoff.py");
    try expectContains(readiness_note, "zigux/tests/phase15_readiness_gate_manifest.json");
    try expectContains(readiness_note, "zigux/tests/phase15_readiness_gate.zig");
    try expectContains(
        readiness_note,
        "whether the dedicated readiness packet still keeps the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes aligned",
    );

    try expectContains(scripts_readme, "validate-phase15.py");
    try expectContains(scripts_readme, "check-phase15-scripts-readme-alignment.py");
    try expectContains(scripts_readme, "check-phase15-review-process-handoff.py");
    try expectContains(scripts_readme, "zigux/tests/phase15_readiness_gate.zig");
    try expectContains(tests_readme, "zigux/tests/phase15_readiness_gate.zig");
    try expectContains(tests_readme, "zigux/tests/phase15_build.zig");
    try expectContains(makefile, "PHONY += phase15-validate phase15-test phase15");
    try expectContains(makefile, "scripts/zigux/validate-phase15.py");
    try expectContains(makefile, "scripts/zigux/check-phase15-review-process-handoff.py --self-test");
    try expectContains(makefile, "$(ZIG) build test --build-file zigux/tests/phase15_build.zig");
    try expectContains(workflow, "Validate Phase 15 governance packet");
    try expectContains(workflow, "Run Phase 15 governance tests");
}

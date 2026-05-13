const std = @import("std");

const manifest_text = @embedFile("phase4_perf_baseline_manifest.json");

fn requireMarker(marker: []const u8) !void {
    if (std.mem.indexOf(u8, manifest_text, marker) == null) {
        return error.MissingManifestMarker;
    }
}

fn requireMarkerCount(marker: []const u8, expected_count: usize) !void {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, manifest_text, start, marker)) |index| {
        count += 1;
        start = index + marker.len;
    }
    if (count != expected_count) {
        return error.UnexpectedManifestMarkerCount;
    }
}

fn requireRepoMarker(repo_root_relative_path: []const u8, marker: []const u8) !void {
    const source = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        repo_root_relative_path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
    defer std.testing.allocator.free(source);

    if (std.mem.indexOf(u8, source, marker) == null) {
        return error.MissingRepoMarker;
    }
}

fn requireRepoMarkerAbsent(repo_root_relative_path: []const u8, marker: []const u8) !void {
    const source = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        repo_root_relative_path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
    defer std.testing.allocator.free(source);

    if (std.mem.indexOf(u8, source, marker) != null) {
        return error.UnexpectedRepoMarker;
    }
}

test "phase4 perf baseline survey manifest keeps the current benchmark-command posture explicit" {
    try requireMarker("\"lane_key\": \"P4-L20\"");
    try requireMarker("\"owner\": \"Validation and Perf Team\"");
    try requireMarker("\"rollback_owner\": \"Validation and Perf Team\"");
    try requireMarker("\"decision_owner\": \"Validation and Perf Team\"");
    try requireMarker("\"dedicated_local_checker\": \"scripts/zigux/check-phase4-perf-baseline-packet.py\"");
    try requireMarker("\"dedicated_local_checker_scope\": \"local_only_self_test_and_packet_check\"");
    try requireMarker("\"surface\": \"zigux/tests/atomic64_diff.zig\"");
    try requireMarker("\"gate_owner\": \"ABI and Runtime Team\"");
    try requireMarker("\"gate_rollback_owner\": \"ABI and Runtime Team\"");
    try requireMarker("\"threshold_posture\": \"threshold_pending_until_runtime_atomic64_scope_widens\"");
    try requireMarker("phase4-perf-baseline-atomic64-command-evidence");
    try requireMarker("phase4-perf-baseline-atomic64-command");
    try requireMarker("phase4-perf-baseline-atomic64-acceptable-limit");
    try requireMarker("\"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\"");
    try requireMarker("\"approved_local_only\"");
    try requireMarker("\"median_elapsed_ns\"");
    try requireMarker("seven monotonic samples");
    try requireMarker("shared CI perf promotion");
}

test "phase4 perf baseline survey keeps the dedicated packet owner and rollback owner explicit" {
    try requireMarkerCount("\"owner\": \"Validation and Perf Team\"", 2);
    try requireMarker("\"rollback_owner\": \"Validation and Perf Team\"");
}

test "phase4 perf baseline survey keeps the approved local-only atomic64 limits explicit" {
    try requireMarker("\"acceptable_limit_max_elapsed_ns\": 8192");
    try requireMarker("\"checksum\": 3626254113632800175");
    try requireMarker("\"final_counter\": 130322557735600377");
    try requireMarker("\"checksum\": 9210681150676220922");
    try requireMarker("\"final_counter\": 130322557735600376");

    try std.testing.expectEqual(@as(u64, 8192), @as(u64, 8192));
    try std.testing.expectEqual(@as(u64, 3626254113632800175), @as(u64, 3626254113632800175));
    try std.testing.expectEqual(@as(i64, 130322557735600377), @as(i64, 130322557735600377));
    try std.testing.expectEqual(@as(u64, 9210681150676220922), @as(u64, 9210681150676220922));
    try std.testing.expectEqual(@as(i64, 130322557735600376), @as(i64, 130322557735600376));
}

test "phase4 perf baseline survey keeps the bitmap companion and pending promotion split explicit" {
    try requireMarker("\"surface\": \"zigux/tests/bitmap_diff.zig\"");
    try requireMarker("\"gate_owner\": \"Shared Subsystems Pod\"");
    try requireMarker("\"gate_rollback_owner\": \"Shared Subsystems Pod\"");
    try requireMarker("\"threshold_posture\": \"threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks\"");
    try requireMarker("\"zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\"");
    try requireMarker("phase4-perf-baseline-bitmap-command");
    try requireMarker("phase4-perf-baseline-bitmap-acceptable-limit");
    try requireMarker("phase4-perf-baseline-shared-promotion-decision");
    try requireMarker("\"status\": \"shared CI perf promotion pending\"");
}

test "phase4 perf baseline survey keeps coordination owners, the dedicated survey wrapper, both surface wrappers, and bitmap limits explicit" {
    try requireMarker("\"coordination_owners\": [");
    try requireMarker("\"ABI and Runtime Team\"");
    try requireMarker("\"Shared Subsystems Pod\"");
    try requireMarker(
        "\"dedicated_local_survey_wrapper\": \"zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\"",
    );
    try requireMarkerCount(
        "\"linux_style_wrapper\": \"make -C zigux phase4-perf-baseline-survey\"",
        2,
    );
    try requireMarker(
        "\"local_only_posture_note\": \"The dedicated perf-baseline survey keeps approved local benchmark commands and approved local-only acceptable limits explicit while shared CI perf promotion remains intentionally pending.\"",
    );
    try requireMarker("\"shared_ci_perf_promotion_status\": \"pending\"");
    try requireMarker("\"acceptable_limit_max_elapsed_ns\": 12288");
    try requireMarker("\"checksum\": 5216946504564592253");
    try requireMarker("\"checksum\": 7942141539243507472");
    try requireMarker("\"final_first_zero\": 109");
    try requireMarker("\"owner\": \"Validation and Perf Team\"");

    try std.testing.expectEqual(@as(u64, 12288), @as(u64, 12288));
    try std.testing.expectEqual(@as(u64, 5216946504564592253), @as(u64, 5216946504564592253));
    try std.testing.expectEqual(@as(u64, 7942141539243507472), @as(u64, 7942141539243507472));
    try std.testing.expectEqual(@as(u64, 109), @as(u64, 109));
}

test "phase4 perf baseline survey keeps promotion-decision coordination owners explicit" {
    try requireMarkerCount("\"coordination_owners\": [", 2);
    try requireMarker(
        "    \"coordination_owners\": [\n      \"ABI and Runtime Team\",\n      \"Shared Subsystems Pod\"\n    ]",
    );
}

test "phase4 perf baseline survey keeps exact local-only iteration and sample counts explicit" {
    try requireMarkerCount("\"acceptable_limit_iterations\": 4", 2);
    try requireMarkerCount("\"acceptable_limit_sample_count\": 7", 2);

    try std.testing.expectEqual(@as(u64, 4), @as(u64, 4));
    try std.testing.expectEqual(@as(u64, 7), @as(u64, 7));
}

test "phase4 perf baseline survey keeps reversible delivery evidence explicit" {
    try requireMarker(
        "\"reversible_delivery_evidence\": \"keep scripts/zigux/check-phase4-perf-baseline-packet.py, zigux/tests/phase4_perf_baseline_manifest.json, zigux/tests/phase4_perf_baseline_survey.zig, Documentation/zigux/phase4-validation-matrix.md, Documentation/zigux/phase4-gate-evidence.md, Documentation/zigux/review-checklist.md, zigux/Makefile, and zigux/tests/phase4_build.zig aligned",
    );
    try requireMarker(
        "the dedicated local-only perf packet, the dedicated local-only checker, the shared rollback-ownership matrix, the exact-readback note, the review checklist, the Linux-style wrapper, and the shared Phase 4 build entrypoint",
    );
    try requireMarker(
        "current decision owner, coordination owners, approved local-only acceptable limits, and still-pending shared-CI promotion posture measurable and reversible on the current head.",
    );
}

test "phase4 perf baseline survey keeps the bounded next step explicit" {
    try requireMarker(
        "\"ready_next\": \"keep the dedicated perf-baseline packet local-only while scripts/zigux/check-phase4-perf-baseline-packet.py, zigux/tests/phase4_perf_baseline_survey.zig, Documentation/zigux/phase4-validation-matrix.md, Documentation/zigux/phase4-gate-evidence.md, and Documentation/zigux/review-checklist.md continue to fail closed",
    );
    try requireMarker(
        "decision-owner, coordination-owner, acceptable-limit, and shared-CI-pending promotion markers; only widen beyond that packet if a later bounded Phase 4 lane intentionally approves broader shared CI perf coverage.",
    );
}

test "phase4 perf baseline survey keeps the shared matrix perf-governance packet aligned" {
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "Validation and Perf Team owning that policy decision in coordination with the ABI and Runtime Team and Shared Subsystems Pod as the current gate rollback owners",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "local-only acceptable limits are approved today",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "`zigux/tests/phase4_perf_baseline_survey.zig` dedicated local survey that keeps the approved local benchmark commands and the approved local-only acceptable limits machine-checked for both landed rollback gates",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "`local_only_commands_and_limits_approved_shared_ci_perf_promotion_pending`",
    );
}

test "phase4 perf baseline survey keeps the shared review checklist perf-governance packet aligned" {
    try requireRepoMarker(
        "Documentation/zigux/review-checklist.md",
        "the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    );
    try requireRepoMarker(
        "Documentation/zigux/review-checklist.md",
        "the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    );
    try requireRepoMarker(
        "Documentation/zigux/review-checklist.md",
        "the still-pending shared-CI perf-promotion posture",
    );
}

test "phase4 perf baseline survey keeps the shared gate-evidence perf-governance packet aligned" {
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "including the dedicated local-only perf-baseline survey files plus the matching direct `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and Linux-style `make -C zigux phase4-perf-baseline-survey` replay routes.",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "atomic64 keeps `median_elapsed_ns <= 8192` across seven monotonic samples, and bitmap keeps `median_elapsed_ns <= 12288` across seven monotonic samples.",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "The shipped local perf-baseline survey packet is intentionally separate from that shared exact-readback set: it exact-pins the approved local-only command-and-limit evidence for both rollback gates while keeping shared CI perf coverage out of scope.",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "the Validation and Perf Team stays named as the decision owner for any broader shared-CI perf promotion",
    );
}

test "phase4 perf baseline survey keeps the tests README perf-governance packet aligned" {
    try requireRepoMarker("zigux/tests/README.md", "phase4_perf_baseline_manifest.json");
    try requireRepoMarker("zigux/tests/README.md", "phase4_perf_baseline_survey.zig");
    try requireRepoMarker(
        "zigux/tests/README.md",
        "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
    );
    try requireRepoMarker("zigux/tests/README.md", "make -C zigux phase4-perf-baseline-survey");
    try requireRepoMarker(
        "zigux/tests/README.md",
        "approved local-only benchmark commands and acceptable limits explicit while shared CI perf promotion stays pending",
    );
}

test "phase4 perf baseline survey keeps the dedicated local checker packet explicit" {
    try requireMarker("\"dedicated_local_checker\": \"scripts/zigux/check-phase4-perf-baseline-packet.py\"");
    try requireMarker("\"dedicated_local_checker_scope\": \"local_only_self_test_and_packet_check\"");
    try requireRepoMarker(
        "scripts/zigux/check-phase4-perf-baseline-packet.py",
        "PHASE4_PERF_BASELINE_PACKET_CHECK=pass",
    );
    try requireRepoMarker(
        "scripts/zigux/check-phase4-perf-baseline-packet.py",
        "PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass",
    );
    try requireRepoMarker(
        "scripts/zigux/check-phase4-perf-baseline-packet.py",
        "scripts/zigux/check-phase4-perf-baseline-packet.py",
    );
}

test "phase4 perf baseline survey keeps the dedicated local checker local-only" {
    try requireMarker("\"dedicated_local_checker_scope\": \"local_only_self_test_and_packet_check\"");
    try requireRepoMarker(
        "scripts/zigux/check-phase4-perf-baseline-packet.py",
        "phase4 perf baseline packet stays local-only and self-tested",
    );
    try requireRepoMarker(
        "scripts/zigux/check-phase4-perf-baseline-packet.py",
        "build_unexpected_marker:test_step.dependOn(&run_perf_baseline_survey_tests.step);",
    );
}

test "phase4 perf baseline survey stays outside the shared test and workflow packet" {
    try requireRepoMarker(
        "zigux/tests/phase4_build.zig",
        "const perf_baseline_survey_step = b.step(",
    );
    try requireRepoMarker(
        "zigux/tests/phase4_build.zig",
        "\"phase4-perf-baseline-survey\"",
    );
    try requireRepoMarkerAbsent(
        "zigux/tests/phase4_build.zig",
        "test_step.dependOn(&run_perf_baseline_survey_tests.step);",
    );
    try requireRepoMarkerAbsent(
        ".github/workflows/zigux-bootstrap.yml",
        "phase4-perf-baseline-survey",
    );
}

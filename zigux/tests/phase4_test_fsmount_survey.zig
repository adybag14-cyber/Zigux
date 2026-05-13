const std = @import("std");

const manifest_text = @embedFile("phase4_test_fsmount_manifest.json");

fn requireMarker(marker: []const u8) !void {
    if (std.mem.indexOf(u8, manifest_text, marker) == null) {
        return error.MissingManifestMarker;
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

test "phase4 test_fsmount survey keeps the parked gap packet explicit" {
    try requireMarker("\"lane_key\": \"P4-L19\"");
    try requireMarker("\"phase\": \"Phase 4\"");
    try requireMarker("\"c_anchor\": \"samples/vfs/test-fsmount.c\"");
    try requireMarker("\"current_linux_replay\": \"make M=samples/vfs\"");
    try requireMarker(
        "\"dedicated_local_survey_wrapper\": \"zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig\"",
    );
    try requireMarker(
        "\"dedicated_linux_style_survey_wrapper\": \"make -C zigux phase4-test-fsmount-survey\"",
    );
    try requireMarker(
        "\"validation_entrypoint\": \"zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig\"",
    );
    try requireMarker("\"owner\": \"Validation and Perf Team\"");
    try requireMarker("\"rollback_owner\": \"Validation and Perf Team\"");
    try requireMarker(
        "\"current_measurable_status\": \"absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter\"",
    );
}

test "phase4 test_fsmount survey keeps threshold posture explicit" {
    try requireMarker("\"threshold_posture\": \"reviewability_only_no_perf_threshold\"");
}

test "phase4 test_fsmount survey keeps bootstrap CI posture explicit" {
    try requireMarker(
        "\"bootstrap_ci_posture\": \"reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow\"",
    );
}

test "phase4 test_fsmount survey keeps reversible-delivery evidence explicit" {
    try requireMarker(
        "\"reversible_delivery_evidence\": \"PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface\"",
    );
}

test "phase4 test_fsmount survey keeps the bounded next step explicit" {
    try requireMarker(
        "\"next_bounded_evidence_step\": \"keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter\"",
    );
}

test "phase4 test_fsmount survey keeps the dedicated gap note aligned" {
    try requireRepoMarker(
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        "PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        "PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        "PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        "samples/zigux/test_fsmount.zig",
    );
}

test "phase4 test_fsmount survey keeps shared gate-evidence coverage aligned" {
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "zigux/tests/phase4_test_fsmount_manifest.json",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "zigux/tests/phase4_test_fsmount_survey.zig",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "make -C zigux phase4-test-fsmount-survey",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "reviewability_only_no_perf_threshold",
    );
}

test "phase4 test_fsmount survey keeps shared validation matrix aligned" {
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "* current replay path: `make M=samples/vfs`",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "* dedicated local survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "* survey owner: `Validation and Perf Team`",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "* rollback owner: `Validation and Perf Team`",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "reviewability_only_no_perf_threshold",
    );
}

test "phase4 test_fsmount survey keeps the shared review checklist aligned" {
    try requireRepoMarker(
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    );
    try requireRepoMarker(
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/phase4_test_fsmount_manifest.json",
    );
    try requireRepoMarker(
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/phase4_test_fsmount_survey.zig",
    );
    try requireRepoMarker(
        "Documentation/zigux/review-checklist.md",
        "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    );
    try requireRepoMarker(
        "Documentation/zigux/review-checklist.md",
        "make -C zigux phase4-test-fsmount-survey",
    );
}

test "phase4 test_fsmount survey keeps the tests-root reminder aligned" {
    try requireRepoMarker(
        "zigux/tests/README.md",
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    );
    try requireRepoMarker(
        "zigux/tests/README.md",
        "zigux/tests/phase4_test_fsmount_manifest.json",
    );
    try requireRepoMarker(
        "zigux/tests/README.md",
        "zigux/tests/phase4_test_fsmount_survey.zig",
    );
    try requireRepoMarker(
        "zigux/tests/README.md",
        "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    );
    try requireRepoMarker(
        "zigux/tests/README.md",
        "make -C zigux phase4-test-fsmount-survey",
    );
}

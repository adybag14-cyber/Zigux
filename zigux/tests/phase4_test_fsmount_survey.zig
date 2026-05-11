const std = @import("std");

const manifest_text = @embedFile("phase4_test_fsmount_manifest.json");

fn requireMarker(marker: []const u8) !void {
    if (std.mem.indexOf(u8, manifest_text, marker) == null) {
        return error.MissingManifestMarker;
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

test "phase4 test_fsmount survey keeps reversible-delivery evidence explicit" {
    try requireMarker(
        "\"reversible_delivery_evidence\": \"PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface\"",
    );
}

test "phase4 test_fsmount survey keeps the bounded next step explicit" {
    try requireMarker(
        "\"next_bounded_evidence_step\": \"keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter\"",
    );
}

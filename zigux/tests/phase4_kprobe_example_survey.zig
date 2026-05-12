const std = @import("std");

const manifest_text = @embedFile("phase4_kprobe_example_manifest.json");

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

test "phase4 kprobe survey keeps the parked gap packet explicit" {
    try requireMarker("\"lane_key\": \"P4-L19\"");
    try requireMarker("\"phase\": \"Phase 4\"");
    try requireMarker("\"c_anchor\": \"samples/kprobes/kprobe_example.c\"");
    try requireMarker(
        "\"current_linux_replay\": \"make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m\"",
    );
    try requireMarker(
        "\"validation_entrypoint\": \"zig test zigux/tests/phase4_kprobe_example_survey.zig\"",
    );
    try requireMarker("\"owner\": \"Validation and Perf Team\"");
    try requireMarker("\"rollback_owner\": \"Validation and Perf Team\"");
    try requireMarker(
        "\"current_measurable_status\": \"absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter\"",
    );
}

test "phase4 kprobe survey keeps the local lab replay explicit" {
    try requireMarker(
        "\"local_lab_replay\": \"make -C zigux phase4-kprobe-example-survey\"",
    );
    try requireMarker(
        "\"dedicated_local_survey_wrapper\": \"make -C zigux phase4-kprobe-example-survey\"",
    );
}

test "phase4 kprobe survey keeps reversible-delivery evidence explicit" {
    try requireMarker(
        "\"reversible_delivery_evidence\": \"PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the explicit local_lab_replay marker, the local survey wrapper, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface\"",
    );
}

test "phase4 kprobe survey keeps the bounded next step explicit" {
    try requireMarker(
        "\"next_bounded_evidence_step\": \"keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 validation packet, the explicit local_lab_replay marker, and the dedicated local survey wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter\"",
    );
}

test "phase4 kprobe survey keeps the dedicated gap note aligned" {
    try requireRepoMarker(
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
        "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
        "PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
        "PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
        "samples/zigux/kprobe_example.zig",
    );
}

test "phase4 kprobe survey keeps shared gate-evidence coverage aligned" {
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "zigux/tests/phase4_kprobe_example_manifest.json",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "zigux/tests/phase4_kprobe_example_survey.zig",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "zig test zigux/tests/phase4_kprobe_example_survey.zig",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-gate-evidence.md",
        "make -C zigux phase4-kprobe-example-survey",
    );
}

test "phase4 kprobe survey keeps shared validation matrix aligned" {
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "* current replay path: `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "* dedicated local survey wrapper: `make -C zigux phase4-kprobe-example-survey`",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "* validation entrypoint: `zig test zigux/tests/phase4_kprobe_example_survey.zig`",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "* rollback owner: `Validation and Perf Team`",
    );
    try requireRepoMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        "samples/zigux/kprobe_example.zig",
    );
}

test "phase4 kprobe survey keeps the tests-root reminder aligned" {
    try requireRepoMarker(
        "zigux/tests/README.md",
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    );
    try requireRepoMarker(
        "zigux/tests/README.md",
        "zigux/tests/phase4_kprobe_example_manifest.json",
    );
    try requireRepoMarker(
        "zigux/tests/README.md",
        "zigux/tests/phase4_kprobe_example_survey.zig",
    );
    try requireRepoMarker(
        "zigux/tests/README.md",
        "zig test zigux/tests/phase4_kprobe_example_survey.zig",
    );
    try requireRepoMarker(
        "zigux/tests/README.md",
        "make -C zigux phase4-kprobe-example-survey",
    );
}

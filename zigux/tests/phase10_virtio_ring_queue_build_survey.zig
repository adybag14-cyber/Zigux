const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoRelative(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    const io = std.testing.io;
    return try std.Io.Dir.cwd().readFileAlloc(io, relative_path, allocator, .limited(64 * 1024));
}

test "phase10 virtio ring queue build keeps the focused queue packet explicit" {
    const allocator = std.testing.allocator;

    const build_file = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_ring_queue_build.zig",
    );
    defer allocator.free(build_file);

    try expectContains(
        build_file,
        ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_verify.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_publish_readiness.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_notification_data.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_callback_enable.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_registration_summary.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"../../drivers/virtio/virtio_ring_reset_readiness.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"phase10_virtio_ring_notification_data_readiness.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"phase10_virtio_ring_registration_replay.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"phase10_virtio_ring_prepare_kick_idempotent.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"phase10_virtio_ring_reset_reuse.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"phase10_virtio_ring_reset_readiness.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"phase10_virtio_ring_broken_queue_queue_discipline.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"phase10_virtio_ring_delayed_callback_budget.zig\"),",
    );
    try expectContains(
        build_file,
        ".root_source_file = b.path(\"phase10_virtio_ring_queue_build_survey.zig\"),",
    );
    try expectContains(build_file, ".name = \"phase10-virtio-ring-verify-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-publish-readiness-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-notification-data-wrapper-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-callback-enable-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-registration-summary-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-notification-data-readiness-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-registration-replay-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-prepare-kick-idempotent-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-reset-reuse-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-reset-readiness-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-broken-queue-queue-discipline-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-delayed-callback-budget-tests\",");
    try expectContains(build_file, ".name = \"phase10-virtio-ring-queue-build-survey-tests\",");
    try expectContains(build_file, "\"phase10-virtio-ring-queue-tests\"");
    try expectContains(
        build_file,
        "\"Run the focused Phase 10 virtio ring queue-handling packet tests\"",
    );
    try expectContains(
        build_file,
        "phase10_virtio_ring_queue_tests.dependOn(&run_phase10_virtio_ring_publish_readiness_tests.step);",
    );
    try expectContains(
        build_file,
        "phase10_virtio_ring_queue_tests.dependOn(\n        &run_phase10_virtio_ring_notification_data_wrapper_tests.step,\n    );",
    );
    try expectContains(
        build_file,
        "phase10_virtio_ring_queue_tests.dependOn(\n        &run_phase10_virtio_ring_callback_enable_tests.step,\n    );",
    );
    try expectContains(
        build_file,
        "phase10_virtio_ring_queue_tests.dependOn(\n        &run_phase10_virtio_ring_registration_replay_tests.step,\n    );",
    );
    try expectContains(
        build_file,
        "phase10_virtio_ring_queue_tests.dependOn(\n        &run_phase10_virtio_ring_registration_summary_tests.step,\n    );",
    );
    try expectContains(
        build_file,
        "phase10_virtio_ring_queue_tests.dependOn(\n        &run_phase10_virtio_ring_reset_readiness_tests.step,\n    );",
    );
    try expectContains(
        build_file,
        "phase10_virtio_ring_queue_tests.dependOn(\n        &run_phase10_virtio_ring_queue_build_survey_tests.step,\n    );",
    );
    try expectContains(
        build_file,
        "test_step.dependOn(&run_phase10_virtio_ring_notification_data_wrapper_tests.step);",
    );
    try expectContains(
        build_file,
        "test_step.dependOn(&run_phase10_virtio_ring_callback_enable_tests.step);",
    );
    try expectContains(
        build_file,
        "test_step.dependOn(&run_phase10_virtio_ring_registration_summary_tests.step);",
    );
    try expectContains(
        build_file,
        "test_step.dependOn(&run_phase10_virtio_ring_reset_readiness_tests.step);",
    );
    try expectContains(
        build_file,
        "test_step.dependOn(&run_phase10_virtio_ring_delayed_callback_budget_tests.step);",
    );
    try expectContains(
        build_file,
        "test_step.dependOn(&run_phase10_virtio_ring_queue_build_survey_tests.step);",
    );
}

test "phase10 virtio ring queue build stays below unrelated transport and input lanes" {
    const allocator = std.testing.allocator;

    const build_file = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_ring_queue_build.zig",
    );
    defer allocator.free(build_file);

    try expectNotContains(build_file, "virtio_mmio");
    try expectNotContains(build_file, "virtio_input");
    try expectNotContains(build_file, "phase10_virtio_mmio");
    try expectNotContains(build_file, "phase10_virtio_input");
}

test "phase10 virtio ring queue build survey keeps callback-enable coverage explicit in the queue packet" {
    const allocator = std.testing.allocator;

    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-ring-survey.md",
    );
    defer allocator.free(survey_note);

    const callback_wrapper = try readRepoRelative(
        allocator,
        "drivers/virtio/virtio_ring_callback_enable.zig",
    );
    defer allocator.free(callback_wrapper);

    const manifest = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_ring_manifest.json",
    );
    defer allocator.free(manifest);

    try expectContains(
        survey_note,
        "`drivers/virtio/virtio_ring_callback_enable.zig` keeps callback-ready, pending-used, and broken-queue recovery state explicit inside the same queue-handling packet.",
    );
    try expectContains(
        callback_wrapper,
        "test \"phase10 virtio ring callback-enable wrapper keeps recovery debt explicit after a broken queue is cleared\" {",
    );
    try expectContains(
        manifest,
        "\"preexisting_ring_callback_enable_present\": true",
    );
    try expectContains(
        manifest,
        "\"zigux_destination\": \"drivers/virtio/virtio_ring_callback_enable.zig\"",
    );
}

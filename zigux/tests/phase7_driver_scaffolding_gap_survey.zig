const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    verified_on_utc: []const u8,
    anchor: []const u8,
    survey_state: []const u8,
    review_surfaces: []const []const u8,
    driver_handoff_surfaces: []const []const u8,
    helper_boundary_surfaces: []const []const u8,
    missing_paths: []const []const u8,
    recorded_gap: []const u8,
    next_bounded_step: []const u8,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    try std.testing.expect(false);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 driver scaffolding gap survey keeps the helper-to-driver handoff explicit" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_driver_scaffolding_gap_manifest.json");
    defer allocator.free(manifest_json);
    const survey_note = try readRepoFile(allocator, "Documentation/zigux/phase7-driver-scaffolding-device-registration-gap-survey.md");
    defer allocator.free(survey_note);
    const cmdline_slice = try readRepoFile(allocator, "Documentation/zigux/phase7-cmdline-slice.md");
    defer allocator.free(cmdline_slice);
    const cmdline_manifest = try readRepoFile(allocator, "zigux/tests/phase7_cmdline_manifest.json");
    defer allocator.free(cmdline_manifest);
    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);
    const virtio_core = try readRepoFile(allocator, "drivers/virtio/virtio.zig");
    defer allocator.free(virtio_core);
    const virtio_input = try readRepoFile(allocator, "drivers/virtio/virtio_input.zig");
    defer allocator.free(virtio_input);
    const gpio_wdt = try readRepoFile(allocator, "drivers/watchdog/gpio_wdt.zig");
    defer allocator.free(gpio_wdt);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P7-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/cmdline.c", manifest.anchor);
    try std.testing.expectEqualStrings("helper_to_driver_handoff_gap_documented", manifest.survey_state);
    try std.testing.expect(manifest.verified_on_utc.len != 0);
    try std.testing.expectEqual(@as(usize, 0), manifest.missing_paths.len);

    try expectSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-driver-scaffolding-device-registration-gap-survey.md");
    try expectSliceContains(manifest.review_surfaces, "zigux/tests/phase7_driver_scaffolding_gap_manifest.json");
    try expectSliceContains(manifest.review_surfaces, "zigux/tests/phase7_driver_scaffolding_gap_survey.zig");
    try expectSliceContains(manifest.review_surfaces, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectSliceContains(manifest.review_surfaces, "zigux/tests/phase7_cmdline_manifest.json");
    try expectSliceContains(manifest.review_surfaces, "drivers/virtio/virtio.zig");
    try expectSliceContains(manifest.review_surfaces, "drivers/virtio/virtio_input.zig");
    try expectSliceContains(manifest.review_surfaces, "drivers/watchdog/gpio_wdt.zig");

    try expectSliceContains(manifest.driver_handoff_surfaces, "drivers/virtio/virtio.zig:queue_registration_ready");
    try expectSliceContains(manifest.driver_handoff_surfaces, "drivers/virtio/virtio_input.zig:RegistrationPreflightSummary");
    try expectSliceContains(manifest.driver_handoff_surfaces, "drivers/watchdog/gpio_wdt.zig:RegisterDeviceCallSummary");
    try expectSliceContains(manifest.helper_boundary_surfaces, "Documentation/zigux/phase7-cmdline-slice.md");
    try expectSliceContains(manifest.helper_boundary_surfaces, "zigux/tests/phase7_cmdline_manifest.json");
    try expectSliceContains(manifest.helper_boundary_surfaces, "samples/zigux/README.md");

    try expectContains(survey_note, "`PHASE7_STATUS=survey_packet_landed`");
    try expectContains(survey_note, "`PHASE7_SLICE=driver-scaffolding-device-registration-gap-survey`");
    try expectContains(survey_note, "`PHASE7_LANE_KEY=P7-L01`");
    try expectContains(survey_note, "Phase 7 is still a helper-only leaf phase in the roadmap");
    try expectContains(survey_note, "drivers/virtio/virtio.zig` exposes `queue_registration_ready`");
    try expectContains(survey_note, "drivers/virtio/virtio_input.zig` exposes `RegistrationPreflightSummary`");
    try expectContains(survey_note, "drivers/watchdog/gpio_wdt.zig` exposes `registerDeviceCallSummary`");
    try expectContains(survey_note, "the gap is the handoff boundary itself, not missing Phase 7 helper code");

    try expectContains(cmdline_slice, "`PHASE7_SLICE=cmdline-runtime-leaf`");
    try expectContains(cmdline_slice, "Current `master` still ships no standalone `samples/zigux/*cmdline*` reference sample");
    try expectContains(cmdline_manifest, "\"lane_key\": \"P7-L08\"");
    try expectContains(cmdline_manifest, "\"anchor\": \"lib/cmdline.c\"");
    try expectContains(samples_readme, "* `*cmdline*`");

    try expectContains(virtio_core, "queue_registration_ready");
    try expectContains(virtio_core, ".queue_registration_ready");
    try expectContains(virtio_core, "DriverModelStage = enum");
    try expectContains(virtio_core, "queue_selected,");

    try expectContains(virtio_input, "pub const RegistrationPreflightSummary = struct");
    try expectContains(virtio_input, "ready_for_registration: bool");
    try expectContains(virtio_input, "pub fn registrationPreflightSummary");
    try expectContains(virtio_input, ".ready_for_registration = blocker == null");

    try expectContains(gpio_wdt, "pub const RegisterDeviceCallSummary = struct");
    try expectContains(gpio_wdt, "register_device_requested: bool");
    try expectContains(gpio_wdt, "\"devm_watchdog_register_device\"");
    try expectContains(gpio_wdt, "pub fn registerDeviceCallSummary");

    try expectContains(manifest.recorded_gap, "handoff boundary itself");
    try expectContains(manifest.next_bounded_step, "handoff note, manifest, or survey test");
}
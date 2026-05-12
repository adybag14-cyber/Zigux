const std = @import("std");

const manifest_text = @embedFile("fixtures/phase12_virtio_scsi_manifest.json");
const build_text = @embedFile("phase12_build.zig");
fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase12 virtio scsi manifest records the bounded support packet" {
    try expectContains(manifest_text, "\"lane_key\": \"complex-drivers-infra\"");
    try expectContains(manifest_text, "\"phase\": \"Phase 12\"");
    try expectContains(manifest_text, "\"surveyed_commit\": \"4b5b0667d4651364ccd4b388d84c3107b64fdd6a\"");
    try expectContains(manifest_text, "\"anchor\": \"drivers/scsi/virtio_scsi.c\"");
    try expectContains(manifest_text, "\"drivers/scsi/virtio_scsi.zig\"");
    try expectContains(manifest_text, "\"zigux/tests/phase12_virtio_scsi.zig\"");
    try expectContains(manifest_text, "\"zigux/tests/phase12_virtio_scsi_syntax_lab.zig\"");
    try expectContains(manifest_text, "\"zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig\"");
    try expectContains(manifest_text, "\"zigux/tests/phase12_virtio_scsi_packet.zig\"");
    try expectContains(manifest_text, "\"scripts/zigux/check-phase12-virtio-scsi-packet.py\"");
    try expectContains(manifest_text, "\"Documentation/zigux/phase12-virtio-scsi-slice.md\"");
}

test "phase12 virtio scsi manifest keeps remaining complex-driver gaps explicit" {
    try expectContains(manifest_text, "\"drivers/net/virtio_net.zig\"");
    try expectContains(manifest_text, "\"drivers/nvme/host/pci.zig\"");
    try expectContains(manifest_text, "\"Documentation/zigux/phase12-closure.md\"");
    try expectContains(manifest_text, "\"status\": \"bounded infra prep\"");
}

test "phase12 build wires the support packet into smoke and test routes" {
    try expectContains(build_text, "phase12_virtio_scsi_packet.zig");
    try expectContains(build_text, "phase12-virtio-scsi-packet-tests");
    try expectContains(build_text, "Run Phase 12 virtio-scsi packet tests");
    try expectContains(build_text, "smoke_step.dependOn(&run_packet_tests.step);");
    try expectContains(build_text, "test_step.dependOn(&run_packet_tests.step);");
}

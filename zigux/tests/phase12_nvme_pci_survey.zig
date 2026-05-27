const std = @import("std");

fn readFileAlloc(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn pathExists(path: []const u8) !bool {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    const file = std.Io.Dir.cwd().openFile(io_instance.io(), path, .{}) catch |err| switch (err) {
        error.FileNotFound => return false,
        else => return err,
    };
    file.close(io_instance.io());
    return true;
}

test "phase12 nvme pci survey manifest keeps the bounded starter packet truthful" {
    const manifest_json = try readFileAlloc("zigux/tests/phase12_nvme_pci_manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest_json);

    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "\"lane_key\": \"P12-L08\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "\"anchor\": \"drivers/nvme/host/pci.c\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "\"status\": \"starter_verifier_direct_test_manifest_and_survey_gate_present_shared_direct_replay_present\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "\"status\": \"recovery_budget_summary_shared_direct_replay_present_throughput_gate_missing\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "\"status\": \"driver_local_slice_note_manifest_survey_note_and_survey_gate_present_shared_direct_replay_present\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "\"status\": \"shared_build_present_direct_replay_only_survey_gate_standalone\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "\"status\": \"survey_present_shared_direct_replay_dedicated_verify_and_survey_retained\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "\"status\": \"survey_present_packet_local_route_retained\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "`zigux/tests/phase12_build.zig` now wires the bounded NVMe direct replay") != null);
}

test "phase12 nvme pci survey note keeps the shared direct replay and packet-local survey split explicit" {
    const survey_note = try readFileAlloc("Documentation/zigux/phase12-nvme-pci-survey.md", 16 * 1024);
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE12_STATUS=starter_verifier_direct_replay_manifest_and_survey_gate_present_shared_direct_replay_present") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the shared `zigux/tests/phase12_build.zig` route now wires the bounded NVMe direct replay into `phase12-smoke`, `phase12-test`, and `phase12`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "the verifier shard remains on the dedicated `phase12-nvme-pci-direct-test` route") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "survey gate still stays packet-local") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "route still stays virtio-net-only") == null);
}

test "phase12 nvme pci reopen governance note keeps the shared direct replay bounded" {
    const reopen_note = try readFileAlloc("Documentation/zigux/phase12-nvme-pci-reopen-governance.md", 16 * 1024);
    defer std.testing.allocator.free(reopen_note);

    try std.testing.expect(std.mem.indexOf(u8, reopen_note, "shares one bounded direct replay through the shared `phase12-smoke`, `phase12-test`, and `phase12` routes") != null);
    try std.testing.expect(std.mem.indexOf(u8, reopen_note, "dedicated `phase12-nvme-pci-direct-test` route") != null);
    try std.testing.expect(std.mem.indexOf(u8, reopen_note, "packet-local beside the manifest and survey note") != null);
    try std.testing.expect(std.mem.indexOf(u8, reopen_note, "still stays virtio_net-only") == null);
}

test "phase12 nvme pci survey gate keeps present packet files explicit" {
    try std.testing.expect(try pathExists("drivers/nvme/host/pci.zig"));
    try std.testing.expect(try pathExists("drivers/nvme/host/pci_verify.zig"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-nvme-pci-reopen-governance.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-nvme-pci-slice.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-nvme-pci-survey.md"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci_build.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci_survey_build.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci_manifest.json"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_nvme_pci_survey.zig"));
    try std.testing.expect(try pathExists("zigux/tests/phase12_build.zig"));
    try std.testing.expect(try pathExists("zigux/Makefile"));
}

test "phase12 nvme pci survey gate keeps the shared build and make wrapper surface explicit" {
    const shared_build = try readFileAlloc("zigux/tests/phase12_build.zig", 24 * 1024);
    defer std.testing.allocator.free(shared_build);
    const makefile = try readFileAlloc("zigux/Makefile", 24 * 1024);
    defer std.testing.allocator.free(makefile);

    try std.testing.expect(std.mem.indexOf(u8, shared_build, "phase12_nvme_pci.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, shared_build, "phase12-nvme-pci-direct-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, shared_build, "phase12_nvme_pci_survey.zig") == null);
    try std.testing.expect(std.mem.count(u8, shared_build, "b.createModule(.{") == 13);
    try std.testing.expect(std.mem.count(u8, shared_build, ".addImport(") == 6);
    try std.testing.expect(std.mem.count(u8, shared_build, "b.addTest(.{") == 7);
    try std.testing.expect(std.mem.count(u8, shared_build, "b.addRunArtifact(") == 7);
    try std.testing.expect(std.mem.count(u8, shared_build, "smoke_step.dependOn(") == 7);
    try std.testing.expect(std.mem.count(u8, shared_build, "test_step.dependOn(") == 7);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-smoke:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-test:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-nvme-pci-direct-test:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12-nvme-pci-survey-test:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase12: phase12-validate phase12-smoke phase12-test") != null);
}

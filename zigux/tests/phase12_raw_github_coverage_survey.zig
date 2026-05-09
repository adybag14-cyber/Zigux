const std = @import("std");

const CommitPinnedArtifact = struct {
    anchor: []const u8,
    note_path: []const u8,
    public_tree_paths: []const []const u8,
};

const SharedTreeOnlyAnchor = struct {
    anchor: []const u8,
    note_path: []const u8,
    public_tree_paths: []const []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_ref: []const u8,
    inspected_via: []const u8,
    public_tree_base_url: []const u8,
    public_raw_base_url: []const u8,
    shared_public_read_paths: []const []const u8,
    shared_release_paths: []const []const u8,
    smoke_surface_paths: []const []const u8,
    commit_pinned_artifacts: []const CommitPinnedArtifact,
    shared_tree_only_anchors: []const SharedTreeOnlyAnchor,
};

fn pathExists(io: std.Io, path: []const u8) !bool {
    std.Io.Dir.cwd().access(io, path, .{}) catch |err| switch (err) {
        error.FileNotFound => return false,
        else => return err,
    };
    return true;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectPublicUrlCoverage(
    allocator: std.mem.Allocator,
    note: []const u8,
    tree_base_url: []const u8,
    raw_base_url: []const u8,
    paths: []const []const u8,
) !void {
    for (paths) |path| {
        const tree_url = try std.fmt.allocPrint(allocator, "{s}{s}", .{ tree_base_url, path });
        defer allocator.free(tree_url);
        const raw_url = try std.fmt.allocPrint(allocator, "{s}{s}", .{ raw_base_url, path });
        defer allocator.free(raw_url);

        try expectContains(note, tree_url);
        try expectContains(note, raw_url);
    }
}

test "phase12 raw GitHub coverage manifest keeps the shared fallback split reviewable" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_raw_github_coverage_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const raw_coverage_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-raw-github-coverage-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(raw_coverage_note);

    const sequencing_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-release-sequencing.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(sequencing_note);

    const coordination_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-release-coordination-matrix.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(coordination_matrix);

    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);

    const build_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_file);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P12-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings("master", manifest.surveyed_ref);
    try std.testing.expectEqualStrings("GitHub connector read on 2026-05-09", manifest.inspected_via);
    try std.testing.expectEqualStrings("https://github.com/adybag14-cyber/Zigux/blob/master/", manifest.public_tree_base_url);
    try std.testing.expectEqualStrings("https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/", manifest.public_raw_base_url);
    try std.testing.expectEqual(@as(usize, 12), manifest.shared_public_read_paths.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.shared_release_paths.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.smoke_surface_paths.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.commit_pinned_artifacts.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.shared_tree_only_anchors.len);

    for (manifest.shared_public_read_paths, 0..) |path, i| {
        try std.testing.expect(try pathExists(io_instance.io(), path));
        for (manifest.shared_public_read_paths[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, path, other));
        }
    }
    try expectPublicUrlCoverage(
        std.testing.allocator,
        raw_coverage_note,
        manifest.public_tree_base_url,
        manifest.public_raw_base_url,
        manifest.shared_public_read_paths,
    );

    for (manifest.shared_release_paths, 0..) |path, i| {
        try std.testing.expect(try pathExists(io_instance.io(), path));
        for (manifest.shared_release_paths[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, path, other));
        }
    }

    for (manifest.smoke_surface_paths, 0..) |path, i| {
        try std.testing.expect(try pathExists(io_instance.io(), path));
        for (manifest.smoke_surface_paths[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, path, other));
        }
    }

    var saw_nvme = false;
    var saw_virtio_scsi = false;
    for (manifest.commit_pinned_artifacts, 0..) |artifact, i| {
        try std.testing.expect(try pathExists(io_instance.io(), artifact.note_path));
        for (manifest.commit_pinned_artifacts[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, artifact.anchor, other.anchor));
            try std.testing.expect(!std.mem.eql(u8, artifact.note_path, other.note_path));
        }
        if (std.mem.eql(u8, artifact.anchor, "nvme_pci")) {
            saw_nvme = true;
            try std.testing.expectEqualStrings(
                "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
                artifact.note_path,
            );
        }
        if (std.mem.eql(u8, artifact.anchor, "virtio_scsi")) {
            saw_virtio_scsi = true;
            try std.testing.expectEqualStrings(
                "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
                artifact.note_path,
            );
        }
        for (artifact.public_tree_paths, 0..) |path, j| {
            try std.testing.expect(try pathExists(io_instance.io(), path));
            for (artifact.public_tree_paths[j + 1 ..]) |other| {
                try std.testing.expect(!std.mem.eql(u8, path, other));
            }
        }
    }
    try std.testing.expect(saw_nvme);
    try std.testing.expect(saw_virtio_scsi);

    var saw_virtio_net = false;
    var saw_libbpf = false;
    for (manifest.shared_tree_only_anchors, 0..) |anchor, i| {
        try std.testing.expect(try pathExists(io_instance.io(), anchor.note_path));
        for (manifest.shared_tree_only_anchors[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, anchor.anchor, other.anchor));
            try std.testing.expect(!std.mem.eql(u8, anchor.note_path, other.note_path));
        }
        if (std.mem.eql(u8, anchor.anchor, "virtio_net")) {
            saw_virtio_net = true;
            try std.testing.expectEqualStrings(
                "Documentation/zigux/phase12-virtio-net-survey.md",
                anchor.note_path,
            );
        }
        if (std.mem.eql(u8, anchor.anchor, "libbpf")) {
            saw_libbpf = true;
            try std.testing.expectEqualStrings(
                "Documentation/zigux/phase12-libbpf-segment-survey.md",
                anchor.note_path,
            );
        }
        for (anchor.public_tree_paths, 0..) |path, j| {
            try std.testing.expect(try pathExists(io_instance.io(), path));
            for (anchor.public_tree_paths[j + 1 ..]) |other| {
                try std.testing.expect(!std.mem.eql(u8, path, other));
            }
        }
    }
    try std.testing.expect(saw_virtio_net);
    try std.testing.expect(saw_libbpf);

    try expectContains(raw_coverage_note, "commit-pinned fallback artifacts:");
    try expectContains(raw_coverage_note, "shared-tree-only anchors:");
    try expectContains(raw_coverage_note, "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md");
    try expectContains(raw_coverage_note, "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md");
    try expectContains(raw_coverage_note, "Documentation/zigux/phase12-virtio-net-survey.md");
    try expectContains(raw_coverage_note, "Documentation/zigux/phase12-libbpf-segment-survey.md");
    try expectContains(raw_coverage_note, "Documentation/zigux/phase12-release-coordination-matrix.md");

    try expectContains(sequencing_note, "current public fallback split: two commit-pinned artifacts");
    try expectContains(sequencing_note, "Documentation/zigux/phase12-raw-github-coverage-survey.md");
    try expectContains(sequencing_note, "Documentation/zigux/phase12-release-coordination-matrix.md");

    try expectContains(coordination_matrix, "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2");
    try expectContains(coordination_matrix, "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2");
    try expectContains(coordination_matrix, "Documentation/zigux/phase12-raw-github-coverage-survey.md");

    try expectContains(tests_readme, "Documentation/zigux/phase12-raw-github-coverage-survey.md");
    try expectContains(tests_readme, "Documentation/zigux/phase12-release-coordination-matrix.md");
    try expectContains(tests_readme, "Documentation/zigux/phase12-release-closure-checklist.md");

    try expectContains(build_file, "const smoke_step = b.step(\"smoke\", \"Run Phase 12 direct driver and syntax-lab smoke tests\");");
    try expectContains(build_file, "const test_step = b.step(\"test\", \"Run Phase 12 driver and survey tests\");");
    try expectContains(build_file, "run_phase12_libbpf_reviewability_tests.step");
}

const std = @import("std");

const Anchor = struct {
    id: []const u8,
    anchor: []const u8,
    roadmap_destination: []const u8,
    survey_note_path: []const u8,
    public_read_status: []const u8,
    raw_fallback_catalog_path: []const u8,
    raw_fallback_map_path: []const u8,
    shared_tree_branch_raw_path: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    scope: []const u8,
    public_read_boundary: []const u8,
    last_replayed_public_head: []const u8,
    roadmap_anchor_count: usize,
    commit_pinned_raw_fallback_catalog_count: usize,
    commit_pinned_raw_fallback_map_count: usize,
    shared_tree_only_anchor_count: usize,
    shared_tree_readback_root_count: usize,
    shared_tree_branch_raw_path_count: usize,
    shared_tree_readback_roots: []const []const u8,
    shared_tree_branch_raw_paths: []const []const u8,
    anchors: []const Anchor,
};

test "phase12 raw GitHub coverage survey keeps the roadmap-wide public-read split explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase12_raw_github_coverage_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-raw-github-coverage-survey.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const raw_fallback_catalog = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(raw_fallback_catalog);

    const raw_fallback_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(raw_fallback_map);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P12-L07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 12", manifest.phase);
    try std.testing.expectEqualStrings(
        "raw GitHub fallback catalog survey public-read coverage gaps vs roadmap",
        manifest.scope,
    );
    try std.testing.expectEqualStrings(
        "read_only_public_github_tree_and_raw_paths_only",
        manifest.public_read_boundary,
    );
    try std.testing.expectEqualStrings(
        "0bd402fd6ca83ba2ace6b21e9e57459401b631cd",
        manifest.last_replayed_public_head,
    );
    try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_anchor_count);
    try std.testing.expectEqual(@as(usize, 1), manifest.commit_pinned_raw_fallback_catalog_count);
    try std.testing.expectEqual(@as(usize, 1), manifest.commit_pinned_raw_fallback_map_count);
    try std.testing.expectEqual(@as(usize, 2), manifest.shared_tree_only_anchor_count);
    try std.testing.expectEqual(@as(usize, 4), manifest.shared_tree_readback_root_count);
    try std.testing.expectEqual(@as(usize, 2), manifest.shared_tree_branch_raw_path_count);
    try std.testing.expectEqual(@as(usize, 4), manifest.shared_tree_readback_roots.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.shared_tree_branch_raw_paths.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);

    for ([_][]const u8{
        "https://github.com/adybag14-cyber/Zigux/tree/master/drivers/net",
        "https://github.com/adybag14-cyber/Zigux/tree/master/tools/lib/bpf",
        "https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux",
        "https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests",
    }, 0..) |expected_root, index| {
        try std.testing.expectEqualStrings(expected_root, manifest.shared_tree_readback_roots[index]);
    }

    for ([_][]const u8{
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/net/virtio_net.c",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/tools/lib/bpf/libbpf.c",
    }, 0..) |expected_raw_path, index| {
        try std.testing.expectEqualStrings(expected_raw_path, manifest.shared_tree_branch_raw_paths[index]);
    }

    var shared_tree_only_count: usize = 0;
    var commit_pinned_catalog_count: usize = 0;
    var commit_pinned_map_count: usize = 0;
    var shared_tree_branch_raw_path_count: usize = 0;
    var saw_virtio_net = false;
    var saw_nvme_pci = false;
    var saw_virtio_scsi = false;
    var saw_libbpf = false;
    for (manifest.anchors) |anchor| {
        if (std.mem.eql(u8, anchor.public_read_status, "shared_tree_only")) {
            shared_tree_only_count += 1;
            try std.testing.expectEqual(@as(usize, 0), anchor.raw_fallback_catalog_path.len);
            try std.testing.expectEqual(@as(usize, 0), anchor.raw_fallback_map_path.len);
            try std.testing.expect(anchor.shared_tree_branch_raw_path.len != 0);
            shared_tree_branch_raw_path_count += 1;
        } else if (std.mem.eql(u8, anchor.public_read_status, "commit_pinned_raw_catalog")) {
            commit_pinned_catalog_count += 1;
            try std.testing.expect(std.mem.indexOf(u8, anchor.raw_fallback_catalog_path, "virtio-scsi-raw-github-fallback-catalog.md") != null);
            try std.testing.expectEqual(@as(usize, 0), anchor.raw_fallback_map_path.len);
            try std.testing.expectEqual(@as(usize, 0), anchor.shared_tree_branch_raw_path.len);
        } else if (std.mem.eql(u8, anchor.public_read_status, "commit_pinned_raw_map")) {
            commit_pinned_map_count += 1;
            try std.testing.expectEqual(@as(usize, 0), anchor.raw_fallback_catalog_path.len);
            try std.testing.expect(std.mem.indexOf(u8, anchor.raw_fallback_map_path, "nvme-pci-raw-github-fallback-map.md") != null);
            try std.testing.expectEqual(@as(usize, 0), anchor.shared_tree_branch_raw_path.len);
        } else {
            return error.UnexpectedStatus;
        }

        if (std.mem.eql(u8, anchor.id, "virtio_net")) {
            saw_virtio_net = true;
            try std.testing.expectEqualStrings("drivers/net/virtio_net.c", anchor.anchor);
            try std.testing.expectEqualStrings("drivers/net/virtio_net.zig", anchor.roadmap_destination);
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-virtio-net-survey.md", anchor.survey_note_path);
            try std.testing.expectEqualStrings("shared_tree_only", anchor.public_read_status);
            try std.testing.expectEqualStrings(
                "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/net/virtio_net.c",
                anchor.shared_tree_branch_raw_path,
            );
        }

        if (std.mem.eql(u8, anchor.id, "nvme_pci")) {
            saw_nvme_pci = true;
            try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", anchor.anchor);
        }

        if (std.mem.eql(u8, anchor.id, "virtio_scsi")) {
            saw_virtio_scsi = true;
            try std.testing.expectEqualStrings("drivers/scsi/virtio_scsi.c", anchor.anchor);
        }

        if (std.mem.eql(u8, anchor.id, "libbpf")) {
            saw_libbpf = true;
            try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", anchor.anchor);
            try std.testing.expectEqualStrings("tools/lib/bpf/zigux_segments/", anchor.roadmap_destination);
            try std.testing.expectEqualStrings("Documentation/zigux/phase12-libbpf-segment-survey.md", anchor.survey_note_path);
            try std.testing.expectEqualStrings("shared_tree_only", anchor.public_read_status);
            try std.testing.expectEqualStrings(
                "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/tools/lib/bpf/libbpf.c",
                anchor.shared_tree_branch_raw_path,
            );
        }
    }

    try std.testing.expectEqual(@as(usize, 2), shared_tree_only_count);
    try std.testing.expectEqual(@as(usize, 1), commit_pinned_catalog_count);
    try std.testing.expectEqual(@as(usize, 1), commit_pinned_map_count);
    try std.testing.expectEqual(@as(usize, 2), shared_tree_branch_raw_path_count);
    try std.testing.expect(saw_virtio_net);
    try std.testing.expect(saw_nvme_pci);
    try std.testing.expect(saw_virtio_scsi);
    try std.testing.expect(saw_libbpf);

    for ([_][]const u8{
        "drivers/net/virtio_net.c",
        "drivers/nvme/host/pci.c",
        "drivers/scsi/virtio_scsi.c",
        "tools/lib/bpf/libbpf.c",
        "one anchor keeps a commit-pinned raw fallback catalog",
        "one anchor keeps a commit-pinned raw fallback map",
        "two anchors remain shared-tree-only fallback reads",
        "0bd402fd6ca83ba2ace6b21e9e57459401b631cd",
        "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
        "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
        "https://github.com/adybag14-cyber/Zigux/tree/master/drivers/net",
        "https://github.com/adybag14-cyber/Zigux/tree/master/tools/lib/bpf",
        "https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux",
        "https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/net/virtio_net.c",
        "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/tools/lib/bpf/libbpf.c",
        "PHASE12_SHARED_TREE_READBACK_ROOT_COUNT=4",
        "PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2",
    }) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, survey_note, marker) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_catalog, "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_map, "PHASE12_SURVEYED_COMMIT=8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1") != null);
    try std.testing.expect(std.mem.indexOf(u8, raw_fallback_map, "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md") != null);
}

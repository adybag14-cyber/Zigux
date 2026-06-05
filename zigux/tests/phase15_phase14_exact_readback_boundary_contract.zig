const std = @import("std");

const MarkerSet = struct {
    path: []const u8,
    required_markers: []const []const u8,
};

const docs_root_markers = [_][]const u8{
    "Documentation/zigux/phase14-shared-smoke-current-master-gap.md",
    "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md",
    "`make -C zigux phase14-validate` gate",
    "`phase14-smoke`, `phase14-test`, and `phase14` wrappers remain absent",
    "while `net/core/skbuff.c` and `kernel/rcu/tree.c` remain freeze-in-C anchors",
};

const review_checklist_markers = [_][]const u8{
    "if the change touches the shared Phase 14 smoke packet",
    "`zigux/Makefile` framed as readable current evidence",
    "returned `make -C zigux phase14-validate` gate",
    "`phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
    "`zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` framed as exact-readback gaps",
};

const freeze_map_markers = [_][]const u8{
    "## Freeze In C Initially",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
    "## Study / Boundary Only",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "shared reminder surfaces that summarize freeze posture",
    "route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
};

const smoke_survey_markers = [_][]const u8{
    "`PHASE14_EXECUTABLE_PACKET_READBACK=partial`",
    "`PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`",
    "`PHASE14_STATUS_CHANGE_CLAIM=no`",
    "the readable `zigux/Makefile` body exposes that route",
    "Keep `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, `make -C zigux phase14`",
    "historical packet vocabulary",
};

const shared_gap_markers = [_][]const u8{
    "`PHASE14_GAP_KIND=shared_smoke_current_master_readback_gap`",
    "bounded_validate_route_only",
    "still omitting the broader `phase14-smoke`, `phase14-test`, and `phase14` targets",
    "Remaining Shared-Smoke Readback Gap",
    "does not claim those paths are globally absent from every repo access mode",
};

const attached_toolchain_markers = [_][]const u8{
    "The Phase 14 roadmap keeps the shared smoke packet in a study-only, reviewability-first posture.",
    "keep `make -C zigux phase14-validate` as the only current Phase 14 Make route",
    "do not treat attached-toolchain availability as proof of deep-core execution ownership, parity, or release-readiness",
};

const manifest_markers = [_][]const u8{
    "\"route_status\": \"bounded_validate_route_only\"",
    "\"make -C zigux phase14-validate\"",
    "\"make -C zigux phase14-smoke\"",
    "\"make -C zigux phase14-test\"",
    "\"make -C zigux phase14\"",
    "\"phase14_make_smoke_target_present\": false",
    "\"workflow_runs_phase14_build\": false",
    "\"workflow_runs_phase14_smoke_shard\": false",
};

const packet_docs = [_]MarkerSet{
    .{ .path = "Documentation/zigux/README.md", .required_markers = &docs_root_markers },
    .{ .path = "Documentation/zigux/review-checklist.md", .required_markers = &review_checklist_markers },
    .{ .path = "Documentation/zigux/freeze-map.md", .required_markers = &freeze_map_markers },
    .{ .path = "Documentation/zigux/phase14-end-to-end-smoke-survey.md", .required_markers = &smoke_survey_markers },
    .{ .path = "Documentation/zigux/phase14-shared-smoke-current-master-gap.md", .required_markers = &shared_gap_markers },
    .{ .path = "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md", .required_markers = &attached_toolchain_markers },
    .{ .path = "zigux/tests/phase14_end_to_end_smoke_manifest.json", .required_markers = &manifest_markers },
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase 14 shared docs keep exact-readback and single-gate route posture explicit" {
    for (packet_docs) |doc| {
        const text = try readRepoFile(doc.path, 256 * 1024);
        defer std.testing.allocator.free(text);

        for (doc.required_markers) |marker| {
            try expectContains(text, marker);
        }
    }
}

test "phase 14 route vocabulary stays bounded to one current Makefile gate" {
    const makefile = try readRepoFile("zigux/Makefile", 128 * 1024);
    defer std.testing.allocator.free(makefile);

    const manifest = try readRepoFile("zigux/tests/phase14_end_to_end_smoke_manifest.json", 128 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(makefile, "phase14-validate:");
    try expectContains(makefile, "scripts/zigux/check-phase14-shared-smoke-route.py --self-test");
    try expectContains(makefile, "scripts/zigux/validate-phase14.py");

    try expectNotContains(makefile, "phase14-smoke:");
    try expectNotContains(makefile, "phase14-test:");
    try expectNotContains(makefile, "phase14:");

    try expectContains(manifest, "\"smoke_commands\": [");
    try expectContains(manifest, "\"make -C zigux phase14-validate\"");
    try expectContains(manifest, "\"confirmed_absent_routes\": [");
    try expectContains(manifest, "\"make -C zigux phase14-smoke\"");
    try expectContains(manifest, "\"make -C zigux phase14-test\"");
    try expectContains(manifest, "\"make -C zigux phase14\"");
}

test "freeze-map anchors remain status boundaries, not Phase 14 delivery approvals" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 64 * 1024);
    defer std.testing.allocator.free(freeze_map);

    const smoke_survey = try readRepoFile("Documentation/zigux/phase14-end-to-end-smoke-survey.md", 256 * 1024);
    defer std.testing.allocator.free(smoke_survey);

    try expectContains(freeze_map, "- `kernel/rcu/tree.c`");
    try expectContains(freeze_map, "- `net/core/skbuff.c`");
    try expectContains(freeze_map, "- `kernel/workqueue.c`");
    try expectContains(freeze_map, "- `kernel/trace/ring_buffer.c`");
    try expectContains(freeze_map, "direct Zig port or bridge claims for a freeze-in-C anchor stay blocked");
    try expectContains(freeze_map, "study-only follow-up may gather narrower evidence");

    try expectContains(smoke_survey, "`PHASE14_STATUS_CHANGE_CLAIM=no`");
    try expectContains(smoke_survey, "This shared smoke slice does not claim:");
    try expectContains(smoke_survey, "live workqueue execution, draining, or cancellation parity");
    try expectContains(smoke_survey, "skbuff lifetime, destructor, checksum, or segmentation ownership");
    try expectContains(smoke_survey, "any Phase 14 status change beyond keeping the current evidence packet truthful");
}

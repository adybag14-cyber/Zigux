const std = @import("std");

const active_lane_key = "P7-L13";

const VerificationPaths = struct {
    status: []const u8,
    paths: []const []const u8,
};

const SharedBuildVerification = struct {
    status: []const u8,
    build_file: []const u8,
    missing_sibling_paths: []const []const u8,
};

const CurrentVerification = struct {
    verified_on_utc: []const u8,
    rbtree_packet_visibility: VerificationPaths,
    shared_phase7_build: SharedBuildVerification,
};

const SurveySummary = struct {
    rbtree_c_lines: usize,
    preexisting_phase7_test_files: usize,
    preexisting_phase7_build_present: bool,
    preexisting_phase7_doc_present: bool,
    preexisting_phase7_helper_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    current_replay_status: ?[]const u8 = null,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    ownership_focus: []const []const u8,
    current_verification: CurrentVerification,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked");
}

fn isLowerHexCommitId(value: []const u8) bool {
    if (value.len != 40) {
        return false;
    }

    for (value) |byte| {
        if (!std.ascii.isDigit(byte) and (byte < 'a' or byte > 'f')) {
            return false;
        }
    }

    return true;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectStringSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) {
            return;
        }
    }
    try std.testing.expect(false);
}

test "phase 7 rbtree survey manifest records the landed runtime leaf surface and committed parity fixture" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_rbtree_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-rbtree-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const helper_lane_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-helper-lane-sequencing.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(helper_lane_note);

    const docs_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(docs_root);

    const scripts_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(scripts_root);

    const tests_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(256 * 1024),
    );
    defer std.testing.allocator.free(tests_root);

    const build_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(build_file);

    const validate_phase7 = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/validate-phase7.py",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(validate_phase7);

    const helper_impl = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/rbtree.zig",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(helper_impl);

    const helper_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_rbtree.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(helper_tests);

    const samples_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(samples_readme);

    const zigux_makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(zigux_makefile);

    const parity_checker = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/check-phase7-rbtree-parity.py",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(parity_checker);

    const parity_fixture = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase7_rbtree.json",
        std.testing.allocator,
        .limited(8 * 1024),
    );
    defer std.testing.allocator.free(parity_fixture);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings(active_lane_key, manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expect(isLowerHexCommitId(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/rbtree.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqual(@as(usize, 5), manifest.ownership_focus.len);
    try expectStringSliceContains(
        manifest.ownership_focus,
        "duplicate-key range helpers keep ordered match ownership explicit through findFirst() and nextMatch() instead of hidden cursors",
    );
    try expectStringSliceContains(
        manifest.ownership_focus,
        "detached-node ownership stays explicit through clearNode(), eraseInit(), and eraseInitCached() after erase paths",
    );
    try expectStringSliceContains(
        manifest.ownership_focus,
        "linked-node teardown reconnects prev and next ownership together with leftmost continuity during eraseLinked()",
    );
    try expectStringSliceContains(
        manifest.ownership_focus,
        "replaceNode() copies victim links onto replacement nodes before reconnecting parent and child ownership",
    );
    try expectStringSliceContains(
        manifest.ownership_focus,
        "postorder traversal helpers treat cleared detached nodes as empty so stale parent walks do not leak past the reusable leaf packet",
    );
    try std.testing.expectEqualStrings("2026-05-13T11:41:16Z", manifest.current_verification.verified_on_utc);
    try std.testing.expectEqualStrings("confirmed", manifest.current_verification.rbtree_packet_visibility.status);
    try std.testing.expectEqual(@as(usize, 8), manifest.current_verification.rbtree_packet_visibility.paths.len);
    try std.testing.expectEqualStrings("Documentation/zigux/phase7-rbtree-slice.md", manifest.current_verification.rbtree_packet_visibility.paths[0]);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase7-rbtree-parity.py", manifest.current_verification.rbtree_packet_visibility.paths[7]);
    try std.testing.expectEqualStrings("blocked", manifest.current_verification.shared_phase7_build.status);
    try std.testing.expectEqualStrings("zigux/tests/phase7_build.zig", manifest.current_verification.shared_phase7_build.build_file);
    try std.testing.expectEqual(@as(usize, 2), manifest.current_verification.shared_phase7_build.missing_sibling_paths.len);
    try std.testing.expectEqualStrings("lib/string_helpers.zig", manifest.current_verification.shared_phase7_build.missing_sibling_paths[0]);
    try std.testing.expectEqualStrings("zigux/tests/phase7_string_helpers.zig", manifest.current_verification.shared_phase7_build.missing_sibling_paths[1]);
    try std.testing.expect(manifest.survey_summary.rbtree_c_lines >= 600);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_helper_present);
    try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var saw_build_gate = false;
    var saw_helper = false;
    var saw_survey_gate = false;
    var saw_parity_checker = false;
    var saw_parity_fixture = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(gap.current_replay_status != null);
            try std.testing.expectEqualStrings("blocked_by_missing_sibling_paths", gap.current_replay_status.?);
            try std.testing.expectEqualStrings("zigux/tests/phase7_build.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-helper")) {
            saw_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("lib/rbtree.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase7_rbtree_survey.zig", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-parity-checker")) {
            saw_parity_checker = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("scripts/zigux/check-phase7-rbtree-parity.py", gap.zigux_destination);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-parity-fixture-layer")) {
            saw_parity_fixture = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/fixtures/phase7_rbtree.json", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try expectContains(slice_note, "PHASE7_LANE_KEY=P7-L13");
    try expectContains(slice_note, "the broader shared `zigux/tests/phase7_build.zig` replay is not a direct current-master green claim because that build file still imports the missing sibling string-helpers pair `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`");
    try expectContains(slice_note, "That means the rbtree-local helper packet is still landed, while the broader shared `phase7_build.zig` replay remains parked because the sibling string-helpers helper-plus-test pair is still missing from live `master`.");
    try expectContains(slice_note, "python3 scripts/zigux/check-phase7-rbtree-parity.py");
    try expectContains(slice_note, "this slice does not carry an open parity-fixture follow-up");
    try expectContains(slice_note, "keep this helper slice parked unless a fresh ownership, parity, or review-surface gap appears");
    try expectContains(slice_note, "That means the dedicated rbtree helper replay, survey, manifest, and parity packet remain reviewable inside this slice, while the broader shared `phase7_build.zig` route is still a parked cross-packet target rather than a direct rbtree-local green claim.");
    try expectContains(slice_note, "Shared helper-lane ownership now lives in `Documentation/zigux/phase7-helper-lane-sequencing.md`; keep rbtree-local follow-through under `P7-L13` instead of reusing the shared sequencing lane.");
    try expectContains(slice_note, "detached-node ownership stays explicit through the clearNode and eraseInit reset paths");
    try expectContains(helper_lane_note, "P7-L13");
    try expectContains(helper_lane_note, "`P7-L13` owns only rbtree helper-local parity, traversal, manifest, fixture, checker, or reminder drift.");
    try expectContains(docs_root, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectContains(docs_root, "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample");
    try expectContains(docs_root, "lib/rbtree.zig");
    try expectContains(docs_root, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectContains(docs_root, "zigux/tests/phase7_build.zig");
    try expectContains(scripts_root, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectContains(scripts_root, "zigux/tests/phase7_rbtree.zig");
    try expectContains(scripts_root, "zigux/tests/phase7_rbtree_survey.zig");
    try expectContains(scripts_root, "zigux/tests/phase7_rbtree_manifest.json");
    try expectContains(scripts_root, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectContains(scripts_root, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectContains(scripts_root, "make -C zigux phase7-validate");
    try expectContains(scripts_root, "make -C zigux phase7");
    try expectContains(tests_root, "`scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectContains(tests_root, "the dedicated `zigux/tests/phase7_rbtree_survey.zig` survey gate");
    try expectContains(tests_root, "`make -C zigux phase7-validate`");
    try expectContains(tests_root, "`make -C zigux phase7`");
    try expectContains(build_file, "\"phase7_rbtree.zig\"");
    try expectContains(build_file, "\"phase7_rbtree_survey.zig\"");
    try expectContains(build_file, "\"phase7-rbtree-tests\"");
    try expectContains(build_file, "\"phase7-rbtree-survey-tests\"");
    try expectContains(build_file, "run_rbtree_survey_tests.setCwd(b.path(\"../..\"));");
    try expectContains(validate_phase7, "\"scripts/zigux/check-phase7-rbtree-parity.py\",");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_rbtree.zig\",");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_rbtree_survey.zig\",");
    try expectContains(validate_phase7, "\"zigux/tests/phase7_rbtree_manifest.json\",");
    try expectContains(validate_phase7, "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test");
    try expectContains(validate_phase7, "python3 scripts/zigux/check-phase7-rbtree-parity.py");
    try expectContains(helper_impl, "pub const NodeLinked");
    try expectContains(helper_impl, "pub const RootLinked");
    try expectContains(helper_impl, "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node");
    try expectContains(helper_impl, "pub fn addLinked");
    try expectContains(helper_impl, "pub fn eraseCached(node: *Node, root: *RootCached) ?*Node");
    try expectContains(helper_impl, "pub fn eraseLinked");
    try expectContains(helper_impl, "pub fn clearLinkedNode");
    try expectContains(helper_impl, "pub fn eraseInit");
    try expectContains(helper_impl, "pub fn replaceNodeCached");
    try expectContains(helper_impl, "pub fn firstPostorder");
    try expectContains(helper_impl, "pub fn nextPostorder");
    try expectContains(helper_impl, "test \"rbtree linked helpers track leftmost and neighbour links\"");
    try expectContains(helper_impl, "test \"rbtree eraseInit clears detached nodes after erase\"");
    try expectContains(helper_impl, "test \"rbtree replaceNode keeps displaced nodes non-empty until cleared\"");
    try expectContains(helper_impl, "test \"rbtree postorder and empty node helpers behave\"");
    try expectContains(helper_impl, "try std.testing.expectEqual(@as(?*Node, null), nextPostorder(null));");
    try expectContains(helper_impl, "try std.testing.expectEqual(@as(?*Node, null), nextPostorder(&detached));");
    try expectContains(helper_tests, "phase 7 rbtree traversal helpers walk a manually linked tree");
    try expectContains(helper_tests, "phase 7 rbtree replaceNode and postorder helpers preserve structure");
    try expectContains(helper_tests, "phase 7 rbtree balancing helpers keep ordered insert erase traversal stable");
    try expectContains(helper_tests, "phase 7 rbtree cached helpers return leftmost handoff state");
    try expectContains(helper_tests, "phase 7 rbtree eraseInit detaches erased nodes and keeps traversal stable");
    try expectContains(helper_tests, "phase 7 rbtree detached nodes stay non-empty until callers clear them");
    try expectContains(helper_tests, "phase 7 rbtree clearNode marks detached nodes as empty");
    try expectContains(helper_tests, "phase 7 rbtree eraseLinked clears detached linked ownership state and reconnects neighbours");
    try expectContains(helper_tests, "phase 7 rbtree find helpers walk duplicate-key ranges");
    try expectContains(helper_tests, "phase 7 rbtree postorder traversal matches committed parity fixture");
    try expectContains(helper_tests, "try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.eraseCached(&entries[3].node, &root));");
    try expectContains(samples_readme, "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample;");
    try expectContains(samples_readme, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectContains(samples_readme, "lib/rbtree.zig");
    try expectContains(samples_readme, "zigux/tests/phase7_rbtree.zig");
    try expectContains(samples_readme, "zigux/tests/phase7_rbtree_survey.zig");
    try expectContains(samples_readme, "zigux/tests/phase7_rbtree_manifest.json");
    try expectContains(samples_readme, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectContains(samples_readme, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectContains(samples_readme, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectContains(samples_readme, "zigux/tests/phase7_build.zig");
    try expectContains(zigux_makefile, "phase7-validate:");
    try expectContains(zigux_makefile, "scripts/zigux/check-phase7-rbtree-parity.py --self-test");
    try expectContains(zigux_makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py");
    try expectContains(zigux_makefile, "phase7-test:");
    try expectContains(zigux_makefile, "phase7: phase7-validate phase7-test");
    try expectContains(parity_checker, "PHASE7_RBTREE_PARITY_SELF_TEST=pass");
    try expectContains(parity_checker, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectContains(parity_checker, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectContains(parity_checker, "lib/rbtree.zig");
    try expectContains(parity_fixture, "\"ordered\"");
    try expectContains(parity_fixture, "\"reverse_order\"");
    try expectContains(parity_fixture, "\"replace_order\"");
    try expectContains(parity_fixture, "\"duplicates\"");
    try expectContains(parity_fixture, "\"erase_init\"");
    try expectContains(parity_fixture, "\"postorder\"");

    try std.testing.expectEqual(manifest.gaps.len, starter_landed_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_helper);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_parity_checker);
    try std.testing.expect(saw_parity_fixture);
}

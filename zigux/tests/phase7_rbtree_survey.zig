const std = @import("std");

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
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked");
}

test "phase 7 rbtree survey manifest records the landed runtime leaf surface and parked parity status" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_rbtree_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const roadmap = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(roadmap);

    const docs_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(docs_readme);

    const scripts_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(scripts_readme);

    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);

    const samples_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(samples_readme);

    const zigux_makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        std.testing.allocator,
        .limited(128 * 1024),
    );
    defer std.testing.allocator.free(zigux_makefile);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const rbtree_helper = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/rbtree.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(rbtree_helper);

    const rbtree_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase7_rbtree.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(rbtree_tests);

    const rbtree_slice = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase7-rbtree-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(rbtree_slice);

    const build_inventory_checker = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/check-phase7-build-inventory.py",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_inventory_checker);

    const build_inventory_fixture = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase7_build_inventory.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_inventory_fixture);

    const rbtree_parity_checker = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/check-phase7-rbtree-parity.py",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(rbtree_parity_checker);

    const manifest = parsed.value;
    try expectContains(roadmap, "## Phase 7: In-Kernel Leaf Libraries");
    try expectContains(roadmap, "lib/rbtree.c");
    try expectContains(roadmap, "- `lib/rbtree.zig`");
    try expectContains(roadmap, "runtime-safe leaf helpers");
    try expectContains(roadmap, "integration with validation substrate");

    try expectContains(docs_readme, "the same sample-root catalog also keeps the current no-`samples/zigux/*rbtree*` boundary explicit");
    try expectContains(docs_readme, "rbtree evidence stays under the separate Phase 7 helper bundle rooted in `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, and `zigux/tests/phase7_build.zig` instead of looking like a missing Phase 5 sample port.");
    try expectContains(docs_readme, "`python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`");
    try expectContains(docs_readme, "`python3 scripts/zigux/check-phase7-rbtree-parity.py`");

    try expectContains(scripts_readme, "`validate-phase7.py`");
    try expectContains(scripts_readme, "`check-phase7-build-inventory.py`");
    try expectContains(scripts_readme, "`check-phase7-make-wrapper.py`");
    try expectContains(scripts_readme, "`check-phase7-rbtree-parity.py`");
    try expectContains(scripts_readme, "`make -C zigux phase7-validate` is the validator-first entrypoint for the current Phase 7 flow.");

    try expectContains(tests_readme, "zigux/tests/phase7_rbtree_survey.zig");
    try expectContains(tests_readme, "`scripts/zigux/check-phase7-rbtree-parity.py --self-test`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectContains(tests_readme, "helper roots in `zigux/tests/phase7_build.zig` receive `string_helpers`, `cmdline`, `argv_split`, and `rbtree` through `addImport(...)`");
    try expectContains(tests_readme, "keep the current Phase 7 helper packet reviewable through `zigux/tests/phase7_build.zig`, `zigux/tests/fixtures/phase7_build_inventory.json`, `make -C zigux phase7-test`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-argv-split-packet.py --self-test`, and `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-make-wrapper.py --self-test`, and `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-cmdline-parity.py --self-test`, and `scripts/zigux/check-phase7-cmdline-parity.py`, `scripts/zigux/check-phase7-argv-split-parity.py --self-test`, and `scripts/zigux/check-phase7-argv-split-parity.py`, `scripts/zigux/check-phase7-rbtree-parity.py --self-test`, and `scripts/zigux/check-phase7-rbtree-parity.py` instead of widening into ad hoc helper-local bootstrap rules");

    try expectContains(samples_readme, "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample; keep rbtree evidence under the separate Phase 7 helper bundle rooted in `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, and `zigux/tests/phase7_build.zig` instead of looking like a missing Phase 5 sample port.");
    try expectContains(samples_readme, "verify the shared docs still keep rbtree evidence in Phase 7 instead of `samples/zigux/`");

    try expectContains(zigux_makefile, "phase7-validate:");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test");
    try expectContains(zigux_makefile, "python3 scripts/zigux/check-phase7-rbtree-parity.py");
    try expectContains(zigux_makefile, "phase7-test:");
    try expectContains(zigux_makefile, "zig build test --build-file zigux/tests/phase7_build.zig --summary all");
    try expectContains(zigux_makefile, "phase7: phase7-validate phase7-test");

    try std.testing.expectEqualStrings("P7-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("c0b506e3254e63fe007a72d420bb275846a89093", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/rbtree.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.survey_summary.rbtree_c_lines >= 600);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.preexisting_phase7_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase7_helper_present);
    try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_build_gate = false;
    var saw_helper = false;
    var saw_dedicated_tests = false;
    var saw_slice_note = false;
    var saw_survey_gate = false;
    var saw_parity_follow_up = false;
    var saw_parity_checker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase7-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("validation", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase7_build.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared Phase 7 build step") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-helper")) {
            saw_helper = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("runtime_leaf_helper", gap.kind);
            try std.testing.expectEqualStrings("lib/rbtree.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "eraseInit ownership reset") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "duplicate-range iterator access") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-dedicated-tests")) {
            saw_dedicated_tests = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("validation", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase7_rbtree.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "traversal order") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "detached-node handling") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("documentation", gap.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase7-rbtree-slice.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "bounded product surface") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "actual leaf-helper lane") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("validation", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase7_rbtree_survey.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "machine-checked survey gate") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-parity-fixture-layer")) {
            saw_parity_follow_up = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("differential_validation", gap.kind);
            try std.testing.expectEqualStrings("zigux/tests/fixtures/phase7_rbtree.json", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "eraseInit ownership reset") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "duplicate-key lookup ranges") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "reverse traversal") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "postorder behavior") != null);
        }

        if (std.mem.eql(u8, gap.id, "phase7-rbtree-parity-checker")) {
            saw_parity_checker = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("validation", gap.kind);
            try std.testing.expectEqualStrings("scripts/zigux/check-phase7-rbtree-parity.py", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "dedicated parity checker") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fail-closed review hook") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expectEqual(@as(usize, 7), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_helper);
    try std.testing.expect(saw_dedicated_tests);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_parity_follow_up);
    try std.testing.expect(saw_parity_checker);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_helper, "pub fn iterateMatches") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_helper, "pub fn iterateMatchesReverse") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_helper, "pub fn findLast") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_helper, "pub fn prevMatch") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_helper, "pub fn eraseInit") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_helper, "pub fn clearNode") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_helper, "pub fn emptyNode") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_helper, "pub fn findAdd") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_tests, "phase 7 rbtree eraseInit detaches erased nodes for reuse") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_tests, "phase 7 rbtree detached nodes stay non-empty until callers clear them") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_tests, "phase 7 rbtree clearNode marks detached nodes as empty") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_tests, "phase 7 rbtree findAdd inserts new nodes and returns existing duplicates") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_tests, "phase 7 rbtree reverse duplicate helpers walk duplicate-key ranges") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_tests, "phase 7 rbtree iterateMatchesReverse streams duplicate-key ranges in reverse") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_tests, "phase 7 rbtree postorder traversal matches committed parity fixture") != null);
    try expectContains(rbtree_slice, "runtime-safe leaf helpers");
    try expectContains(rbtree_slice, "integration with validation substrate through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_build.zig`, and `scripts/zigux/check-phase7-rbtree-parity.py`.");
    try expectContains(rbtree_slice, "prove the shared Phase 7 validator packet plus the build-inventory and make-wrapper gates still fail closed before the helper replay runs");
    try expectContains(rbtree_slice, "`python3 scripts/zigux/validate-phase7.py --self-test`");
    try expectContains(rbtree_slice, "`python3 scripts/zigux/check-phase7-build-inventory.py`");
    try expectContains(rbtree_slice, "`python3 scripts/zigux/check-phase7-make-wrapper.py`");
    try expectContains(rbtree_slice, "`make -C zigux phase7-validate`");
    try expectContains(rbtree_slice, "`zig build test --build-file zigux/tests/phase7_build.zig --summary all`");
    try expectContains(rbtree_slice, "keep the manifest-backed survey record machine-checked from `repo_root`");
    try expectContains(rbtree_slice, "the published `make -C zigux phase7` one-command bundle stays aligned with that same review path");
    try expectContains(build_inventory_checker, "BUILD_PATH = ROOT / \"zigux\" / \"tests\" / \"phase7_build.zig\"");
    try expectContains(build_inventory_checker, "FIXTURE_PATH = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase7_build_inventory.json\"");
    try expectContains(build_inventory_checker, "\"shared_validation_gates\"");
    try expectContains(build_inventory_checker, "\"shared_validation_commands\"");
    try expectContains(build_inventory_checker, "\"scripts/zigux/check-phase7-build-inventory.py --self-test\"");
    try expectContains(build_inventory_checker, "\"scripts/zigux/check-phase7-build-inventory.py\"");
    try expectContains(build_inventory_fixture, "\"shared_validation_gates\"");
    try expectContains(build_inventory_fixture, "\"shared_validation_commands\"");
    try expectContains(build_inventory_fixture, "\"scripts/zigux/check-phase7-build-inventory.py\"");
    try expectContains(build_inventory_fixture, "\"phase7-rbtree-tests\"");
    try expectContains(build_inventory_fixture, "\"phase7-rbtree-survey-tests\"");
    try expectContains(build_inventory_fixture, "\"run_rbtree_tests\"");
    try expectContains(build_inventory_fixture, "\"run_rbtree_survey_tests\"");
    try expectContains(build_inventory_fixture, "\"../../lib/rbtree.zig\"");
    try expectContains(build_inventory_fixture, "\"scripts/zigux/check-phase7-rbtree-parity.py --self-test\"");
    try expectContains(rbtree_parity_checker, "SOURCE = ROOT / \"lib\" / \"rbtree.c\"");
    try expectContains(rbtree_parity_checker, "FIXTURE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase7_rbtree.json\"");
    try expectContains(rbtree_parity_checker, "HARNESS = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase7_rbtree_c_harness.c\"");
    try expectContains(rbtree_parity_checker, "PHASE7_RBTREE_PARITY_SELF_TEST_CASE_COUNT=4");
    try std.testing.expect(std.mem.indexOf(u8, rbtree_slice, "detached-node ownership discipline after `erase()` and `replaceNode()`, where callers must still run `clearNode()` before `emptyNode()` becomes true") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_slice, "detached-node clearing semantics") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_slice, "duplicate-aware find-or-insert behavior via `findAdd()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_slice, "erase-and-detach reuse semantics via `eraseInit()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, rbtree_slice, "a machine-checked manifest that records the `lib/rbtree.c` anchor and the landed Phase 7 review surfaces") != null);
}

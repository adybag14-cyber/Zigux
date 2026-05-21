const std = @import("std");

const RbtreeManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    verified_on_utc: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    current_direct_readback_state: []const u8,
    visible_paths: []const []const u8,
    readable_non_owner_paths: []const []const u8,
    public_fallback_non_owner_paths: []const []const u8,
    missing_paths: []const []const u8,
    absent_makefile_markers: []const []const u8,
    absent_workflow_markers: []const []const u8,
    ownership_focus: []const []const u8,
    next_bounded_step: []const u8,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    try std.testing.expect(false);
}

fn expectSliceNotContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) try std.testing.expect(false);
    }
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 rbtree survey keeps the shared-build evidence truthful without claiming helper-local ownership" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_rbtree_manifest.json");
    defer allocator.free(manifest_json);

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-slice.md");
    defer allocator.free(slice_note);

    const direct_anchor_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md");
    defer allocator.free(direct_anchor_note);

    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-rbtree-parity.py");
    defer allocator.free(checker);

    const helper = try readRepoFile(allocator, "tools/lib/rbtree.zig");
    defer allocator.free(helper);

    const helper_companion = try readRepoFile(allocator, "zigux/tests/phase7_rbtree.zig");
    defer allocator.free(helper_companion);

    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);

    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    const parsed = try std.json.parseFromSlice(RbtreeManifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqualStrings("direct_helper_slice_checker_test_note_survey_manifest", manifest.current_direct_readback_state);
    try std.testing.expectEqualStrings("lib/rbtree.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.verified_on_utc.len != 0);

    try expectContains(checker, "PHASE7_RBTREE_PARITY=pass");
    try expectContains(checker, "PHASE7_RBTREE_PARITY_REQUIRED_FILE_COUNT=");
    try expectContains(checker, "PHASE7_RBTREE_PARITY_SELF_TEST=pass");
    try expectContains(checker, "\"Documentation/zigux/phase7-rbtree-slice.md\",");
    try expectContains(checker, "\"tools/lib/rbtree.zig\",");
    try expectContains(checker, "\"zigux/tests/phase7_rbtree.zig\",");
    try expectContains(checker, "\"zigux/tests/phase7_rbtree_survey.zig\",");
    try expectContains(checker, "\"zigux/tests/phase7_rbtree_manifest.json\",");

    try expectContains(slice_note, "`PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_anchor`");
    try expectContains(slice_note, "`PHASE7_LANE_KEY=P7-L13`");
    try expectContains(slice_note, "`tools/lib/rbtree.zig`");
    try expectContains(slice_note, "`Documentation/zigux/phase7-rbtree-direct-anchor-note.md`");
    try expectContains(slice_note, "`scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectContains(slice_note, "`lib/rbtree.zig`");
    try expectContains(slice_note, "`zigux/tests/fixtures/phase7_rbtree.json`");
    try expectContains(slice_note, "same-lane truthfulness keeps the returned slice note, direct-anchor note, parity checker, replay, survey, and manifest explicit without claiming the dedicated fixture pair as returned");
    try expectContains(slice_note, "`scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`");
    try expectContains(slice_note, "`zigux/tests/phase7_build.zig` needed public blob/raw fallback after the authenticated contents bridge returned `404`, so keep that one path framed as returned shared non-owner evidence without overstating authenticated whole-file coverage.");
    try expectContains(slice_note, "in this runtime `zigux/tests/phase7_build.zig` was confirmed through public blob/raw fallback after the authenticated contents bridge returned `404`, while the roadmap-path port and dedicated fixture pair still do not directly materialize on current `master`");
    try expectContains(slice_note, "public-fallback provenance");
    try expectNotContains(slice_note, "- `zigux/tests/phase7_build.zig`");

    try expectSliceContains(manifest.visible_paths, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectSliceContains(manifest.visible_paths, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md");
    try expectSliceContains(manifest.visible_paths, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectSliceContains(manifest.visible_paths, "tools/lib/rbtree.zig");
    try expectSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree.zig");
    try expectSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_survey.zig");
    try expectSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_manifest.json");

    try expectContains(helper, "pub const Node = struct {");
    try expectContains(helper, "pub const RootCached = struct {");
    try expectContains(helper, "pub fn clearNode");
    try expectContains(helper, "pub fn linkNode");
    try expectContains(helper, "pub fn add");
    try expectContains(helper, "pub fn findAdd");
    try expectContains(helper, "pub fn rb_find_add_cached");

    try expectContains(helper_companion, "const rbtree = @import(\"../../tools/lib/rbtree.zig\");");
    try expectContains(helper_companion, "phase 7 rbtree companion replays ordered traversal and duplicate-range helpers");
    try expectContains(helper_companion, "phase 7 rbtree companion replays cached-leftmost promotion and erase-init ownership boundaries");
    try expectContains(helper_companion, "rbtree.matchIterator");
    try expectContains(helper_companion, "rbtree.eraseInitCached");
    try expectContains(helper_companion, "rbtree.rb_erase_init_cached");

    try expectContains(build_file, "../../lib/rbtree.zig");
    try expectContains(build_file, "phase7-rbtree-test");
    try expectContains(build_file, "phase7-rbtree-survey");
    try expectContains(build_file, "Run Phase 7 runtime helper tests");

    try expectContains(makefile, "phase7-validate:");
    try expectContains(makefile, "scripts/zigux/validate-phase7.py");
    try expectNotContains(makefile, "phase7-rbtree-test:");
    try expectNotContains(makefile, "phase7-rbtree-survey:");
    try expectNotContains(makefile, "phase7-test:");

    try expectContains(workflow, "Check current Phase 7 shared-control gap packet");
    try expectContains(workflow, "Check current Phase 7 make-wrapper selftest alignment packet");

    try expectSliceContains(manifest.readable_non_owner_paths, "scripts/zigux/check-phase7-build-wiring.py");
    try expectSliceContains(manifest.readable_non_owner_paths, "scripts/zigux/validate-phase7.py");
    try expectSliceContains(manifest.readable_non_owner_paths, "zigux/tests/phase7_build.zig");
    try expectSliceContains(manifest.readable_non_owner_paths, "zigux/Makefile");
    try expectSliceContains(manifest.readable_non_owner_paths, ".github/workflows/zigux-bootstrap.yml");

    try expectSliceContains(manifest.public_fallback_non_owner_paths, "zigux/tests/phase7_build.zig");
    try expectSliceNotContains(manifest.public_fallback_non_owner_paths, "scripts/zigux/check-phase7-build-wiring.py");
    try expectSliceNotContains(manifest.public_fallback_non_owner_paths, "scripts/zigux/validate-phase7.py");
    try expectSliceNotContains(manifest.public_fallback_non_owner_paths, "zigux/Makefile");
    try expectSliceNotContains(manifest.public_fallback_non_owner_paths, ".github/workflows/zigux-bootstrap.yml");

    try expectSliceNotContains(manifest.missing_paths, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectSliceContains(manifest.missing_paths, "lib/rbtree.zig");
    try expectSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectSliceNotContains(manifest.missing_paths, "zigux/tests/phase7_build.zig");
    try expectSliceNotContains(manifest.missing_paths, "scripts/zigux/validate-phase7.py");
    try expectSliceNotContains(manifest.missing_paths, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectSliceNotContains(manifest.missing_paths, "zigux/tests/phase7_rbtree.zig");

    try expectSliceNotContains(manifest.absent_makefile_markers, "phase7-validate:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-test:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-survey:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7-test:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7:");

    try expectSliceContains(manifest.absent_workflow_markers, "Validate Phase 7 runtime helper gates");
    try expectSliceContains(manifest.absent_workflow_markers, "Run Phase 7 runtime helper tests");
    try expectSliceContains(manifest.absent_workflow_markers, "make -C zigux phase7-test");
    try expectSliceNotContains(manifest.absent_workflow_markers, "make -C zigux phase7-validate");
    try expectNotContains(workflow, "Validate Phase 7 runtime helper gates");
    try expectNotContains(workflow, "Run Phase 7 runtime helper tests");
    try expectNotContains(workflow, "make -C zigux phase7-test");

    try expectSliceContains(manifest.ownership_focus, "the currently readable same-lane rbtree packet now includes the direct helper at `tools/lib/rbtree.zig`, the dedicated slice note at `Documentation/zigux/phase7-rbtree-slice.md`, the direct-anchor note, the dedicated parity checker at `scripts/zigux/check-phase7-rbtree-parity.py`, the dedicated replay at `zigux/tests/phase7_rbtree.zig`, and the returned survey and manifest, so same-lane truthfulness must keep those returned surfaces explicit while still not presenting the roadmap-path port or fixture pair as returned on current master");
    try expectSliceContains(manifest.ownership_focus, "path truthfulness must keep the currently returned helper rooted at `tools/lib/rbtree.zig` explicit while the roadmap destination `lib/rbtree.zig` still remains a repo-reality gap on current master");
    try expectSliceContains(manifest.ownership_focus, "cross-helper truthfulness must keep the landed string_helpers packet explicit while keeping the cmdline, argv_split, and rbtree packets distinct instead of collapsing them into one shared reminder claim");
    try expectSliceContains(manifest.ownership_focus, "build-graph truthfulness must keep the split non-owner evidence explicit: `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` are readable, while the roadmap-path port and dedicated fixture pair still do not directly materialize on current master");
    try expectSliceContains(manifest.ownership_focus, "build-surface provenance must stay explicit: in this runtime `zigux/tests/phase7_build.zig` only rematerialized through public blob/raw fallback after the authenticated contents bridge returned `404`, while `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/Makefile`, and the helper-local rbtree packet still came back through authenticated rereads");
    try expectSliceContains(manifest.ownership_focus, "machine-readable fallback provenance must stay explicit too: `public_fallback_non_owner_paths` currently names only `zigux/tests/phase7_build.zig`, because that shared non-owner surface needed public fallback in this runtime while the other listed shared-control surfaces still rematerialized through authenticated rereads");
    try expectContains(manifest.next_bounded_step, "public-fallback provenance");
    try expectContains(manifest.next_bounded_step, "`kernel-leaf-libraries`");
    try expectContains(manifest.next_bounded_step, "`zigux/tests/phase7_rbtree_survey.zig`");
    try expectContains(manifest.next_bounded_step, "shared non-owner build evidence");
    try expectContains(manifest.next_bounded_step, "without widening beyond the rbtree packet");
    try expectNotContains(manifest.next_bounded_step, "`lib/rbtree.zig`");
    try expectNotContains(manifest.next_bounded_step, "`zigux/tests/fixtures/phase7_rbtree.json`");
    try expectNotContains(manifest.next_bounded_step, "`zigux/tests/phase7_build.zig`");
    try expectNotContains(manifest.next_bounded_step, "`scripts/zigux/validate-phase7.py`");

    try expectContains(direct_anchor_note, "Current direct-readback Phase 7 rbtree helper packet now rematerializes a dedicated helper-local slice note and parity checker on current `master`");
    try expectContains(direct_anchor_note, "`Documentation/zigux/phase7-rbtree-slice.md`");
    try expectContains(direct_anchor_note, "`scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectContains(direct_anchor_note, "Fresh authenticated GitHub reread in this slot directly returned:");
    try expectContains(direct_anchor_note, "Fresh current-master reread in this slot also confirmed these shared non-owner surfaces:");
    try expectContains(direct_anchor_note, "`scripts/zigux/check-phase7-build-wiring.py`");
    try expectContains(direct_anchor_note, "`scripts/zigux/validate-phase7.py`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_build.zig`");
    try expectContains(direct_anchor_note, "`zigux/Makefile`");
    try expectContains(direct_anchor_note, "`.github/workflows/zigux-bootstrap.yml`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_build.zig` needed the public blob and raw GitHub fallback in this slot after the authenticated GitHub contents bridge returned `404` for that path, so keep it explicit as returned shared non-owner build evidence without overstating authenticated whole-file coverage for this one surface.");
    try expectContains(direct_anchor_note, "Fresh authenticated GitHub reread in this slot still returned `404` for these dedicated companion or roadmap-path surfaces:");
    try expectContains(direct_anchor_note, "`lib/rbtree.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree.json`");
    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`");
    try expectContains(direct_anchor_note, "`zigux/Makefile` now returns shared `phase7-validate`");
    try expectContains(direct_anchor_note, "`phase7-rbtree-test:`");
    try expectContains(direct_anchor_note, "still lacks dedicated Phase 7 runtime-helper steps");
    try expectContains(direct_anchor_note, "Keep the current Phase 7 rbtree reminder surface tied to the returned tool-root helper");
    try expectContains(direct_anchor_note, "shared build, validator, and workflow evidence");
    try expectContains(direct_anchor_note, "`string_helpers` remains the Phase 7 fully landed sibling packet");
    try expectContains(direct_anchor_note, "`cmdline` and `argv_split` keep their own helper-local packet ownership");
    try expectContains(direct_anchor_note, "Do not widen this note into dedicated make-wrapper or workflow-recovery claims until a fresh same-lane reread proves one more concrete rbtree companion surface");
}

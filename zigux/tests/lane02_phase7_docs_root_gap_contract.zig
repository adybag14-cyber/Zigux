const std = @import("std");

const max_file_bytes = 1024 * 1024;

const docs_readme = "Documentation/zigux/README.md";
const review_checklist = "Documentation/zigux/review-checklist.md";
const catalog_path = "Documentation/zigux/phase7-leaf-library-evidence-catalog.md";
const shared_checker = "scripts/zigux/check-phase7-shared-surface.py";
const build_checker = "scripts/zigux/check-phase7-build-wiring.py";
const cmdline_checker = "scripts/zigux/check-phase7-cmdline-packet.py";
const build_path = "zigux/tests/phase7_build.zig";
const makefile_path = "zigux/Makefile";
const manifest_path = "zigux/tests/phase7_leaf_library_evidence_manifest.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "docs root and review checklist keep Phase 7 shared packet bounded" {
    const allocator = std.testing.allocator;
    const readme = try readFile(allocator, docs_readme);
    defer allocator.free(readme);
    const checklist = try readFile(allocator, review_checklist);
    defer allocator.free(checklist);

    try expectContains(readme, "Phase 7 notes - `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`");
    try expectContains(readme, "`zigux/tests/phase7_build.zig` keeps `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` wired through the dedicated helper, survey, sample-boundary, and format-boundary routes plus the shared `test` step");
    try expectContains(readme, "`zigux/Makefile` keeps only the narrow `make -C zigux phase7-validate` foothold explicit and leaves broader wrapper routes outside this packet");
    try expectContains(readme, "`python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `python3 scripts/zigux/validate-phase7.py`, and `make -C zigux phase7-validate` replay the bounded current Phase 7 docs-root reminder packet");
    try expectMissing(readme, "`python3 scripts/zigux/check-phase7-cmdline-packet.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`");

    try expectContains(checklist, "if the change touches the shared Phase 7 leaf-library packet");
    try expectContains(checklist, "`scripts/zigux/check-phase7-shared-surface.py`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `scripts/zigux/validate-phase7.py`");
    try expectContains(checklist, "`zigux/tests/phase7_leaf_library_evidence_manifest.json`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, and `lib/rbtree.zig`");
    try expectContains(checklist, "keep broader wrapper families or deeper runtime validation claims out of the Phase 7 reminder packet");
    try expectMissing(checklist, "`scripts/zigux/check-phase7-cmdline-packet.py`, `scripts/zigux/check-phase7-argv-split-packet.py`");
}

test "catalog manifest and checker record the shipped cmdline guard gap" {
    const allocator = std.testing.allocator;
    const catalog = try readFile(allocator, catalog_path);
    defer allocator.free(catalog);
    const manifest = try readFile(allocator, manifest_path);
    defer allocator.free(manifest);
    const checker = try readFile(allocator, shared_checker);
    defer allocator.free(checker);
    const cmdline = try readFile(allocator, cmdline_checker);
    defer allocator.free(cmdline);

    try expectContains(catalog, "## Current repo-reality gaps");
    try expectContains(catalog, "shared `Documentation/zigux/README.md` Phase 7 reminder text still omits the shipped `scripts/zigux/check-phase7-cmdline-packet.py` guard from the shared packet inventory");
    try expectContains(catalog, "shared `Documentation/zigux/review-checklist.md` Phase 7 reminder text still omits the shipped `scripts/zigux/check-phase7-cmdline-packet.py` guard from the shared packet inventory");
    try expectContains(catalog, "shared `scripts/zigux/README.md` and `zigux/tests/README.md` Phase 7 reminder text still omits the shipped `scripts/zigux/check-phase7-cmdline-packet.py` guard from the shared packet inventory");
    try expectContains(catalog, "do not widen this packet into new helper semantics, workflow recovery claims, or deeper runtime-family validation routes");

    try expectContains(manifest, "\"packet\": \"phase7-leaf-library-evidence\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase7-cmdline-packet.py\"");
    try expectContains(manifest, "\"python3 scripts/zigux/check-phase7-cmdline-packet.py\"");
    try expectContains(manifest, "shared `scripts/zigux/README.md` and `zigux/tests/README.md` Phase 7 reminder text still omits the shipped `scripts/zigux/check-phase7-cmdline-packet.py` guard from the shared packet inventory");

    try expectContains(checker, "CMDLINE_PACKET_CHECKER_PATH = Path(\"scripts/zigux/check-phase7-cmdline-packet.py\")");
    try expectContains(checker, "run_checker(root, CMDLINE_PACKET_CHECKER_PATH)");
    try expectContains(cmdline, "PHASE7_CMDLINE_PACKET=pass");
    try expectContains(cmdline, "EXPECTED_MANIFEST_LANE_KEY = \"P7-L08\"");
    try expectContains(cmdline, "helper-local survey-manifest-checker truthfulness packet");
}

test "build wiring and Makefile keep narrow Phase 7 route boundary" {
    const allocator = std.testing.allocator;
    const build = try readFile(allocator, build_path);
    defer allocator.free(build);
    const makefile = try readFile(allocator, makefile_path);
    defer allocator.free(makefile);
    const build_check = try readFile(allocator, build_checker);
    defer allocator.free(build_check);

    try expectContains(build, "../../lib/string_helpers.zig");
    try expectContains(build, "../../lib/cmdline.zig");
    try expectContains(build, "../../lib/argv_split.zig");
    try expectContains(build, "../../lib/rbtree.zig");
    try expectContains(build, "phase7-string-helpers-format-boundary");
    try expectContains(build, "phase7-cmdline-survey");
    try expectContains(build, "phase7-argv-split-survey");
    try expectContains(build, "phase7-rbtree-test");
    try expectContains(build, "phase7-rbtree-survey");
    try expectContains(build, "test_step.dependOn(&run_string_helpers_format_boundary_tests.step)");
    try expectContains(build, "test_step.dependOn(&run_rbtree_survey_tests.step)");

    try expectContains(makefile, "phase7-validate:");
    try expectContains(makefile, "scripts/zigux/validate-phase7.py --self-test");
    try expectContains(makefile, "scripts/zigux/validate-phase7.py");
    try expectMissing(makefile, "\nphase7-test:");
    try expectMissing(makefile, "\nphase7:");

    try expectContains(build_check, "phase7 build-wiring evidence drift");
    try expectContains(build_check, "phase7 build marker missing: ../../lib/rbtree.zig");
    try expectContains(build_check, "phase7 build marker missing: phase7-rbtree-test");
    try expectContains(build_check, "FORBIDDEN_MAKEFILE_MARKERS");
}

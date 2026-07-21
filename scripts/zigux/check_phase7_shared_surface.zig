const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE7_SHARED_SURFACE=pass";
pub const self_test_pass_marker = "PHASE7_SHARED_SURFACE_SELF_TEST=pass";

const EXPECTED_PACKET = [_][]const u8{
    "phase7-leaf-library-evidence",
};

const EXPECTED_SCOPE = [_][]const u8{
    "shared leaf-library evidence rows and validation foothold only",
};

const EXPECTED_COMPANIONS = [_][]const u8{
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts\\zigux/check_phase7_shared_surface.zig",
    "scripts\\zigux/check_phase7_build_wiring.zig",
    "scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "scripts\\zigux/check_phase7_cmdline_packet.zig",
    "scripts\\zigux/check_phase7_argv_split_packet.zig",
    "scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "scripts\\zigux/check_phase7_rbtree_parity.zig",
    "scripts\\zigux/validate_phase7.zig",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
};

const EXPECTED_ROADMAP_ANCHORS = [_][]const u8{
    "lib/string_helpers.c",
    "lib/cmdline.c",
    "lib/argv_split.c",
    "lib/rbtree.c",
};

const EXPECTED_GAPS = [_][]const u8{
    "shared `scripts/zigux/README.md` and `zigux/tests/README.md` Phase 7 reminder text still omits the shipped `scripts\\zigux/check_phase7_cmdline_packet.zig` guard from the shared packet inventory",
};

const EXPECTED_REPLAYS = [_][]const u8{
    "zig run scripts/zigux/check_phase7_shared_surface.zig",
    "zig run scripts/zigux/check_phase7_shared_surface.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_build_wiring.zig",
    "zig run scripts/zigux/check_phase7_build_wiring.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig",
    "zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_cmdline_packet.zig",
    "zig run scripts/zigux/check_phase7_cmdline_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_argv_split_packet.zig",
    "zig run scripts/zigux/check_phase7_argv_split_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig",
    "zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase7_rbtree_parity.zig",
    "zig run scripts/zigux/check_phase7_rbtree_parity.zig -- --self-test",
    "zig run scripts/zigux/validate_phase7.zig",
    "zig run scripts/zigux/validate_phase7.zig -- --self-test",
    "make -C zigux phase7-validate",
};

const REQUIRED_CATALOG_SNIPPETS = [_][]const u8{
    "## Current direct-readback companions",
    "- `Documentation/zigux/README.md`",
    "- `Documentation/zigux/review-checklist.md`",
    "- `scripts\\zigux/check_phase7_build_wiring.zig`",
    "- `scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig`",
    "- `scripts\\zigux/check_phase7_cmdline_packet.zig`",
    "- `scripts\\zigux/check_phase7_argv_split_packet.zig`",
    "- `scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig`",
    "- `scripts\\zigux/check_phase7_rbtree_parity.zig`",
    "- `scripts/zigux/README.md`",
    "- `zigux/tests/README.md`",
    "- `zigux/tests/phase7_build.zig`",
    "- `lib/rbtree.zig`",
    "## Current replay inventory",
    "- `zig run scripts/zigux/check_phase7_build_wiring.zig`",
    "- `zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig`",
    "- `zig run scripts/zigux/check_phase7_cmdline_packet.zig`",
    "- `zig run scripts/zigux/check_phase7_argv_split_packet.zig`",
    "- `zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig`",
    "- `zig run scripts/zigux/check_phase7_rbtree_parity.zig`",
    "- `make -C zigux phase7-validate`",
    "## Current build-wiring evidence",
    "- `zigux/tests/phase7_build.zig` wires `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` into the shared Phase 7 build graph.",
    "- `zigux/tests/phase7_build.zig` still exposes the dedicated helper, survey, sample-boundary, and format-boundary routes through `phase7-string-helpers-test`, `phase7-string-helpers-survey`, `phase7-string-helpers-sample-boundary`, `phase7-string-helpers-format-boundary`, `phase7-cmdline-test`, `phase7-cmdline-survey`, `phase7-argv-split-test`, `phase7-argv-split-survey`, `phase7-rbtree-test`, and `phase7-rbtree-survey`.",
    "- `zigux/tests/phase7_build.zig` keeps the shared `test` build step aggregating every helper, survey, sample-boundary, and format-boundary replay through the current `test_step.dependOn(...)` handoff list.",
    "- `zigux/Makefile` keeps the narrow `phase7-validate` foothold explicit while broader wrapper routes remain outside this packet.",
    "## Current repo-reality gaps",
    "- shared `Documentation/zigux/README.md` Phase 7 reminder text still omits the shipped `scripts\\zigux/check_phase7_cmdline_packet.zig` guard from the shared packet inventory",
    "- shared `Documentation/zigux/review-checklist.md` Phase 7 reminder text still omits the shipped `scripts\\zigux/check_phase7_cmdline_packet.zig` guard from the shared packet inventory",
};

const REQUIRED_DOCS_README_SNIPPETS = [_][]const u8{
    "Phase 7 notes - `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`",
    "* `zigux/tests/phase7_build.zig` keeps `../../lib/string_helpers.zig`, `../../lib/cmdline.zig`, `../../lib/argv_split.zig`, and `../../lib/rbtree.zig` wired through the dedicated helper, survey, sample-boundary, and format-boundary routes plus the shared `test` step, while `zigux/Makefile` keeps only the narrow `make -C zigux phase7-validate` foothold explicit and leaves broader wrapper routes outside this packet.",
    "* `zig run scripts/zigux/check_phase7_shared_surface.zig`, `zig run scripts/zigux/check_phase7_build_wiring.zig`, `zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig`, `zig run scripts/zigux/check_phase7_argv_split_packet.zig`, `zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig`, `zig run scripts/zigux/validate_phase7.zig`, and `make -C zigux phase7-validate` replay the bounded current Phase 7 docs-root reminder packet without widening it into new helper semantics, workflow recovery claims, or deeper runtime-family validation routes.",
};

const REQUIRED_REVIEW_CHECKLIST_SNIPPETS = [_][]const u8{
    "* if the change touches the shared Phase 7 leaf-library packet, do `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts\\zigux/check_phase7_shared_surface.zig`, `scripts\\zigux/check_phase7_build_wiring.zig`, `scripts\\zigux/check_phase7_make_wrapper_selftest_alignment.zig`, `scripts\\zigux/check_phase7_argv_split_packet.zig`, `scripts\\zigux/check_phase7_string_helpers_format_boundary_packet.zig`, `scripts\\zigux/validate_phase7.zig`, `zigux/tests/phase7_leaf_library_evidence_manifest.json`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, and `lib/rbtree.zig` still agree on the current bounded Phase 7 packet, keep the returned helper-anchor set and shared build-wiring packet explicit, keep `zig run scripts/zigux/check_phase7_shared_surface.zig`, `zig run scripts/zigux/check_phase7_build_wiring.zig`, `zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig`, `zig run scripts/zigux/check_phase7_argv_split_packet.zig`, `zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig`, `zig run scripts/zigux/validate_phase7.zig`, and `make -C zigux phase7-validate` explicit as the current bounded replay surfaces, and keep broader wrapper families or deeper runtime validation claims out of the Phase 7 reminder packet?",
};

const REQUIRED_SCRIPTS_README_SNIPPETS = [_][]const u8{
    "- Phase 7 flow - the current scripts-root leaf-library packet stays reviewable through the returned leaf-library evidence catalog, the shared docs-root and tests-root reminder packet, the shipped shared-surface, build-wiring, make-wrapper self-test alignment, dedicated `cmdline`, `argv_split`, `string_helpers` format-boundary, and `rbtree` parity guards, the validator entrypoint, the shared machine-readable manifest, the shared build graph, the narrow `phase7-validate` wrapper foothold, and the four roadmap-backed helper anchors instead of reopening helper semantics or reconstructing a broader missing-wrapper story",
    "- `zig run scripts/zigux/check_phase7_shared_surface.zig -- --self-test`, `zig run scripts/zigux/check_phase7_build_wiring.zig -- --self-test`, `zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig -- --self-test`, `zig run scripts/zigux/check_phase7_cmdline_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase7_argv_split_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase7_rbtree_parity.zig -- --self-test`, and `zig run scripts/zigux/validate_phase7.zig -- --self-test` replay the shipped shared Phase 7 scripts-root reminder guards",
};

const REQUIRED_TESTS_README_SNIPPETS = [_][]const u8{
    "## Phase 7 leaf-library packet",
    "Keep the validator-first reminder packet explicit too: `zig run scripts/zigux/check_phase7_shared_surface.zig`, `zig run scripts/zigux/check_phase7_build_wiring.zig`, `zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig`, `zig run scripts/zigux/check_phase7_cmdline_packet.zig`, `zig run scripts/zigux/check_phase7_argv_split_packet.zig`, `zig run scripts/zigux/check_phase7_string_helpers_format_boundary_packet.zig`, `zig run scripts/zigux/check_phase7_rbtree_parity.zig`, `zig run scripts/zigux/check_phase7_rbtree_parity.zig -- --self-test`, `zig run scripts/zigux/validate_phase7.zig`, `zig run scripts/zigux/validate_phase7.zig -- --self-test`, and `make -C zigux phase7-validate` remain the shipped bounded replay surfaces, while `zigux/Makefile` keeps `phase7-validate` as the shared foothold and `phase7-rbtree-test:` plus `phase7-rbtree-survey:` as dedicated helper-local wrappers rather than a broader aggregate wrapper family.",
};

const REQUIRED_MAKEFILE_SNIPPETS = [_][]const u8{
    "phase7-validate:",
    "$(ZIG) run scripts/zigux/validate_phase7.zig",
};

const REQUIRED_BUILD_SNIPPETS = [_][]const u8{
    "../../lib/rbtree.zig",
    "phase7-string-helpers-format-boundary",
    "string_helpers_format_boundary_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
    "phase7-rbtree-test",
    "phase7-rbtree-survey",
    "const test_step = b.step(\"test\", \"Run the Phase 7 runtime helper tests\");",
    "test_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
};

const EXPECTED_HELPERS = [_][]const u8{
    "(string_helpers",
    "lib/string_helpers.zig",
    "pub const STRING_UNITS_10pub const KasprintfStrarrayResultpub fn kstrdupQuotablepub fn kstrdupQuotableCmdline",
    ")",
    "(string_helpers_parse_int_array",
    "lib/string_helpers.zig",
    "pub const ParseIntArrayErrorpub fn parseIntArray",
    ")",
    "(cmdline",
    "lib/cmdline.zig",
    "pub fn parseOptionStrpub fn getOption)",
    "(argv_split",
    "lib/argv_split.zig",
    "pub const ArgvSplitResultpub fn argvSplit)",
    "(rbtree",
    "lib/rbtree.zig",
    "pub const Node = structpub const RootCached = structpub fn add(pub fn rb_find_add_cached(",
    ")",
};

const EXPECTED_BUILD_WIRING_EVIDENCE = [_][]const u8{
    "{path:zigux/tests/phase7_build.zig",
    "expected_markers:../../lib/string_helpers.zig../../lib/cmdline.zig../../lib/argv_split.zig../../lib/rbtree.zigphase7-string-helpers-testphase7-string-helpers-surveyphase7-string-helpers-sample-boundaryphase7-string-helpers-format-boundarystring_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step)string_helpers_format_boundary_step.dependOn(&run_string_helpers_format_boundary_tests.step)phase7-cmdline-testphase7-cmdline-surveycmdline_survey_step.dependOn(&run_cmdline_survey_tests.step)phase7-argv-split-testphase7-argv-split-surveyargv_split_survey_step.dependOn(&run_argv_split_survey_tests.step)phase7-rbtree-testphase7-rbtree-surveyconst test_step = b.step(\"test\", \"Run the Phase 7 runtime helper tests\");test_step.dependOn(&run_string_helpers_tests.step)test_step.dependOn(&run_string_helpers_survey_tests.step)test_step.dependOn(&run_string_helpers_sample_boundary_tests.step)test_step.dependOn(&run_string_helpers_format_boundary_tests.step)test_step.dependOn(&run_cmdline_tests.step)test_step.dependOn(&run_cmdline_survey_tests.step)test_step.dependOn(&run_argv_split_tests.step)test_step.dependOn(&run_argv_split_survey_tests.step)test_step.dependOn(&run_rbtree_tests.step)test_step.dependOn(&run_rbtree_survey_tests.step)",
    "}",
    "{path:zigux/Makefile",
    "expected_markers:phase7-validate:$(ZIG) run scripts/zigux/validate_phase7.zig -- --self-test$(ZIG) run scripts/zigux/validate_phase7.zig",
    "}",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_packet_path);
    const text_expected_packet = try guard.readUtf8File(io, allocator, text_expected_packet_path);
    defer allocator.free(text_expected_packet);
    for (EXPECTED_PACKET) |marker| try guard.requireMarker(text_expected_packet, marker);
    const text_expected_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_scope_path);
    const text_expected_scope = try guard.readUtf8File(io, allocator, text_expected_scope_path);
    defer allocator.free(text_expected_scope);
    for (EXPECTED_SCOPE) |marker| try guard.requireMarker(text_expected_scope, marker);
    const text_expected_companions_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_companions_path);
    const text_expected_companions = try guard.readUtf8File(io, allocator, text_expected_companions_path);
    defer allocator.free(text_expected_companions);
    for (EXPECTED_COMPANIONS) |marker| try guard.requireMarker(text_expected_companions, marker);
    const text_expected_roadmap_anchors_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_roadmap_anchors_path);
    const text_expected_roadmap_anchors = try guard.readUtf8File(io, allocator, text_expected_roadmap_anchors_path);
    defer allocator.free(text_expected_roadmap_anchors);
    for (EXPECTED_ROADMAP_ANCHORS) |marker| try guard.requireMarker(text_expected_roadmap_anchors, marker);
    const text_expected_gaps_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_gaps_path);
    const text_expected_gaps = try guard.readUtf8File(io, allocator, text_expected_gaps_path);
    defer allocator.free(text_expected_gaps);
    for (EXPECTED_GAPS) |marker| try guard.requireMarker(text_expected_gaps, marker);
    const text_expected_replays_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_expected_replays_path);
    const text_expected_replays = try guard.readUtf8File(io, allocator, text_expected_replays_path);
    defer allocator.free(text_expected_replays);
    for (EXPECTED_REPLAYS) |marker| try guard.requireMarker(text_expected_replays, marker);
    const text_required_catalog_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_required_catalog_snippets_path);
    const text_required_catalog_snippets = try guard.readUtf8File(io, allocator, text_required_catalog_snippets_path);
    defer allocator.free(text_required_catalog_snippets);
    for (REQUIRED_CATALOG_SNIPPETS) |marker| try guard.requireMarker(text_required_catalog_snippets, marker);
    const text_required_docs_readme_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_required_docs_readme_snippets_path);
    const text_required_docs_readme_snippets = try guard.readUtf8File(io, allocator, text_required_docs_readme_snippets_path);
    defer allocator.free(text_required_docs_readme_snippets);
    for (REQUIRED_DOCS_README_SNIPPETS) |marker| try guard.requireMarker(text_required_docs_readme_snippets, marker);
    const text_required_review_checklist_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_required_review_checklist_snippets_path);
    const text_required_review_checklist_snippets = try guard.readUtf8File(io, allocator, text_required_review_checklist_snippets_path);
    defer allocator.free(text_required_review_checklist_snippets);
    for (REQUIRED_REVIEW_CHECKLIST_SNIPPETS) |marker| try guard.requireMarker(text_required_review_checklist_snippets, marker);
    const text_required_scripts_readme_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_required_scripts_readme_snippets_path);
    const text_required_scripts_readme_snippets = try guard.readUtf8File(io, allocator, text_required_scripts_readme_snippets_path);
    defer allocator.free(text_required_scripts_readme_snippets);
    for (REQUIRED_SCRIPTS_README_SNIPPETS) |marker| try guard.requireMarker(text_required_scripts_readme_snippets, marker);
    const text_required_tests_readme_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_required_tests_readme_snippets_path);
    const text_required_tests_readme_snippets = try guard.readUtf8File(io, allocator, text_required_tests_readme_snippets_path);
    defer allocator.free(text_required_tests_readme_snippets);
    for (REQUIRED_TESTS_README_SNIPPETS) |marker| try guard.requireMarker(text_required_tests_readme_snippets, marker);
    const text_required_makefile_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_required_makefile_snippets_path);
    const text_required_makefile_snippets = try guard.readUtf8File(io, allocator, text_required_makefile_snippets_path);
    defer allocator.free(text_required_makefile_snippets);
    for (REQUIRED_MAKEFILE_SNIPPETS) |marker| try guard.requireMarker(text_required_makefile_snippets, marker);
    const text_required_build_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase7-leaf-library-evidence-catalog.md");
    defer allocator.free(text_required_build_snippets_path);
    const text_required_build_snippets = try guard.readUtf8File(io, allocator, text_required_build_snippets_path);
    defer allocator.free(text_required_build_snippets);
    for (REQUIRED_BUILD_SNIPPETS) |marker| try guard.requireMarker(text_required_build_snippets, marker);
    const text_expected_helpers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_helpers_path);
    const text_expected_helpers = try guard.readUtf8File(io, allocator, text_expected_helpers_path);
    defer allocator.free(text_expected_helpers);
    for (EXPECTED_HELPERS) |marker| try guard.requireMarker(text_expected_helpers, marker);
    const text_expected_build_wiring_evidence_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_build_wiring_evidence_path);
    const text_expected_build_wiring_evidence = try guard.readUtf8File(io, allocator, text_expected_build_wiring_evidence_path);
    defer allocator.free(text_expected_build_wiring_evidence);
    for (EXPECTED_BUILD_WIRING_EVIDENCE) |marker| try guard.requireMarker(text_expected_build_wiring_evidence, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_SHARED_SURFACE=pass";
pub const self_test_pass_marker = "PHASE6_SHARED_SURFACE_SELF_TEST=pass";

const EXPECTED_EVIDENCE_PACKET = [_][]const u8{
    "phase6-helper-evidence",
};

const EXPECTED_PARITY_PACKET = [_][]const u8{
    "phase6-helper-parity",
};

const EXPECTED_EVIDENCE_SURVEYED_HEAD = [_][]const u8{
    "current-master-readback-2026-05-22",
};

const EXPECTED_EVIDENCE_LANE_SCOPE = [_][]const u8{
    "shared helper-evidence rows and machine-readable manifest only",
};

const EXPECTED_PARITY_SURVEYED_HEAD = [_][]const u8{
    "current-master-readback-2026-05-22",
};

const EXPECTED_PARITY_LANE_SCOPE = [_][]const u8{
    "shared helper-parity rows and machine-readable manifest only",
};

const EXPECTED_PARITY_PURPOSE = [_][]const u8{
    "Record the current directly readable Phase 6 helper-parity packet without overstating missing shared reminder, checker, or perf-note surfaces as returned evidence.",
};

const EXPECTED_EVIDENCE_DIRECT_COMPANIONS = [_][]const u8{
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-hexdump-perf-refresh.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts\\zigux/check_phase6_present_entrypoints.zig",
    "scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig",
    "scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig",
    "scripts\\zigux/check_phase6_perf_threshold_markers.zig",
    "scripts\\zigux/check_phase6_hexdump_packet.zig",
    "scripts\\zigux/check_phase6_hexdump_route.zig",
};

const EXPECTED_PARITY_DIRECT_EVIDENCE = [_][]const u8{
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts\\zigux/check_phase6_shared_surface.zig",
    "scripts\\zigux/check_phase6_present_entrypoints.zig",
    "scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig",
    "scripts\\zigux/validate_phase6.zig",
    "scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig",
    "scripts\\zigux/check_phase6_perf_threshold_markers.zig",
    "scripts\\zigux/check_phase6_hexdump_packet.zig",
    "scripts\\zigux/check_phase6_hexdump_route.zig",
};

const EXPECTED_ROADMAP_ANCHORS = [_][]const u8{
    "lib/base64.c",
    "lib/bsearch.c",
    "lib/checksum.c",
    "lib/hexdump.c",
};

const EXPECTED_HELPER_KEYS = [_][]const u8{
    "base64",
    "bsearch",
    "checksum",
    "hexdump",
};

const EXPECTED_SHARED_REPLAY_INVENTORY = [_][]const u8{
    "zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-test",
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "zig run scripts\\zigux/check_phase6_base64_c_parity.zig",
    "zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-test",
    "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-perf",
    "zig run scripts\\zigux/check_phase6_bsearch_c_parity.zig",
    "zig run scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig",
    "zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-test",
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "zig run scripts\\zigux/check_phase6_checksum_c_parity.zig",
    "zig run scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig",
    "zig run scripts\\zigux/check_phase6_perf_threshold_markers.zig",
    "zig run scripts\\zigux/check_phase6_hexdump_packet.zig",
    "zig run scripts\\zigux/check_phase6_hexdump_route.zig",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
};

const REQUIRED_DOCS_README_SNIPPETS = [_][]const u8{
    "Phase 6 notes - `Documentation/zigux/phase6-helper-evidence-catalog.md` - `Documentation/zigux/phase6-helper-parity-catalog.md` - `Documentation/zigux/phase6-perf-gate-survey.md` - `Documentation/zigux/review-checklist.md` - `scripts/zigux/README.md` - `zigux/tests/README.md` - `zigux/tests/phase6_build.zig` - `zigux/tests/phase6_helper_evidence_manifest.json` - `zigux/tests/phase6_helper_parity_manifest.json` - `scripts\\zigux/check_phase6_shared_surface.zig` - `scripts\\zigux/check_phase6_present_entrypoints.zig` - `zigux/Makefile` keep the bounded Phase 6 docs-root packet explicit through the shared helper-evidence and helper-parity catalogs, the current scripts-root and tests-root reminders, the shared build foothold, the shared machine-readable manifests, the present-entrypoint guard, and the returned Makefile wrapper surface instead of leaving the active leaf-helper tranche implicit from neighboring reminder surfaces alone.",
    "authenticated current-master rereads now directly recover both `Documentation/zigux/phase6-helper-parity-catalog.md` and `Documentation/zigux/phase6-perf-gate-survey.md`, so keep both note surfaces inside the current docs-root evidence packet beside the shared manifests instead of framing the broader perf-note surface as public-tree-backed companion evidence.",
    "current `master` directly serves the four roadmap-backed helper anchors through `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig`, their focused `zigux/tests/phase6_*` helper and perf replays, the restored `zigux/tests/phase6_build.zig` foothold, and the current `zigux/Makefile` wrapper family, so keep the docs-root reminder reviewable through that returned helper-evidence packet instead of restating helper-local semantics here.",
};

const REQUIRED_SCRIPTS_README_SNIPPETS = [_][]const u8{
    "- authenticated current-master rereads now directly recover both `Documentation/zigux/phase6-helper-parity-catalog.md` and `Documentation/zigux/phase6-perf-gate-survey.md`, so keep both note surfaces inside the current directly readable shared packet beside the shared manifests instead of treating the broader perf reminder path as public-tree-backed companion evidence",
    "- the shared replay inventory now treats `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-base64-perf`, `zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig`, and `make -C zigux phase6-bsearch-perf`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, and `make -C zigux phase6-checksum-perf` as committed rerun routes beside the existing hexdump reminders, so keep those wrappers out of the older inventory-only bucket",
};

const REQUIRED_EVIDENCE_CATALOG_SNIPPETS = [_][]const u8{
    "Authenticated current-master rereads now directly recover `Documentation/zigux/phase6-perf-gate-survey.md`, and that broader perf note is now aligned again on the currently readable base64, bsearch, checksum, and hexdump measurement packet.",
    "The directly readable shared packet in this environment is therefore this helper-evidence catalog together with `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, `Documentation/zigux/phase6-hexdump-slice.md`, `Documentation/zigux/phase6-hexdump-perf-refresh.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/README.md`, `zigux/Makefile`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts\\zigux/check_phase6_present_entrypoints.zig`, `scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig`, `scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig`, `scripts\\zigux/check_phase6_perf_threshold_markers.zig`, `scripts\\zigux/check_phase6_hexdump_packet.zig`, and `scripts\\zigux/check_phase6_hexdump_route.zig`.",
    "The docs-root README now keeps a dedicated Phase 6 helper-evidence stanza aligned with surveyed head `current-master-readback-2026-05-22`, so keep `Documentation/zigux/README.md` inside the current direct-readback packet rather than treating it as a remaining shared-note follow-through gap.",
    "- `zig run scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig`",
    "- `zig run scripts\\zigux/check_phase6_perf_threshold_markers.zig`",
};

const REQUIRED_PARITY_CATALOG_SNIPPETS = [_][]const u8{
    "- direct helper-evidence companion: `Documentation/zigux/phase6-helper-evidence-catalog.md`",
    "- helper-evidence row: `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `zigux/tests/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `scripts\\zigux/check_phase6_base64_corpus_determinism.zig`, `scripts\\zigux/check_phase6_base64_c_parity.zig`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`",
    "- current posture: direct helper readback is restored for the helper, focused replay, perf replay, fixture surface, dedicated corpus checker, direct C parity runner, direct C parity harness, direct C parity vectors companion, direct C parity casegen companion, direct C parity checker, and slice note. A targeted authenticated current-master reread on 2026-05-27 directly recovered `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`, so the base64 row no longer carries a known generator-side direct-readback gap.",
    "- current posture: direct helper readback is restored for the helper, focused replay, fixture-owned perf packet, direct C parity runner, direct C parity harness, direct C parity checker, and slice note, so the checksum row now ships the same external parity review hook as the other portability-sensitive Phase 6 helpers without reopening hexdump work",
    "Treat this file as the broader parity companion for the current helper-evidence packet rather than as a substitute for the directly readable shared packet in `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts\\zigux/check_phase6_shared_surface.zig`, `scripts\\zigux/check_phase6_present_entrypoints.zig`, `scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig`, `scripts\\zigux/validate_phase6.zig`, `scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig`, `scripts\\zigux/check_phase6_perf_threshold_markers.zig`, `scripts\\zigux/check_phase6_hexdump_packet.zig`, `scripts\\zigux/check_phase6_hexdump_route.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `Documentation/zigux/phase6-perf-gate-survey.md`.",
    "Authenticated follow-up readback on 2026-05-22 directly recovered `Documentation/zigux/phase6-perf-gate-survey.md` and `scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig` again, so broader reminder surfaces can keep the shared survey plus the base64-bsearch, checksum-hexdump, and perf-threshold guard surfaces inside the directly readable shared packet instead of treating any of those guards as fallback-only evidence.",
};

const REQUIRED_VALIDATOR_SNIPPETS = [_][]const u8{
    "HELPER_EVIDENCE_MANIFEST = Path(\"zigux/tests/phase6_helper_evidence_manifest.json\")",
    "HELPER_PARITY_MANIFEST = Path(\"zigux/tests/phase6_helper_parity_manifest.json\")",
    "run_checker(root, SHARED_SURFACE_CHECKER, \"--repo-root\")",
    "run_checker(root, PRESENT_ENTRYPOINTS_CHECKER, \"--repo-root\")",
};

const REQUIRED_PARITY_COVERAGE_NOTE_SNIPPETS = [_][]const u8{
    "Authenticated GitHub contents readback on 2026-05-20 reconfirmed direct access to Documentation/zigux/phase6-helper-evidence-catalog.md, Documentation/zigux/phase6-helper-parity-catalog.md, Documentation/zigux/phase6-hexdump-slice.md, Documentation/zigux/phase6-hexdump-perf-refresh.md, scripts\\zigux/check_phase6_shared_surface.zig, scripts\\zigux/validate_phase6.zig, and zigux/tests/phase6_build.zig.",
    "A follow-up authenticated current-master readback on 2026-05-21 also directly recovered Documentation/zigux/phase6-perf-gate-survey.md, zigux/tests/phase6_helper_parity_manifest.json, zigux/tests/phase6_helper_evidence_manifest.json, and scripts\\zigux/check_phase6_perf_threshold_markers.zig.",
    "A later authenticated current-master readback on 2026-05-22 directly recovered zigux/tests/phase6_base64_c_parity.zig, zigux/tests/fixtures/phase6_base64_c_harness.c, and scripts\\zigux/check_phase6_base64_c_parity.zig.",
    "A targeted authenticated current-master reread on 2026-05-27 also directly recovered zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig and zigux/tests/phase6_base64_c_casegen.zig, so the base64 helper row no longer carries a known generator-side direct-readback gap.",
};

const REQUIRED_PARITY_PERF_NOTE_SNIPPETS = [_][]const u8{
    "Verified the current Phase 6 perf packet on 2026-05-20 from direct current-master readback of zigux/tests/phase6_base64_perf.zig, zigux/tests/fixtures/phase6_base64_vectors.zig, zigux/tests/phase6_bsearch.zig, zigux/tests/phase6_bsearch_perf.zig, zigux/tests/phase6_bsearch_lower_bound_c_abi.zig, zigux/tests/phase6_bsearch_c_abi_budget.zig, zigux/tests/fixtures/phase6_bsearch_vectors.zig, zigux/tests/phase6_checksum_perf.zig, zigux/tests/fixtures/phase6_checksum_vectors.zig, zigux/tests/phase6_hexdump_perf.zig, zigux/tests/phase6_hexdump_perf_matrix.zig, zigux/tests/fixtures/phase6_hexdump_vectors.zig, Documentation/zigux/phase6-hexdump-slice.md, Documentation/zigux/phase6-hexdump-perf-refresh.md, zigux/tests/phase6_build.zig, and zigux/Makefile.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_evidence_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_evidence_packet_path);
    const text_expected_evidence_packet = try guard.readUtf8File(io, allocator, text_expected_evidence_packet_path);
    defer allocator.free(text_expected_evidence_packet);
    for (EXPECTED_EVIDENCE_PACKET) |marker| try guard.requireMarker(text_expected_evidence_packet, marker);
    const text_expected_parity_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_parity_packet_path);
    const text_expected_parity_packet = try guard.readUtf8File(io, allocator, text_expected_parity_packet_path);
    defer allocator.free(text_expected_parity_packet);
    for (EXPECTED_PARITY_PACKET) |marker| try guard.requireMarker(text_expected_parity_packet, marker);
    const text_expected_evidence_surveyed_head_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_evidence_surveyed_head_path);
    const text_expected_evidence_surveyed_head = try guard.readUtf8File(io, allocator, text_expected_evidence_surveyed_head_path);
    defer allocator.free(text_expected_evidence_surveyed_head);
    for (EXPECTED_EVIDENCE_SURVEYED_HEAD) |marker| try guard.requireMarker(text_expected_evidence_surveyed_head, marker);
    const text_expected_evidence_lane_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_evidence_lane_scope_path);
    const text_expected_evidence_lane_scope = try guard.readUtf8File(io, allocator, text_expected_evidence_lane_scope_path);
    defer allocator.free(text_expected_evidence_lane_scope);
    for (EXPECTED_EVIDENCE_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_evidence_lane_scope, marker);
    const text_expected_parity_surveyed_head_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_parity_surveyed_head_path);
    const text_expected_parity_surveyed_head = try guard.readUtf8File(io, allocator, text_expected_parity_surveyed_head_path);
    defer allocator.free(text_expected_parity_surveyed_head);
    for (EXPECTED_PARITY_SURVEYED_HEAD) |marker| try guard.requireMarker(text_expected_parity_surveyed_head, marker);
    const text_expected_parity_lane_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_parity_lane_scope_path);
    const text_expected_parity_lane_scope = try guard.readUtf8File(io, allocator, text_expected_parity_lane_scope_path);
    defer allocator.free(text_expected_parity_lane_scope);
    for (EXPECTED_PARITY_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_parity_lane_scope, marker);
    const text_expected_parity_purpose_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_parity_purpose_path);
    const text_expected_parity_purpose = try guard.readUtf8File(io, allocator, text_expected_parity_purpose_path);
    defer allocator.free(text_expected_parity_purpose);
    for (EXPECTED_PARITY_PURPOSE) |marker| try guard.requireMarker(text_expected_parity_purpose, marker);
    const text_expected_evidence_direct_companions_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_evidence_direct_companions_path);
    const text_expected_evidence_direct_companions = try guard.readUtf8File(io, allocator, text_expected_evidence_direct_companions_path);
    defer allocator.free(text_expected_evidence_direct_companions);
    for (EXPECTED_EVIDENCE_DIRECT_COMPANIONS) |marker| try guard.requireMarker(text_expected_evidence_direct_companions, marker);
    const text_expected_parity_direct_evidence_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_parity_direct_evidence_path);
    const text_expected_parity_direct_evidence = try guard.readUtf8File(io, allocator, text_expected_parity_direct_evidence_path);
    defer allocator.free(text_expected_parity_direct_evidence);
    for (EXPECTED_PARITY_DIRECT_EVIDENCE) |marker| try guard.requireMarker(text_expected_parity_direct_evidence, marker);
    const text_expected_roadmap_anchors_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_roadmap_anchors_path);
    const text_expected_roadmap_anchors = try guard.readUtf8File(io, allocator, text_expected_roadmap_anchors_path);
    defer allocator.free(text_expected_roadmap_anchors);
    for (EXPECTED_ROADMAP_ANCHORS) |marker| try guard.requireMarker(text_expected_roadmap_anchors, marker);
    const text_expected_helper_keys_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_helper_keys_path);
    const text_expected_helper_keys = try guard.readUtf8File(io, allocator, text_expected_helper_keys_path);
    defer allocator.free(text_expected_helper_keys);
    for (EXPECTED_HELPER_KEYS) |marker| try guard.requireMarker(text_expected_helper_keys, marker);
    const text_expected_shared_replay_inventory_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_shared_replay_inventory_path);
    const text_expected_shared_replay_inventory = try guard.readUtf8File(io, allocator, text_expected_shared_replay_inventory_path);
    defer allocator.free(text_expected_shared_replay_inventory);
    for (EXPECTED_SHARED_REPLAY_INVENTORY) |marker| try guard.requireMarker(text_expected_shared_replay_inventory, marker);
    const text_required_docs_readme_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_docs_readme_snippets_path);
    const text_required_docs_readme_snippets = try guard.readUtf8File(io, allocator, text_required_docs_readme_snippets_path);
    defer allocator.free(text_required_docs_readme_snippets);
    for (REQUIRED_DOCS_README_SNIPPETS) |marker| try guard.requireMarker(text_required_docs_readme_snippets, marker);
    const text_required_scripts_readme_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_scripts_readme_snippets_path);
    const text_required_scripts_readme_snippets = try guard.readUtf8File(io, allocator, text_required_scripts_readme_snippets_path);
    defer allocator.free(text_required_scripts_readme_snippets);
    for (REQUIRED_SCRIPTS_README_SNIPPETS) |marker| try guard.requireMarker(text_required_scripts_readme_snippets, marker);
    const text_required_evidence_catalog_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_evidence_catalog_snippets_path);
    const text_required_evidence_catalog_snippets = try guard.readUtf8File(io, allocator, text_required_evidence_catalog_snippets_path);
    defer allocator.free(text_required_evidence_catalog_snippets);
    for (REQUIRED_EVIDENCE_CATALOG_SNIPPETS) |marker| try guard.requireMarker(text_required_evidence_catalog_snippets, marker);
    const text_required_parity_catalog_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_parity_catalog_snippets_path);
    const text_required_parity_catalog_snippets = try guard.readUtf8File(io, allocator, text_required_parity_catalog_snippets_path);
    defer allocator.free(text_required_parity_catalog_snippets);
    for (REQUIRED_PARITY_CATALOG_SNIPPETS) |marker| try guard.requireMarker(text_required_parity_catalog_snippets, marker);
    const text_required_validator_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_validator_snippets_path);
    const text_required_validator_snippets = try guard.readUtf8File(io, allocator, text_required_validator_snippets_path);
    defer allocator.free(text_required_validator_snippets);
    for (REQUIRED_VALIDATOR_SNIPPETS) |marker| try guard.requireMarker(text_required_validator_snippets, marker);
    const text_required_parity_coverage_note_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_parity_coverage_note_snippets_path);
    const text_required_parity_coverage_note_snippets = try guard.readUtf8File(io, allocator, text_required_parity_coverage_note_snippets_path);
    defer allocator.free(text_required_parity_coverage_note_snippets);
    for (REQUIRED_PARITY_COVERAGE_NOTE_SNIPPETS) |marker| try guard.requireMarker(text_required_parity_coverage_note_snippets, marker);
    const text_required_parity_perf_note_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_parity_perf_note_snippets_path);
    const text_required_parity_perf_note_snippets = try guard.readUtf8File(io, allocator, text_required_parity_perf_note_snippets_path);
    defer allocator.free(text_required_parity_perf_note_snippets);
    for (REQUIRED_PARITY_PERF_NOTE_SNIPPETS) |marker| try guard.requireMarker(text_required_parity_perf_note_snippets, marker);
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

const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_PRESENT_ENTRYPOINTS=pass";
pub const self_test_pass_marker = "PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST=pass";

const EXPECTED_PACKET = [_][]const u8{
    "phase6-helper-evidence",
};

const EXPECTED_PARITY_PACKET = [_][]const u8{
    "phase6-helper-parity",
};

const EXPECTED_LANE_SCOPE = [_][]const u8{
    "shared helper-evidence rows and machine-readable manifest only",
};

const EXPECTED_PARITY_LANE_SCOPE = [_][]const u8{
    "shared helper-parity rows and machine-readable manifest only",
};

const EXPECTED_SURVEYED_HEAD = [_][]const u8{
    "current-master-readback-2026-05-22",
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

const EXPECTED_DIRECT_COMPANIONS = [_][]const u8{
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-hexdump-perf-refresh.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md",
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

const EXPECTED_SHARED_DIRECT_EVIDENCE = [_][]const u8{
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

const EXPECTED_DOCS_README_SNIPPETS = [_][]const u8{
    "- `Documentation/zigux/phase6-helper-evidence-catalog.md` - `Documentation/zigux/phase6-helper-parity-catalog.md` - `Documentation/zigux/phase6-perf-gate-survey.md`",
    "* current `master` directly serves the four roadmap-backed helper anchors through `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig`",
    "* authenticated current-master rereads now directly recover both `Documentation/zigux/phase6-helper-parity-catalog.md` and `Documentation/zigux/phase6-perf-gate-survey.md`",
};

const EXPECTED_CATALOG_SNIPPETS = [_][]const u8{
    "- surveyed head: `current-master-readback-2026-05-22`",
    "Authenticated current-master rereads now directly recover `Documentation/zigux/phase6-perf-gate-survey.md`",
    "A targeted authenticated current-master reread on 2026-05-27 also directly recovered `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`, so the Phase 6 base64 packet no longer carries a known direct-readback generator gap.",
};

const EXPECTED_SURVEY_SNIPPETS = [_][]const u8{
    "This note records the bounded control-surface gap between the Phase 6 Zigux roadmap packet and the much broader runtime command, session, and persisted environment surfaces described in the attached ZAR runtime references.",
    "That is a runtime command substrate, not a Phase 6 leaf-helper replay.",
    "Do not use it to claim that Zigux Phase 6 has already landed:",
    "- shell execution semantics",
    "- TTY session control",
    "- runtime RPC/session control",
    "- persisted workspace or app-runtime environment orchestration",
};

const REQUIRED_BUILD_SNIPPETS = [_][]const u8{
    "const bsearch_perf_root_module = b.createModule(.{",
    "const bsearch_perf_step = b.step(\"phase6-bsearch-perf\", \"Run Phase 6 bsearch helper perf gate\");",
    "const checksum_perf_matrix_test_step = b.step(",
    "const checksum_perf_step = b.step(\"phase6-checksum-perf\", \"Run Phase 6 checksum helper perf gate\");",
    "const hexdump_perf_step = b.step(\"phase6-hexdump-perf\", \"Run Phase 6 hexdump helper perf gate\");",
};

const REQUIRED_MAKEFILE_SNIPPETS = [_][]const u8{
    "phase6-bsearch-perf:",
    "$(ZIG) build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf-matrix-test:",
    "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf:",
    "phase6-hexdump-perf:",
};

const EXPECTED_BASE64_CASES = [_][]const u8{
    "STD_PAD",
    "STD_NO_PAD",
    "URLSAFE_PAD",
    "URLSAFE_NO_PAD",
    "IMAP_PAD",
    "IMAP_NO_PAD",
};

const EXPECTED_BASE64_RERUN_ROUTES = [_][]const u8{
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "make -C zigux phase6-perf",
};

const EXPECTED_BASE64_CHECKER_SURFACES = [_][]const u8{
    "scripts\\zigux/check_phase6_base64_corpus_determinism.zig",
    "scripts\\zigux/check_phase6_base64_c_parity.zig",
};

const EXPECTED_BSEARCH_CHECKER_SURFACES = [_][]const u8{
    "scripts\\zigux/check_phase6_bsearch_corpus_evidence.zig",
    "scripts\\zigux/check_phase6_bsearch_c_parity.zig",
};

const EXPECTED_BSEARCH_CASES = [_][]const u8{
    "len15",
    "len64",
    "len1024",
};

const EXPECTED_BSEARCH_RERUN_ROUTES = [_][]const u8{
    "zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-test",
    "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-perf",
    "make -C zigux phase6-perf",
};

const EXPECTED_BSEARCH_C_ABI_REPLAYS = [_][]const u8{
    "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "zigux/tests/phase6_bsearch_c_abi_budget.zig",
};

const EXPECTED_CHECKSUM_CHECKER_SURFACES = [_][]const u8{
    "scripts\\zigux/check_phase6_checksum_corpus_evidence.zig",
    "scripts\\zigux/check_phase6_checksum_c_parity.zig",
};

const EXPECTED_CHECKSUM_RERUN_ROUTES = [_][]const u8{
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
};

const EXPECTED_HEXDUMP_CHECKER_SURFACES = [_][]const u8{
    "scripts\\zigux/check_phase6_hexdump_packet.zig",
    "scripts\\zigux/check_phase6_hexdump_route.zig",
};

const EXPECTED_HEXDUMP_EVIDENCE_RERUN_ROUTES = [_][]const u8{
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
};

const EXPECTED_HEXDUMP_PARITY_RERUN_ROUTES = [_][]const u8{
    "make -C zigux phase6-hexdump-review",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
};

const EXPECTED_HEXDUMP_SHARED_REPLAY_MARKERS = [_][]const u8{
    "zig run scripts\\zigux/check_phase6_hexdump_packet.zig",
    "zig run scripts\\zigux/check_phase6_hexdump_route.zig",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
};

const EXPECTED_CHECKSUM_PAYLOAD_CASES = [_][]const u8{
    "{label:64B",
    "iterations:200000",
    "max_slowdown_pct:150}",
    "{label:1501B",
    "iterations:12000",
    "max_slowdown_pct:150}",
};

const EXPECTED_CHECKSUM_FAST_PATH_CASES = [_][]const u8{
    "{label:IPV4_20B",
    "iterations:600000",
    "max_slowdown_pct:100}",
    "{label:IPV4_20B_UPDATED",
    "iterations:600000",
    "max_slowdown_pct:100}",
    "{label:IPV4_24B",
    "iterations:500000",
    "max_slowdown_pct:100}",
    "{label:IPV4_60B",
    "iterations:250000",
    "max_slowdown_pct:100}",
};

const EXPECTED_HEXDUMP_PERF_CASES = [_][]const u8{
    "{label:16B-plain-g1",
    "reps:40000",
    "max_slowdown_pct:175}",
    "{label:32B-ascii-g2",
    "reps:10000",
    "max_slowdown_pct:550}",
    "{label:16B-ascii-g4",
    "reps:20000",
    "max_slowdown_pct:550}",
    "{label:16B-ascii-g8",
    "reps:20000",
    "max_slowdown_pct:600}",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_packet_path);
    const text_expected_packet = try guard.readUtf8File(io, allocator, text_expected_packet_path);
    defer allocator.free(text_expected_packet);
    for (EXPECTED_PACKET) |marker| try guard.requireMarker(text_expected_packet, marker);
    const text_expected_parity_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_parity_packet_path);
    const text_expected_parity_packet = try guard.readUtf8File(io, allocator, text_expected_parity_packet_path);
    defer allocator.free(text_expected_parity_packet);
    for (EXPECTED_PARITY_PACKET) |marker| try guard.requireMarker(text_expected_parity_packet, marker);
    const text_expected_lane_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_lane_scope_path);
    const text_expected_lane_scope = try guard.readUtf8File(io, allocator, text_expected_lane_scope_path);
    defer allocator.free(text_expected_lane_scope);
    for (EXPECTED_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_lane_scope, marker);
    const text_expected_parity_lane_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_parity_lane_scope_path);
    const text_expected_parity_lane_scope = try guard.readUtf8File(io, allocator, text_expected_parity_lane_scope_path);
    defer allocator.free(text_expected_parity_lane_scope);
    for (EXPECTED_PARITY_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_parity_lane_scope, marker);
    const text_expected_surveyed_head_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_surveyed_head_path);
    const text_expected_surveyed_head = try guard.readUtf8File(io, allocator, text_expected_surveyed_head_path);
    defer allocator.free(text_expected_surveyed_head);
    for (EXPECTED_SURVEYED_HEAD) |marker| try guard.requireMarker(text_expected_surveyed_head, marker);
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
    const text_expected_direct_companions_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_direct_companions_path);
    const text_expected_direct_companions = try guard.readUtf8File(io, allocator, text_expected_direct_companions_path);
    defer allocator.free(text_expected_direct_companions);
    for (EXPECTED_DIRECT_COMPANIONS) |marker| try guard.requireMarker(text_expected_direct_companions, marker);
    const text_expected_shared_direct_evidence_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_shared_direct_evidence_path);
    const text_expected_shared_direct_evidence = try guard.readUtf8File(io, allocator, text_expected_shared_direct_evidence_path);
    defer allocator.free(text_expected_shared_direct_evidence);
    for (EXPECTED_SHARED_DIRECT_EVIDENCE) |marker| try guard.requireMarker(text_expected_shared_direct_evidence, marker);
    const text_expected_docs_readme_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_docs_readme_snippets_path);
    const text_expected_docs_readme_snippets = try guard.readUtf8File(io, allocator, text_expected_docs_readme_snippets_path);
    defer allocator.free(text_expected_docs_readme_snippets);
    for (EXPECTED_DOCS_README_SNIPPETS) |marker| try guard.requireMarker(text_expected_docs_readme_snippets, marker);
    const text_expected_catalog_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_catalog_snippets_path);
    const text_expected_catalog_snippets = try guard.readUtf8File(io, allocator, text_expected_catalog_snippets_path);
    defer allocator.free(text_expected_catalog_snippets);
    for (EXPECTED_CATALOG_SNIPPETS) |marker| try guard.requireMarker(text_expected_catalog_snippets, marker);
    const text_expected_survey_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_survey_snippets_path);
    const text_expected_survey_snippets = try guard.readUtf8File(io, allocator, text_expected_survey_snippets_path);
    defer allocator.free(text_expected_survey_snippets);
    for (EXPECTED_SURVEY_SNIPPETS) |marker| try guard.requireMarker(text_expected_survey_snippets, marker);
    const text_required_build_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_build_snippets_path);
    const text_required_build_snippets = try guard.readUtf8File(io, allocator, text_required_build_snippets_path);
    defer allocator.free(text_required_build_snippets);
    for (REQUIRED_BUILD_SNIPPETS) |marker| try guard.requireMarker(text_required_build_snippets, marker);
    const text_required_makefile_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_makefile_snippets_path);
    const text_required_makefile_snippets = try guard.readUtf8File(io, allocator, text_required_makefile_snippets_path);
    defer allocator.free(text_required_makefile_snippets);
    for (REQUIRED_MAKEFILE_SNIPPETS) |marker| try guard.requireMarker(text_required_makefile_snippets, marker);
    const text_expected_base64_cases_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_base64_cases_path);
    const text_expected_base64_cases = try guard.readUtf8File(io, allocator, text_expected_base64_cases_path);
    defer allocator.free(text_expected_base64_cases);
    for (EXPECTED_BASE64_CASES) |marker| try guard.requireMarker(text_expected_base64_cases, marker);
    const text_expected_base64_rerun_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_base64_rerun_routes_path);
    const text_expected_base64_rerun_routes = try guard.readUtf8File(io, allocator, text_expected_base64_rerun_routes_path);
    defer allocator.free(text_expected_base64_rerun_routes);
    for (EXPECTED_BASE64_RERUN_ROUTES) |marker| try guard.requireMarker(text_expected_base64_rerun_routes, marker);
    const text_expected_base64_checker_surfaces_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_base64_checker_surfaces_path);
    const text_expected_base64_checker_surfaces = try guard.readUtf8File(io, allocator, text_expected_base64_checker_surfaces_path);
    defer allocator.free(text_expected_base64_checker_surfaces);
    for (EXPECTED_BASE64_CHECKER_SURFACES) |marker| try guard.requireMarker(text_expected_base64_checker_surfaces, marker);
    const text_expected_bsearch_checker_surfaces_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_bsearch_checker_surfaces_path);
    const text_expected_bsearch_checker_surfaces = try guard.readUtf8File(io, allocator, text_expected_bsearch_checker_surfaces_path);
    defer allocator.free(text_expected_bsearch_checker_surfaces);
    for (EXPECTED_BSEARCH_CHECKER_SURFACES) |marker| try guard.requireMarker(text_expected_bsearch_checker_surfaces, marker);
    const text_expected_bsearch_cases_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_bsearch_cases_path);
    const text_expected_bsearch_cases = try guard.readUtf8File(io, allocator, text_expected_bsearch_cases_path);
    defer allocator.free(text_expected_bsearch_cases);
    for (EXPECTED_BSEARCH_CASES) |marker| try guard.requireMarker(text_expected_bsearch_cases, marker);
    const text_expected_bsearch_rerun_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_bsearch_rerun_routes_path);
    const text_expected_bsearch_rerun_routes = try guard.readUtf8File(io, allocator, text_expected_bsearch_rerun_routes_path);
    defer allocator.free(text_expected_bsearch_rerun_routes);
    for (EXPECTED_BSEARCH_RERUN_ROUTES) |marker| try guard.requireMarker(text_expected_bsearch_rerun_routes, marker);
    const text_expected_bsearch_c_abi_replays_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_bsearch_c_abi_replays_path);
    const text_expected_bsearch_c_abi_replays = try guard.readUtf8File(io, allocator, text_expected_bsearch_c_abi_replays_path);
    defer allocator.free(text_expected_bsearch_c_abi_replays);
    for (EXPECTED_BSEARCH_C_ABI_REPLAYS) |marker| try guard.requireMarker(text_expected_bsearch_c_abi_replays, marker);
    const text_expected_checksum_checker_surfaces_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_checksum_checker_surfaces_path);
    const text_expected_checksum_checker_surfaces = try guard.readUtf8File(io, allocator, text_expected_checksum_checker_surfaces_path);
    defer allocator.free(text_expected_checksum_checker_surfaces);
    for (EXPECTED_CHECKSUM_CHECKER_SURFACES) |marker| try guard.requireMarker(text_expected_checksum_checker_surfaces, marker);
    const text_expected_checksum_rerun_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_checksum_rerun_routes_path);
    const text_expected_checksum_rerun_routes = try guard.readUtf8File(io, allocator, text_expected_checksum_rerun_routes_path);
    defer allocator.free(text_expected_checksum_rerun_routes);
    for (EXPECTED_CHECKSUM_RERUN_ROUTES) |marker| try guard.requireMarker(text_expected_checksum_rerun_routes, marker);
    const text_expected_hexdump_checker_surfaces_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_hexdump_checker_surfaces_path);
    const text_expected_hexdump_checker_surfaces = try guard.readUtf8File(io, allocator, text_expected_hexdump_checker_surfaces_path);
    defer allocator.free(text_expected_hexdump_checker_surfaces);
    for (EXPECTED_HEXDUMP_CHECKER_SURFACES) |marker| try guard.requireMarker(text_expected_hexdump_checker_surfaces, marker);
    const text_expected_hexdump_evidence_rerun_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_hexdump_evidence_rerun_routes_path);
    const text_expected_hexdump_evidence_rerun_routes = try guard.readUtf8File(io, allocator, text_expected_hexdump_evidence_rerun_routes_path);
    defer allocator.free(text_expected_hexdump_evidence_rerun_routes);
    for (EXPECTED_HEXDUMP_EVIDENCE_RERUN_ROUTES) |marker| try guard.requireMarker(text_expected_hexdump_evidence_rerun_routes, marker);
    const text_expected_hexdump_parity_rerun_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_hexdump_parity_rerun_routes_path);
    const text_expected_hexdump_parity_rerun_routes = try guard.readUtf8File(io, allocator, text_expected_hexdump_parity_rerun_routes_path);
    defer allocator.free(text_expected_hexdump_parity_rerun_routes);
    for (EXPECTED_HEXDUMP_PARITY_RERUN_ROUTES) |marker| try guard.requireMarker(text_expected_hexdump_parity_rerun_routes, marker);
    const text_expected_hexdump_shared_replay_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_expected_hexdump_shared_replay_markers_path);
    const text_expected_hexdump_shared_replay_markers = try guard.readUtf8File(io, allocator, text_expected_hexdump_shared_replay_markers_path);
    defer allocator.free(text_expected_hexdump_shared_replay_markers);
    for (EXPECTED_HEXDUMP_SHARED_REPLAY_MARKERS) |marker| try guard.requireMarker(text_expected_hexdump_shared_replay_markers, marker);
    const text_expected_checksum_payload_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_checksum_payload_cases_path);
    const text_expected_checksum_payload_cases = try guard.readUtf8File(io, allocator, text_expected_checksum_payload_cases_path);
    defer allocator.free(text_expected_checksum_payload_cases);
    for (EXPECTED_CHECKSUM_PAYLOAD_CASES) |marker| try guard.requireMarker(text_expected_checksum_payload_cases, marker);
    const text_expected_checksum_fast_path_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_checksum_fast_path_cases_path);
    const text_expected_checksum_fast_path_cases = try guard.readUtf8File(io, allocator, text_expected_checksum_fast_path_cases_path);
    defer allocator.free(text_expected_checksum_fast_path_cases);
    for (EXPECTED_CHECKSUM_FAST_PATH_CASES) |marker| try guard.requireMarker(text_expected_checksum_fast_path_cases, marker);
    const text_expected_hexdump_perf_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_hexdump_perf_cases_path);
    const text_expected_hexdump_perf_cases = try guard.readUtf8File(io, allocator, text_expected_hexdump_perf_cases_path);
    defer allocator.free(text_expected_hexdump_perf_cases);
    for (EXPECTED_HEXDUMP_PERF_CASES) |marker| try guard.requireMarker(text_expected_hexdump_perf_cases, marker);
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

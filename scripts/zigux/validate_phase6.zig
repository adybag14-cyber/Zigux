const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "VALIDATE_PHASE6_VALIDATION=pass";
pub const self_test_pass_marker = "VALIDATE_PHASE6_VALIDATION_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "\"packet\": \"phase6-helper-evidence\"",
    "\"surveyed_head\": \"current-master-readback-2026-05-22\"",
    "\"lane_scope\": \"shared helper-evidence rows and machine-readable manifest only\"",
    "\"current_repo_reality_gaps\": []",
    "\"lib/base64.c\"",
    "\"lib/bsearch.c\"",
    "\"lib/checksum.c\"",
    "\"lib/hexdump.c\"",
    "\"zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig\"",
    "\"zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig\"",
    "\"zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig\"",
    "\"zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe\"",
    "\"make -C zigux phase6-perf\"",
};

const markers_1 = [_][]const u8{
    "\"packet\": \"phase6-helper-parity\"",
    "\"surveyed_head\": \"current-master-readback-2026-05-22\"",
    "\"lane_scope\": \"shared helper-parity rows and machine-readable manifest only\"",
    "\"shared_follow_through_gaps\": []",
    "\"Documentation/zigux/phase6-helper-evidence-catalog.md\"",
    "\"Documentation/zigux/phase6-helper-parity-catalog.md\"",
    "\"Documentation/zigux/phase6-perf-gate-survey.md\"",
    "\"zigux/tests/phase6_build.zig\"",
    "\"zigux/tests/phase6_helper_evidence_manifest.json\"",
    "\"zigux/tests/phase6_helper_parity_manifest.json\"",
    "\"lib/base64.c\"",
    "\"lib/bsearch.c\"",
    "\"lib/checksum.c\"",
    "\"lib/hexdump.c\"",
};

const markers_2 = [_][]const u8{
    "phase6-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase6.zig",
    "phase6-base64-test:",
    "phase6-base64-perf:",
    "phase6-bsearch-test:",
    "phase6-bsearch-perf:",
    "phase6-checksum-test:",
    "phase6-checksum-perf-matrix-test:",
    "phase6-checksum-perf:",
    "phase6-hexdump-review:",
    "phase6-hexdump-perf-matrix-test:",
    "phase6-hexdump-test:",
    "phase6-hexdump-perf:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
};

const markers_3 = [_][]const u8{
    ".root_source_file = b.path(\"phase6_base64_perf.zig\")",
    ".root_source_file = b.path(\"phase6_bsearch_perf.zig\")",
    ".root_source_file = b.path(\"phase6_checksum_perf.zig\")",
    ".root_source_file = b.path(\"phase6_hexdump_perf.zig\")",
    ".root_source_file = b.path(\"phase6_hexdump_perf_matrix.zig\")",
    "b.step(\"phase6-base64-test\", \"Run Phase 6 base64 helper tests\")",
    "b.step(\"phase6-base64-perf\", \"Run Phase 6 base64 helper perf gate\")",
    "b.step(\"phase6-bsearch-test\", \"Run Phase 6 bsearch helper tests\")",
    "b.step(\"phase6-bsearch-perf\", \"Run Phase 6 bsearch helper perf gate\")",
    "\"phase6-checksum-perf-matrix-test\"",
    "b.step(\"phase6-checksum-perf\", \"Run Phase 6 checksum helper perf gate\")",
    "b.step(\"phase6-hexdump-review\", \"Run Phase 6 hexdump perf-matrix review preflight\")",
    "\"phase6-hexdump-perf-matrix-test\"",
    "b.step(\"phase6-hexdump-test\", \"Run Phase 6 hexdump helper tests\")",
    "b.step(\"phase6-hexdump-perf\", \"Run Phase 6 hexdump helper perf gate\")",
};

const markers_4 = [_][]const u8{
    "- name: Validate current Phase 6 helper packet",
    "run: make -C zigux phase6-validate",
    "- name: Run current Phase 6 leaf helper tests",
    "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    "- name: Run current Phase 6 shared perf route",
    "run: make -C zigux phase6-perf",
};

const markers_5 = [_][]const u8{
    "# Phase 6 Helper Evidence Catalog",
    "surveyed head: `current-master-readback-2026-05-22`",
    "lane scope: shared helper-evidence rows and machine-readable manifest only",
    "## Current helper-evidence rows",
    "### base64",
    "### bsearch",
    "### checksum",
    "### hexdump",
    "`zigux/tests/phase6_helper_evidence_manifest.json`",
    "`zigux/tests/phase6_helper_parity_manifest.json`",
};

const markers_6 = [_][]const u8{
    "# Phase 6 Helper Parity Catalog",
    "surveyed head: `current-master-readback-2026-05-22`",
    "lane scope: shared helper-parity rows and machine-readable manifest only",
    "## Roadmap-to-helper-evidence row index",
    "## Current helper-parity rows",
    "### base64",
    "### bsearch",
    "### checksum",
    "### hexdump",
    "PHASE6_BSEARCH_C_PARITY_CASES=17",
    "## Shared parity boundary",
};

const markers_7 = [_][]const u8{
    "# Phase 6 Perf Gate Survey",
    "PHASE6_PERF_SURVEY_STATUS=active",
    "PHASE6_PERF_PACKET=base64-bsearch-checksum-hexdump",
    "make -C zigux phase6-perf",
    "phase6-base64-perf",
    "phase6-bsearch-perf",
    "phase6-checksum-perf",
    "phase6-hexdump-perf",
    "## Current Measurement Posture",
    "## Roadmap Gap Summary",
};

const contracts = [_]FileContract{
    .{ .rel = "zigux/tests/phase6_helper_evidence_manifest.json", .markers = &markers_0 },
    .{ .rel = "zigux/tests/phase6_helper_parity_manifest.json", .markers = &markers_1 },
    .{ .rel = "zigux/Makefile", .markers = &markers_2 },
    .{ .rel = "zigux/tests/phase6_build.zig", .markers = &markers_3 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_4 },
    .{ .rel = "Documentation/zigux/phase6-helper-evidence-catalog.md", .markers = &markers_5 },
    .{ .rel = "Documentation/zigux/phase6-helper-parity-catalog.md", .markers = &markers_6 },
    .{ .rel = "Documentation/zigux/phase6-perf-gate-survey.md", .markers = &markers_7 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "VALIDATE_PHASE6_CONTRACT_COUNT={d}", .{contracts.len});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try guard.printLine(io, "VALIDATE_PHASE6_CONTRACT_COUNT={d}", .{contracts.len});
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const live_pass_marker = "VALIDATE_PHASE6_VALIDATION=pass";
// pub const self_test_pass_marker = "VALIDATE_PHASE6_VALIDATION_SELF_TEST=pass";
//
// const EXPECTED_HELPER_EVIDENCE_PACKET = [_][]const u8{
//     "phase6-helper-evidence",
// };
//
// const EXPECTED_HELPER_PARITY_PACKET = [_][]const u8{
//     "phase6-helper-parity",
// };
//
// const EXPECTED_SURVEYED_HEAD = [_][]const u8{
//     "current-master-readback-2026-05-22",
// };
//
// const EXPECTED_EVIDENCE_LANE_SCOPE = [_][]const u8{
//     "shared helper-evidence rows and machine-readable manifest only",
// };
//
// const EXPECTED_PARITY_LANE_SCOPE = [_][]const u8{
//     "shared helper-parity rows and machine-readable manifest only",
// };
//
// const EXPECTED_CURRENT_DIRECT_READBACK_COMPANIONS = [_][]const u8{
//     "Documentation/zigux/phase6-helper-evidence-catalog.md",
//     "Documentation/zigux/phase6-helper-parity-catalog.md",
//     "Documentation/zigux/phase6-hexdump-slice.md",
//     "Documentation/zigux/phase6-hexdump-perf-refresh.md",
//     "Documentation/zigux/phase6-perf-gate-survey.md",
//     "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md",
//     "Documentation/zigux/README.md",
//     "scripts/zigux/README.md",
//     "zigux/tests/README.md",
//     "zigux/Makefile",
//     "zigux/tests/phase6_build.zig",
//     "zigux/tests/phase6_helper_evidence_manifest.json",
//     "zigux/tests/phase6_helper_parity_manifest.json",
//     "scripts\\zigux/check_phase6_present_entrypoints.zig",
//     "scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig",
//     "scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig",
//     "scripts\\zigux/check_phase6_perf_threshold_markers.zig",
//     "scripts\\zigux/check_phase6_hexdump_packet.zig",
//     "scripts\\zigux/check_phase6_hexdump_route.zig",
// };
//
// const EXPECTED_SHARED_DIRECT_EVIDENCE = [_][]const u8{
//     "Documentation/zigux/phase6-helper-evidence-catalog.md",
//     "Documentation/zigux/phase6-helper-parity-catalog.md",
//     "Documentation/zigux/phase6-perf-gate-survey.md",
//     "scripts/zigux/README.md",
//     "zigux/tests/README.md",
//     "zigux/Makefile",
//     "zigux/tests/phase6_build.zig",
//     "zigux/tests/phase6_helper_evidence_manifest.json",
//     "zigux/tests/phase6_helper_parity_manifest.json",
//     "scripts\\zigux/check_phase6_shared_surface.zig",
//     "scripts\\zigux/check_phase6_present_entrypoints.zig",
//     "scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig",
//     "scripts\\zigux/validate_phase6.zig",
//     "scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig",
//     "scripts\\zigux/check_phase6_perf_threshold_markers.zig",
//     "scripts\\zigux/check_phase6_hexdump_packet.zig",
//     "scripts\\zigux/check_phase6_hexdump_route.zig",
// };
//
// const EXPECTED_ROADMAP_ANCHORS = [_][]const u8{
//     "lib/base64.c",
//     "lib/bsearch.c",
//     "lib/checksum.c",
//     "lib/hexdump.c",
// };
//
// const EXPECTED_SHARED_PERF_WRAPPER = [_][]const u8{
//     "make -C zigux phase6-perf",
// };
//
// const EXPECTED_SHARED_PERF_WRAPPER_KEYS = [_][]const u8{
//     "base64",
//     "bsearch",
//     "checksum",
//     "hexdump",
// };
//
// const EXPECTED_SHARED_REPLAY_INVENTORY = [_][]const u8{
//     "zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig",
//     "make -C zigux phase6-base64-test",
//     "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
//     "make -C zigux phase6-base64-perf",
//     "zig run scripts\\zigux/check_phase6_base64_c_parity.zig",
//     "zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
//     "make -C zigux phase6-bsearch-test",
//     "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
//     "make -C zigux phase6-bsearch-perf",
//     "zig run scripts\\zigux/check_phase6_bsearch_c_parity.zig",
//     "zig run scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig",
//     "zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig",
//     "make -C zigux phase6-checksum-test",
//     "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
//     "make -C zigux phase6-checksum-perf-matrix-test",
//     "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
//     "make -C zigux phase6-checksum-perf",
//     "zig run scripts\\zigux/check_phase6_checksum_c_parity.zig",
//     "zig run scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig",
//     "zig run scripts\\zigux/check_phase6_perf_threshold_markers.zig",
//     "zig run scripts\\zigux/check_phase6_hexdump_packet.zig",
//     "zig run scripts\\zigux/check_phase6_hexdump_route.zig",
//     "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
//     "make -C zigux phase6-hexdump-review",
//     "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
//     "make -C zigux phase6-hexdump-perf-matrix-test",
//     "zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
//     "make -C zigux phase6-hexdump-test",
//     "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
//     "make -C zigux phase6-hexdump-perf",
//     "make -C zigux phase6-perf",
// };
//
// const REQUIRED_MAKEFILE_SNIPPETS = [_][]const u8{
//     "phase6-validate:",
//     "$(ZIG) run scripts/zigux/validate_phase6.zig",
//     "phase6-base64-perf:",
//     "phase6-bsearch-perf:",
//     "$(ZIG) build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig --summary all",
//     "phase6-checksum-perf-matrix-test:",
//     "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
//     "phase6-checksum-perf:",
//     "phase6-hexdump-review:",
//     "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
// };
//
// const REQUIRED_BUILD_SNIPPETS = [_][]const u8{
//     "const base64_perf_step = b.step(\"phase6-base64-perf\", \"Run Phase 6 base64 helper perf gate\");",
//     "const bsearch_perf_root_module = b.createModule(.{",
//     "const bsearch_perf_step = b.step(\"phase6-bsearch-perf\", \"Run Phase 6 bsearch helper perf gate\");",
//     "const checksum_perf_matrix_test_step = b.step(",
//     "const checksum_perf_step = b.step(\"phase6-checksum-perf\", \"Run Phase 6 checksum helper perf gate\");",
//     "const hexdump_review_step = b.step(\"phase6-hexdump-review\", \"Run Phase 6 hexdump perf-matrix review preflight\");",
// };
//
// const REQUIRED_WORKFLOW_SNIPPETS = [_][]const u8{
//     "- name: Run current Phase 6 shared perf route",
//     "run: make -C zigux phase6-perf",
// };
//
// const REQUIRED_CATALOG_SNIPPETS = [_][]const u8{
//     "- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf.zig`",
//     "## Roadmap perf-gap readback",
//     "## Current shared replay inventory",
//     "- `zig run scripts\\zigux/check_phase6_base64_c_parity.zig`",
//     "- `make -C zigux phase6-bsearch-perf`",
//     "- `zig run scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig`",
//     "- `make -C zigux phase6-checksum-perf-matrix-test`",
//     "- `zig run scripts\\zigux/check_phase6_checksum_c_parity.zig`",
//     "- `zig run scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig`",
//     "- `zig run scripts\\zigux/check_phase6_perf_threshold_markers.zig`",
//     "A targeted authenticated current-master reread on 2026-05-27 also directly recovered `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`, so the Phase 6 base64 packet no longer carries a known direct-readback generator gap.",
// };
//
// const REQUIRED_PARITY_CATALOG_SNIPPETS = [_][]const u8{
//     "- direct helper-evidence companion: `Documentation/zigux/phase6-helper-evidence-catalog.md`",
//     "- helper-evidence row: `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `scripts\\zigux/check_phase6_base64_corpus_determinism.zig`, `scripts\\zigux/check_phase6_base64_c_parity.zig`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`",
//     "- current posture: direct helper readback is restored for the helper, focused replay, perf replay, fixture surface, dedicated corpus checker, direct C parity runner, direct C parity harness, direct C parity vectors companion, direct C parity casegen companion, direct C parity checker, and slice note. A targeted authenticated current-master reread on 2026-05-27 directly recovered `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`, so the base64 row no longer carries a known generator-side direct-readback gap.",
//     "- current posture: direct helper readback is restored for the helper, focused replay, fixture-owned perf packet, direct C parity runner, direct C parity harness, direct C parity checker, and slice note, so the checksum row now ships the same external parity review hook as the other portability-sensitive Phase 6 helpers without reopening hexdump work",
//     "scripts\\zigux/check_phase6_perf_threshold_markers.zig",
//     "Treat this file as the broader parity companion for the current helper-evidence packet rather than as a substitute for the directly readable shared packet in `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts\\zigux/check_phase6_shared_surface.zig`, `scripts\\zigux/check_phase6_present_entrypoints.zig`, `scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig`, `scripts\\zigux/validate_phase6.zig`, `scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig`, `scripts\\zigux/check_phase6_perf_threshold_markers.zig`, `scripts\\zigux/check_phase6_hexdump_packet.zig`, `scripts\\zigux/check_phase6_hexdump_route.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `Documentation/zigux/phase6-perf-gate-survey.md`.",
//     "broader reminder surfaces can keep the shared survey plus the base64-bsearch, checksum-hexdump, and perf-threshold guard surfaces inside the directly readable shared packet instead of treating any of those guards as fallback-only evidence.",
// };
//
// const REQUIRED_PARITY_COVERAGE_NOTE_SNIPPETS = [_][]const u8{
//     "Documentation/zigux/phase6-helper-parity-catalog.md",
//     "scripts\\zigux/check_phase6_base64_c_parity.zig",
//     "scripts\\zigux/check_phase6_checksum_c_parity.zig",
//     "A targeted authenticated current-master reread on 2026-05-27 also directly recovered zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig and zigux/tests/phase6_base64_c_casegen.zig, so the base64 helper row no longer carries a known generator-side direct-readback gap.",
// };
//
// const REQUIRED_PARITY_PERF_NOTE_SNIPPETS = [_][]const u8{
//     "zigux/tests/phase6_bsearch_perf.zig",
//     "zigux/tests/phase6_hexdump_perf_matrix.zig",
// };
//
// const EXPECTED_BSEARCH_CHECKER_SURFACES = [_][]const u8{
//     "scripts\\zigux/check_phase6_bsearch_corpus_evidence.zig",
//     "scripts\\zigux/check_phase6_bsearch_c_parity.zig",
// };
//
// const EXPECTED_CHECKSUM_CHECKER_SURFACES = [_][]const u8{
//     "scripts\\zigux/check_phase6_checksum_corpus_evidence.zig",
//     "scripts\\zigux/check_phase6_checksum_c_parity.zig",
// };
//
// const EXPECTED_HEXDUMP_CHECKER_SURFACES = [_][]const u8{
//     "scripts\\zigux/check_phase6_hexdump_packet.zig",
//     "scripts\\zigux/check_phase6_hexdump_route.zig",
// };
//
// const CHECKER_INVOCATIONS = [_][]const u8{
//     "(SHARED_SURFACE_CHECKER",
//     "--repo-root)",
//     "(PRESENT_ENTRYPOINTS_CHECKER",
//     "--repo-root)",
//     "(BASE64_CORPUS_CHECKER",
//     "--repo-root)",
//     "(BASE64_C_PARITY_CHECKER",
//     "None)",
//     "(BSEARCH_CORPUS_CHECKER",
//     "--repo-root)",
//     "(BSEARCH_C_PARITY_CHECKER",
//     "None)",
//     "(BASE64_BSEARCH_PERF_MARKERS_CHECKER",
//     "--repo-root)",
//     "(CHECKSUM_CORPUS_CHECKER",
//     "--repo-root)",
//     "(CHECKSUM_C_PARITY_CHECKER",
//     "None)",
//     "(CHECKSUM_HEXDUMP_PERF_MARKERS_CHECKER",
//     "--repo-root)",
//     "(HEXDUMP_PACKET_CHECKER",
//     "--repo-root)",
//     "(HEXDUMP_ROUTE_CHECKER",
//     "--root)",
//     "(PERF_THRESHOLD_CHECKER",
//     "--repo-root)",
//     "(RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET_CHECKER",
//     "--root)",
// };
//
// fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
//     const text_expected_helper_evidence_packet_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_helper_evidence_packet_path);
//     const text_expected_helper_evidence_packet = try guard.readUtf8File(io, allocator, text_expected_helper_evidence_packet_path);
//     defer allocator.free(text_expected_helper_evidence_packet);
//     for (EXPECTED_HELPER_EVIDENCE_PACKET) |marker| try guard.requireMarker(text_expected_helper_evidence_packet, marker);
//     const text_expected_helper_parity_packet_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_helper_parity_packet_path);
//     const text_expected_helper_parity_packet = try guard.readUtf8File(io, allocator, text_expected_helper_parity_packet_path);
//     defer allocator.free(text_expected_helper_parity_packet);
//     for (EXPECTED_HELPER_PARITY_PACKET) |marker| try guard.requireMarker(text_expected_helper_parity_packet, marker);
//     const text_expected_surveyed_head_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_surveyed_head_path);
//     const text_expected_surveyed_head = try guard.readUtf8File(io, allocator, text_expected_surveyed_head_path);
//     defer allocator.free(text_expected_surveyed_head);
//     for (EXPECTED_SURVEYED_HEAD) |marker| try guard.requireMarker(text_expected_surveyed_head, marker);
//     const text_expected_evidence_lane_scope_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_evidence_lane_scope_path);
//     const text_expected_evidence_lane_scope = try guard.readUtf8File(io, allocator, text_expected_evidence_lane_scope_path);
//     defer allocator.free(text_expected_evidence_lane_scope);
//     for (EXPECTED_EVIDENCE_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_evidence_lane_scope, marker);
//     const text_expected_parity_lane_scope_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_parity_lane_scope_path);
//     const text_expected_parity_lane_scope = try guard.readUtf8File(io, allocator, text_expected_parity_lane_scope_path);
//     defer allocator.free(text_expected_parity_lane_scope);
//     for (EXPECTED_PARITY_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_parity_lane_scope, marker);
//     const text_expected_current_direct_readback_companions_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_current_direct_readback_companions_path);
//     const text_expected_current_direct_readback_companions = try guard.readUtf8File(io, allocator, text_expected_current_direct_readback_companions_path);
//     defer allocator.free(text_expected_current_direct_readback_companions);
//     for (EXPECTED_CURRENT_DIRECT_READBACK_COMPANIONS) |marker| try guard.requireMarker(text_expected_current_direct_readback_companions, marker);
//     const text_expected_shared_direct_evidence_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_shared_direct_evidence_path);
//     const text_expected_shared_direct_evidence = try guard.readUtf8File(io, allocator, text_expected_shared_direct_evidence_path);
//     defer allocator.free(text_expected_shared_direct_evidence);
//     for (EXPECTED_SHARED_DIRECT_EVIDENCE) |marker| try guard.requireMarker(text_expected_shared_direct_evidence, marker);
//     const text_expected_roadmap_anchors_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_roadmap_anchors_path);
//     const text_expected_roadmap_anchors = try guard.readUtf8File(io, allocator, text_expected_roadmap_anchors_path);
//     defer allocator.free(text_expected_roadmap_anchors);
//     for (EXPECTED_ROADMAP_ANCHORS) |marker| try guard.requireMarker(text_expected_roadmap_anchors, marker);
//     const text_expected_shared_perf_wrapper_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_shared_perf_wrapper_path);
//     const text_expected_shared_perf_wrapper = try guard.readUtf8File(io, allocator, text_expected_shared_perf_wrapper_path);
//     defer allocator.free(text_expected_shared_perf_wrapper);
//     for (EXPECTED_SHARED_PERF_WRAPPER) |marker| try guard.requireMarker(text_expected_shared_perf_wrapper, marker);
//     const text_expected_shared_perf_wrapper_keys_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_shared_perf_wrapper_keys_path);
//     const text_expected_shared_perf_wrapper_keys = try guard.readUtf8File(io, allocator, text_expected_shared_perf_wrapper_keys_path);
//     defer allocator.free(text_expected_shared_perf_wrapper_keys);
//     for (EXPECTED_SHARED_PERF_WRAPPER_KEYS) |marker| try guard.requireMarker(text_expected_shared_perf_wrapper_keys, marker);
//     const text_expected_shared_replay_inventory_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_shared_replay_inventory_path);
//     const text_expected_shared_replay_inventory = try guard.readUtf8File(io, allocator, text_expected_shared_replay_inventory_path);
//     defer allocator.free(text_expected_shared_replay_inventory);
//     for (EXPECTED_SHARED_REPLAY_INVENTORY) |marker| try guard.requireMarker(text_expected_shared_replay_inventory, marker);
//     const text_required_makefile_snippets_path = try guard.joinPath(allocator, root, "zigux/Makefile");
//     defer allocator.free(text_required_makefile_snippets_path);
//     const text_required_makefile_snippets = try guard.readUtf8File(io, allocator, text_required_makefile_snippets_path);
//     defer allocator.free(text_required_makefile_snippets);
//     for (REQUIRED_MAKEFILE_SNIPPETS) |marker| try guard.requireMarker(text_required_makefile_snippets, marker);
//     const text_required_build_snippets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_required_build_snippets_path);
//     const text_required_build_snippets = try guard.readUtf8File(io, allocator, text_required_build_snippets_path);
//     defer allocator.free(text_required_build_snippets);
//     for (REQUIRED_BUILD_SNIPPETS) |marker| try guard.requireMarker(text_required_build_snippets, marker);
//     const text_required_workflow_snippets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_required_workflow_snippets_path);
//     const text_required_workflow_snippets = try guard.readUtf8File(io, allocator, text_required_workflow_snippets_path);
//     defer allocator.free(text_required_workflow_snippets);
//     for (REQUIRED_WORKFLOW_SNIPPETS) |marker| try guard.requireMarker(text_required_workflow_snippets, marker);
//     const text_required_catalog_snippets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_required_catalog_snippets_path);
//     const text_required_catalog_snippets = try guard.readUtf8File(io, allocator, text_required_catalog_snippets_path);
//     defer allocator.free(text_required_catalog_snippets);
//     for (REQUIRED_CATALOG_SNIPPETS) |marker| try guard.requireMarker(text_required_catalog_snippets, marker);
//     const text_required_parity_catalog_snippets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_required_parity_catalog_snippets_path);
//     const text_required_parity_catalog_snippets = try guard.readUtf8File(io, allocator, text_required_parity_catalog_snippets_path);
//     defer allocator.free(text_required_parity_catalog_snippets);
//     for (REQUIRED_PARITY_CATALOG_SNIPPETS) |marker| try guard.requireMarker(text_required_parity_catalog_snippets, marker);
//     const text_required_parity_coverage_note_snippets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_required_parity_coverage_note_snippets_path);
//     const text_required_parity_coverage_note_snippets = try guard.readUtf8File(io, allocator, text_required_parity_coverage_note_snippets_path);
//     defer allocator.free(text_required_parity_coverage_note_snippets);
//     for (REQUIRED_PARITY_COVERAGE_NOTE_SNIPPETS) |marker| try guard.requireMarker(text_required_parity_coverage_note_snippets, marker);
//     const text_required_parity_perf_note_snippets_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_required_parity_perf_note_snippets_path);
//     const text_required_parity_perf_note_snippets = try guard.readUtf8File(io, allocator, text_required_parity_perf_note_snippets_path);
//     defer allocator.free(text_required_parity_perf_note_snippets);
//     for (REQUIRED_PARITY_PERF_NOTE_SNIPPETS) |marker| try guard.requireMarker(text_required_parity_perf_note_snippets, marker);
//     const text_expected_bsearch_checker_surfaces_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_bsearch_checker_surfaces_path);
//     const text_expected_bsearch_checker_surfaces = try guard.readUtf8File(io, allocator, text_expected_bsearch_checker_surfaces_path);
//     defer allocator.free(text_expected_bsearch_checker_surfaces);
//     for (EXPECTED_BSEARCH_CHECKER_SURFACES) |marker| try guard.requireMarker(text_expected_bsearch_checker_surfaces, marker);
//     const text_expected_checksum_checker_surfaces_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_checksum_checker_surfaces_path);
//     const text_expected_checksum_checker_surfaces = try guard.readUtf8File(io, allocator, text_expected_checksum_checker_surfaces_path);
//     defer allocator.free(text_expected_checksum_checker_surfaces);
//     for (EXPECTED_CHECKSUM_CHECKER_SURFACES) |marker| try guard.requireMarker(text_expected_checksum_checker_surfaces, marker);
//     const text_expected_hexdump_checker_surfaces_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_expected_hexdump_checker_surfaces_path);
//     const text_expected_hexdump_checker_surfaces = try guard.readUtf8File(io, allocator, text_expected_hexdump_checker_surfaces_path);
//     defer allocator.free(text_expected_hexdump_checker_surfaces);
//     for (EXPECTED_HEXDUMP_CHECKER_SURFACES) |marker| try guard.requireMarker(text_expected_hexdump_checker_surfaces, marker);
//     const text_checker_invocations_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_checker_invocations_path);
//     const text_checker_invocations = try guard.readUtf8File(io, allocator, text_checker_invocations_path);
//     defer allocator.free(text_checker_invocations);
//     for (CHECKER_INVOCATIONS) |marker| try guard.requireMarker(text_checker_invocations, marker);
// }
//
// fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
//     try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
//     try guard.printLine(io, "{s}", .{self_test_pass_marker});
//     return 0;
// }
//
// pub fn main(init: std.process.Init) !void {
//     const allocator = init.gpa;
//     const io = init.io;
//     const args = try init.minimal.args.toSlice(allocator);
//
//     var self_test = false;
//     var explicit_root: ?[]const u8 = null;
//     var index: usize = 1;
//     while (index < args.len) : (index += 1) {
//         const arg = args[index];
//         if (std.mem.eql(u8, arg, "--self-test")) {
//             self_test = true;
//             continue;
//         }
//         if (std.mem.eql(u8, arg, "--root")) {
//             if (index + 1 >= args.len) std.process.exit(2);
//             index += 1;
//             explicit_root = args[index];
//             continue;
//         }
//     }
//
//     const root = explicit_root orelse try guard.repoRootFromScript(allocator);
//     defer if (explicit_root == null) allocator.free(root);
//
//     if (self_test) {
//         std.process.exit(try runSelfTest(io, allocator));
//     }
//
//     checkRepo(io, allocator, root) catch {
//         std.process.exit(1);
//     };
//     try guard.printLine(io, "{s}", .{live_pass_marker});
// }

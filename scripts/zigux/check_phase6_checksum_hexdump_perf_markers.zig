const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS=pass";
pub const self_test_pass_marker = "PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST=pass";

const REQUIRED_SCRIPTS_SNIPPETS = [_][]const u8{
    "## Phase 6",
    "`zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-checksum-perf`",
    "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-hexdump-perf`",
};

const REQUIRED_CATALOG_SNIPPETS = [_][]const u8{
    "checksum keeps a dedicated helper-vs-reference slowdown gate in `zigux/tests/phase6_checksum_perf.zig`",
    "- `checksum` keeps a dedicated helper-vs-reference slowdown gate in `zigux/tests/phase6_checksum_perf.zig`, with the committed payload threshold matrix (`64B`, `1501B`) and the `checksum.ipFastCsum` IPv4 fast-path matrix (`IPV4_20B`, `IPV4_20B_UPDATED`, `IPV4_24B`, `IPV4_60B`) still owned by `zigux/tests/fixtures/phase6_checksum_vectors.zig`; the shared replay packet exposes that packet through `zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-checksum-perf-matrix-test`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-perf`.",
    "hexdump keeps a dedicated slowdown gate in `zigux/tests/phase6_hexdump_perf.zig`",
    "- `make -C zigux phase6-checksum-perf`",
    "- `zig run scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig`",
    "- `make -C zigux phase6-hexdump-perf`",
};

const REQUIRED_SURVEY_SNIPPETS = [_][]const u8{
    "`64B` at `iterations = 200_000` with `max_slowdown_pct = 150`",
    "`1501B` at `iterations = 12_000` with `max_slowdown_pct = 150`",
    "`IPV4_20B` with `iterations = 600_000` and `max_slowdown_pct = 100`",
    "`IPV4_20B_UPDATED` with `iterations = 600_000` and `max_slowdown_pct = 100`",
    "`IPV4_24B` with `iterations = 500_000` and `max_slowdown_pct = 100`",
    "`IPV4_60B` with `iterations = 250_000` and `max_slowdown_pct = 100`",
    "`16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`",
    "`32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`",
    "`16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`",
    "`16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`",
};

const REQUIRED_MAKEFILE_SNIPPETS = [_][]const u8{
    "phase6-checksum-perf:",
    "phase6-hexdump-review:",
    "phase6-hexdump-perf-matrix-test:",
    "phase6-hexdump-perf:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
};

const REQUIRED_BUILD_SNIPPETS = [_][]const u8{
    "const checksum_perf_matrix_test_step = b.step(",
    "        \"phase6-checksum-perf-matrix-test\",",
    "const checksum_perf_step = b.step(\"phase6-checksum-perf\", \"Run Phase 6 checksum helper perf gate\");",
    "const hexdump_review_step = b.step(\"phase6-hexdump-review\", \"Run Phase 6 hexdump perf-matrix review preflight\");",
    "const hexdump_perf_matrix_test_step = b.step(",
    "        \"phase6-hexdump-perf-matrix-test\",",
    "const hexdump_perf_step = b.step(\"phase6-hexdump-perf\", \"Run Phase 6 hexdump helper perf gate\");",
};

const REQUIRED_CHECKSUM_PERF_SNIPPETS = [_][]const u8{
    "try validatePerfMatrix();",
    "try validateFastPathMatrix();",
    "PHASE6_CHECKSUM_PERF_CASE_COUNT",
    "PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT",
    "std.debug.print(\"PHASE6_CHECKSUM_PERF_{s}_THRESHOLD_PCT={d}\\n\", .{ case.label, case.max_slowdown_pct });",
    "std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_THRESHOLD_PCT={d}\\n\", .{ case.label, case.max_slowdown_pct });",
    "std.debug.print(\"PHASE6_CHECKSUM_PERF={s}\\n\", .{if (failed) \"fail\" else \"pass\"});",
    "error.ChecksumPerfRegression",
};

const REQUIRED_EVIDENCE_REPLAYS = [_][]const u8{
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "zig run scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
};

const REQUIRED_SHARED_DIRECT_EVIDENCE = [_][]const u8{
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "scripts\\zigux/validate_phase6.zig",
    "scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig",
    "scripts\\zigux/check_phase6_perf_threshold_markers.zig",
    "scripts\\zigux/check_phase6_hexdump_packet.zig",
    "scripts\\zigux/check_phase6_hexdump_route.zig",
};

const REQUIRED_CHECKSUM_CHECKER_SURFACES = [_][]const u8{
    "scripts\\zigux/check_phase6_checksum_corpus_evidence.zig",
    "scripts\\zigux/check_phase6_checksum_c_parity.zig",
};

const REQUIRED_HEXDUMP_CHECKER_SURFACES = [_][]const u8{
    "scripts\\zigux/check_phase6_hexdump_packet.zig",
    "scripts\\zigux/check_phase6_hexdump_route.zig",
};

const REQUIRED_CHECKSUM_EVIDENCE_LINUX_STYLE_RERUN_ROUTES = [_][]const u8{
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
};

const REQUIRED_HEXDUMP_EVIDENCE_LINUX_STYLE_RERUN_ROUTES = [_][]const u8{
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
};

const REQUIRED_CHECKSUM_LINUX_STYLE_RERUN_ROUTES = [_][]const u8{
    "make -C zigux phase6-checksum-perf-matrix-test",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
};

const REQUIRED_HEXDUMP_LINUX_STYLE_RERUN_ROUTES = [_][]const u8{
    "make -C zigux phase6-hexdump-review",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
};

const EXPECTED_HEXDUMP_PERF_MATRIX_PREFLIGHT = [_][]const u8{
    "zigux/tests/phase6_hexdump_perf_matrix.zig",
};

const EXPECTED_SURVEYED_HEAD = [_][]const u8{
    "current-master-readback-2026-05-22",
};

const EXPECTED_EVIDENCE_LANE_SCOPE = [_][]const u8{
    "shared helper-evidence rows and machine-readable manifest only",
};

const EXPECTED_PARITY_LANE_SCOPE = [_][]const u8{
    "shared helper-parity rows and machine-readable manifest only",
};

const EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS = [_][]const u8{
    "IPV4_20B",
    "IPV4_20B_UPDATED",
    "IPV4_24B",
    "IPV4_60B",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_scripts_snippets_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_scripts_snippets_path);
    const text_required_scripts_snippets = try guard.readUtf8File(io, allocator, text_required_scripts_snippets_path);
    defer allocator.free(text_required_scripts_snippets);
    for (REQUIRED_SCRIPTS_SNIPPETS) |marker| try guard.requireMarker(text_required_scripts_snippets, marker);
    const text_required_catalog_snippets_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_catalog_snippets_path);
    const text_required_catalog_snippets = try guard.readUtf8File(io, allocator, text_required_catalog_snippets_path);
    defer allocator.free(text_required_catalog_snippets);
    for (REQUIRED_CATALOG_SNIPPETS) |marker| try guard.requireMarker(text_required_catalog_snippets, marker);
    const text_required_survey_snippets_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_survey_snippets_path);
    const text_required_survey_snippets = try guard.readUtf8File(io, allocator, text_required_survey_snippets_path);
    defer allocator.free(text_required_survey_snippets);
    for (REQUIRED_SURVEY_SNIPPETS) |marker| try guard.requireMarker(text_required_survey_snippets, marker);
    const text_required_makefile_snippets_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_makefile_snippets_path);
    const text_required_makefile_snippets = try guard.readUtf8File(io, allocator, text_required_makefile_snippets_path);
    defer allocator.free(text_required_makefile_snippets);
    for (REQUIRED_MAKEFILE_SNIPPETS) |marker| try guard.requireMarker(text_required_makefile_snippets, marker);
    const text_required_build_snippets_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_build_snippets_path);
    const text_required_build_snippets = try guard.readUtf8File(io, allocator, text_required_build_snippets_path);
    defer allocator.free(text_required_build_snippets);
    for (REQUIRED_BUILD_SNIPPETS) |marker| try guard.requireMarker(text_required_build_snippets, marker);
    const text_required_checksum_perf_snippets_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_checksum_perf_snippets_path);
    const text_required_checksum_perf_snippets = try guard.readUtf8File(io, allocator, text_required_checksum_perf_snippets_path);
    defer allocator.free(text_required_checksum_perf_snippets);
    for (REQUIRED_CHECKSUM_PERF_SNIPPETS) |marker| try guard.requireMarker(text_required_checksum_perf_snippets, marker);
    const text_required_evidence_replays_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_evidence_replays_path);
    const text_required_evidence_replays = try guard.readUtf8File(io, allocator, text_required_evidence_replays_path);
    defer allocator.free(text_required_evidence_replays);
    for (REQUIRED_EVIDENCE_REPLAYS) |marker| try guard.requireMarker(text_required_evidence_replays, marker);
    const text_required_shared_direct_evidence_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_shared_direct_evidence_path);
    const text_required_shared_direct_evidence = try guard.readUtf8File(io, allocator, text_required_shared_direct_evidence_path);
    defer allocator.free(text_required_shared_direct_evidence);
    for (REQUIRED_SHARED_DIRECT_EVIDENCE) |marker| try guard.requireMarker(text_required_shared_direct_evidence, marker);
    const text_required_checksum_checker_surfaces_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_checksum_checker_surfaces_path);
    const text_required_checksum_checker_surfaces = try guard.readUtf8File(io, allocator, text_required_checksum_checker_surfaces_path);
    defer allocator.free(text_required_checksum_checker_surfaces);
    for (REQUIRED_CHECKSUM_CHECKER_SURFACES) |marker| try guard.requireMarker(text_required_checksum_checker_surfaces, marker);
    const text_required_hexdump_checker_surfaces_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_hexdump_checker_surfaces_path);
    const text_required_hexdump_checker_surfaces = try guard.readUtf8File(io, allocator, text_required_hexdump_checker_surfaces_path);
    defer allocator.free(text_required_hexdump_checker_surfaces);
    for (REQUIRED_HEXDUMP_CHECKER_SURFACES) |marker| try guard.requireMarker(text_required_hexdump_checker_surfaces, marker);
    const text_required_checksum_evidence_linux_style_rerun_routes_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_checksum_evidence_linux_style_rerun_routes_path);
    const text_required_checksum_evidence_linux_style_rerun_routes = try guard.readUtf8File(io, allocator, text_required_checksum_evidence_linux_style_rerun_routes_path);
    defer allocator.free(text_required_checksum_evidence_linux_style_rerun_routes);
    for (REQUIRED_CHECKSUM_EVIDENCE_LINUX_STYLE_RERUN_ROUTES) |marker| try guard.requireMarker(text_required_checksum_evidence_linux_style_rerun_routes, marker);
    const text_required_hexdump_evidence_linux_style_rerun_routes_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_hexdump_evidence_linux_style_rerun_routes_path);
    const text_required_hexdump_evidence_linux_style_rerun_routes = try guard.readUtf8File(io, allocator, text_required_hexdump_evidence_linux_style_rerun_routes_path);
    defer allocator.free(text_required_hexdump_evidence_linux_style_rerun_routes);
    for (REQUIRED_HEXDUMP_EVIDENCE_LINUX_STYLE_RERUN_ROUTES) |marker| try guard.requireMarker(text_required_hexdump_evidence_linux_style_rerun_routes, marker);
    const text_required_checksum_linux_style_rerun_routes_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_checksum_linux_style_rerun_routes_path);
    const text_required_checksum_linux_style_rerun_routes = try guard.readUtf8File(io, allocator, text_required_checksum_linux_style_rerun_routes_path);
    defer allocator.free(text_required_checksum_linux_style_rerun_routes);
    for (REQUIRED_CHECKSUM_LINUX_STYLE_RERUN_ROUTES) |marker| try guard.requireMarker(text_required_checksum_linux_style_rerun_routes, marker);
    const text_required_hexdump_linux_style_rerun_routes_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_hexdump_linux_style_rerun_routes_path);
    const text_required_hexdump_linux_style_rerun_routes = try guard.readUtf8File(io, allocator, text_required_hexdump_linux_style_rerun_routes_path);
    defer allocator.free(text_required_hexdump_linux_style_rerun_routes);
    for (REQUIRED_HEXDUMP_LINUX_STYLE_RERUN_ROUTES) |marker| try guard.requireMarker(text_required_hexdump_linux_style_rerun_routes, marker);
    const text_expected_hexdump_perf_matrix_preflight_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_hexdump_perf_matrix_preflight_path);
    const text_expected_hexdump_perf_matrix_preflight = try guard.readUtf8File(io, allocator, text_expected_hexdump_perf_matrix_preflight_path);
    defer allocator.free(text_expected_hexdump_perf_matrix_preflight);
    for (EXPECTED_HEXDUMP_PERF_MATRIX_PREFLIGHT) |marker| try guard.requireMarker(text_expected_hexdump_perf_matrix_preflight, marker);
    const text_expected_surveyed_head_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_surveyed_head_path);
    const text_expected_surveyed_head = try guard.readUtf8File(io, allocator, text_expected_surveyed_head_path);
    defer allocator.free(text_expected_surveyed_head);
    for (EXPECTED_SURVEYED_HEAD) |marker| try guard.requireMarker(text_expected_surveyed_head, marker);
    const text_expected_evidence_lane_scope_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_evidence_lane_scope_path);
    const text_expected_evidence_lane_scope = try guard.readUtf8File(io, allocator, text_expected_evidence_lane_scope_path);
    defer allocator.free(text_expected_evidence_lane_scope);
    for (EXPECTED_EVIDENCE_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_evidence_lane_scope, marker);
    const text_expected_parity_lane_scope_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_parity_lane_scope_path);
    const text_expected_parity_lane_scope = try guard.readUtf8File(io, allocator, text_expected_parity_lane_scope_path);
    defer allocator.free(text_expected_parity_lane_scope);
    for (EXPECTED_PARITY_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_parity_lane_scope, marker);
    const text_expected_checksum_ipv4_fast_path_labels_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_checksum_ipv4_fast_path_labels_path);
    const text_expected_checksum_ipv4_fast_path_labels = try guard.readUtf8File(io, allocator, text_expected_checksum_ipv4_fast_path_labels_path);
    defer allocator.free(text_expected_checksum_ipv4_fast_path_labels);
    for (EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS) |marker| try guard.requireMarker(text_expected_checksum_ipv4_fast_path_labels, marker);
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

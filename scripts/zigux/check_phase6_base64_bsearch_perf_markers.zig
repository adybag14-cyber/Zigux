const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_BASE64_BSEARCH_PERF_MARKERS=pass";
pub const self_test_pass_marker = "PHASE6_BASE64_BSEARCH_PERF_MARKERS_SELF_TEST=pass";

const REQUIRED_SCRIPTS_SNIPPETS = [_][]const u8{
    "## Phase 6",
    "`zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-base64-perf`",
    "`zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-bsearch-perf`",
};

const REQUIRED_CATALOG_SNIPPETS = [_][]const u8{
    "base64` keeps a dedicated helper-local slowdown replay in `zigux/tests/phase6_base64_perf.zig`",
    "bsearch` now keeps a dedicated helper-local perf replay in `zigux/tests/phase6_bsearch_perf.zig`",
    "`scripts\\zigux/check_phase6_bsearch_c_parity.zig` now keeps 17 sorted lookup cases explicit across ascending and descending comparator-driven lookups",
    "- `make -C zigux phase6-base64-perf`",
    "- `make -C zigux phase6-bsearch-perf`",
};

const REQUIRED_PARITY_CATALOG_SNIPPETS = [_][]const u8{
    "- direct C parity spot-check marker: `PHASE6_BSEARCH_C_PARITY_CASES=17`",
};

const REQUIRED_SURVEY_SNIPPETS = [_][]const u8{
    "- aggregate route note: `make -C zigux phase6-perf` is now a committed shared wrapper over the directly readable helper-local perf packet, while the broader `make -C zigux phase6` route still stops at `phase6-validate` plus the bundled helper tests and does not rerun the dedicated perf gates",
    "- workflow note: current `.github/workflows/zigux-bootstrap.yml` reruns `make -C zigux phase6-perf`, so the shared bootstrap route now follows the aggregate perf wrapper rather than relying on helper-specific ad hoc coverage",
    "`zigux/tests/fixtures/phase6_base64_vectors.zig` now pins six perf cases, `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, and `zigux/tests/phase6_base64_perf.zig` keeps the same six-case helper-owned replay aligned with that fixture packet",
    "`len15` at `reps = 4_000`, `len64` at `reps = 2_000`, and `len1024` at `reps = 250`; `zigux/tests/fixtures/phase6_bsearch_vectors.zig` fixes `query_count = 16`; and `zigux/tests/phase6_bsearch_perf.zig` enforces the direct budget formula `std.math.log2_int_ceil(usize, case.len) + 1` across witness, average, and worst-case comparator counts while still printing the live `ns_per_lookup` evidence for each case",
};

const REQUIRED_MAKEFILE_SNIPPETS = [_][]const u8{
    "phase6-base64-perf:",
    "phase6-bsearch-perf:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
};

const REQUIRED_BSEARCH_PERF_SNIPPETS = [_][]const u8{
    "fn compareCountedDescending(key: *const u32, item: *const u32) i32 {",
    "fn compareCountedOpaqueDescending(key: *const anyopaque, item: *const anyopaque) i32 {",
    "populateDescending(descending_values, ascending_values);",
    "const descending_witness = try runWitnessCases(",
    "compareCountedDescending,",
    "compareCountedOpaqueDescending,",
    "for (descending_queries, descending_expected_hits) |query, expected_hit| {",
};

const REQUIRED_BSEARCH_C_PARITY_CHECKER_SNIPPETS = [_][]const u8{
    "EXPECTED_CASE_COUNT = 17",
    "print(f\"PHASE6_BSEARCH_C_PARITY_CASES={len(c_lines)}\")",
};

const REQUIRED_SHARED_REPLAYS = [_][]const u8{
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-perf",
    "zig run scripts\\zigux/check_phase6_bsearch_c_parity.zig",
    "make -C zigux phase6-perf",
};

const REQUIRED_BASE64_CHECKER_SURFACES = [_][]const u8{
    "scripts\\zigux/check_phase6_base64_corpus_determinism.zig",
    "scripts\\zigux/check_phase6_base64_c_parity.zig",
};

const REQUIRED_BSEARCH_CHECKER_SURFACES = [_][]const u8{
    "scripts\\zigux/check_phase6_bsearch_corpus_evidence.zig",
    "scripts\\zigux/check_phase6_bsearch_c_parity.zig",
};

const EXPECTED_BASE64_LABELS = [_][]const u8{
    "STD_PAD",
    "STD_NO_PAD",
    "URLSAFE_PAD",
    "URLSAFE_NO_PAD",
    "IMAP_PAD",
    "IMAP_NO_PAD",
};

const EXPECTED_BSEARCH_LABELS = [_][]const u8{
    "len15",
    "len64",
    "len1024",
};

const EXPECTED_BSEARCH_C_ABI_REPLAYS = [_][]const u8{
    "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "zigux/tests/phase6_bsearch_c_abi_budget.zig",
};

const EXPECTED_BSEARCH_BUDGET_FORMULA = [_][]const u8{
    "std.math.log2_int_ceil(len) + 1",
};

const EXPECTED_BSEARCH_BOUND_BUDGET_FORMULA = [_][]const u8{
    "std.math.log2_int_ceil(len) + 1",
};

const EXPECTED_SHARED_PERF_WRAPPER = [_][]const u8{
    "make -C zigux phase6-perf",
};

const EXPECTED_BASE64_ZIG_PERF_ROUTE = [_][]const u8{
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
};

const EXPECTED_BSEARCH_ZIG_PERF_ROUTE = [_][]const u8{
    "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
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

const EXPECTED_BSEARCH_CASES = [_][]const u8{
    "{label:len15",
    "reps:4000}",
    "{label:len64",
    "reps:2000}",
    "{label:len1024",
    "reps:250}",
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
    const text_required_parity_catalog_snippets_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_parity_catalog_snippets_path);
    const text_required_parity_catalog_snippets = try guard.readUtf8File(io, allocator, text_required_parity_catalog_snippets_path);
    defer allocator.free(text_required_parity_catalog_snippets);
    for (REQUIRED_PARITY_CATALOG_SNIPPETS) |marker| try guard.requireMarker(text_required_parity_catalog_snippets, marker);
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
    const text_required_bsearch_perf_snippets_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_bsearch_perf_snippets_path);
    const text_required_bsearch_perf_snippets = try guard.readUtf8File(io, allocator, text_required_bsearch_perf_snippets_path);
    defer allocator.free(text_required_bsearch_perf_snippets);
    for (REQUIRED_BSEARCH_PERF_SNIPPETS) |marker| try guard.requireMarker(text_required_bsearch_perf_snippets, marker);
    const text_required_bsearch_c_parity_checker_snippets_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_bsearch_c_parity_checker_snippets_path);
    const text_required_bsearch_c_parity_checker_snippets = try guard.readUtf8File(io, allocator, text_required_bsearch_c_parity_checker_snippets_path);
    defer allocator.free(text_required_bsearch_c_parity_checker_snippets);
    for (REQUIRED_BSEARCH_C_PARITY_CHECKER_SNIPPETS) |marker| try guard.requireMarker(text_required_bsearch_c_parity_checker_snippets, marker);
    const text_required_shared_replays_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_shared_replays_path);
    const text_required_shared_replays = try guard.readUtf8File(io, allocator, text_required_shared_replays_path);
    defer allocator.free(text_required_shared_replays);
    for (REQUIRED_SHARED_REPLAYS) |marker| try guard.requireMarker(text_required_shared_replays, marker);
    const text_required_base64_checker_surfaces_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_base64_checker_surfaces_path);
    const text_required_base64_checker_surfaces = try guard.readUtf8File(io, allocator, text_required_base64_checker_surfaces_path);
    defer allocator.free(text_required_base64_checker_surfaces);
    for (REQUIRED_BASE64_CHECKER_SURFACES) |marker| try guard.requireMarker(text_required_base64_checker_surfaces, marker);
    const text_required_bsearch_checker_surfaces_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_required_bsearch_checker_surfaces_path);
    const text_required_bsearch_checker_surfaces = try guard.readUtf8File(io, allocator, text_required_bsearch_checker_surfaces_path);
    defer allocator.free(text_required_bsearch_checker_surfaces);
    for (REQUIRED_BSEARCH_CHECKER_SURFACES) |marker| try guard.requireMarker(text_required_bsearch_checker_surfaces, marker);
    const text_expected_base64_labels_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_base64_labels_path);
    const text_expected_base64_labels = try guard.readUtf8File(io, allocator, text_expected_base64_labels_path);
    defer allocator.free(text_expected_base64_labels);
    for (EXPECTED_BASE64_LABELS) |marker| try guard.requireMarker(text_expected_base64_labels, marker);
    const text_expected_bsearch_labels_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_bsearch_labels_path);
    const text_expected_bsearch_labels = try guard.readUtf8File(io, allocator, text_expected_bsearch_labels_path);
    defer allocator.free(text_expected_bsearch_labels);
    for (EXPECTED_BSEARCH_LABELS) |marker| try guard.requireMarker(text_expected_bsearch_labels, marker);
    const text_expected_bsearch_c_abi_replays_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_bsearch_c_abi_replays_path);
    const text_expected_bsearch_c_abi_replays = try guard.readUtf8File(io, allocator, text_expected_bsearch_c_abi_replays_path);
    defer allocator.free(text_expected_bsearch_c_abi_replays);
    for (EXPECTED_BSEARCH_C_ABI_REPLAYS) |marker| try guard.requireMarker(text_expected_bsearch_c_abi_replays, marker);
    const text_expected_bsearch_budget_formula_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_bsearch_budget_formula_path);
    const text_expected_bsearch_budget_formula = try guard.readUtf8File(io, allocator, text_expected_bsearch_budget_formula_path);
    defer allocator.free(text_expected_bsearch_budget_formula);
    for (EXPECTED_BSEARCH_BUDGET_FORMULA) |marker| try guard.requireMarker(text_expected_bsearch_budget_formula, marker);
    const text_expected_bsearch_bound_budget_formula_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_bsearch_bound_budget_formula_path);
    const text_expected_bsearch_bound_budget_formula = try guard.readUtf8File(io, allocator, text_expected_bsearch_bound_budget_formula_path);
    defer allocator.free(text_expected_bsearch_bound_budget_formula);
    for (EXPECTED_BSEARCH_BOUND_BUDGET_FORMULA) |marker| try guard.requireMarker(text_expected_bsearch_bound_budget_formula, marker);
    const text_expected_shared_perf_wrapper_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_shared_perf_wrapper_path);
    const text_expected_shared_perf_wrapper = try guard.readUtf8File(io, allocator, text_expected_shared_perf_wrapper_path);
    defer allocator.free(text_expected_shared_perf_wrapper);
    for (EXPECTED_SHARED_PERF_WRAPPER) |marker| try guard.requireMarker(text_expected_shared_perf_wrapper, marker);
    const text_expected_base64_zig_perf_route_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_base64_zig_perf_route_path);
    const text_expected_base64_zig_perf_route = try guard.readUtf8File(io, allocator, text_expected_base64_zig_perf_route_path);
    defer allocator.free(text_expected_base64_zig_perf_route);
    for (EXPECTED_BASE64_ZIG_PERF_ROUTE) |marker| try guard.requireMarker(text_expected_base64_zig_perf_route, marker);
    const text_expected_bsearch_zig_perf_route_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_expected_bsearch_zig_perf_route_path);
    const text_expected_bsearch_zig_perf_route = try guard.readUtf8File(io, allocator, text_expected_bsearch_zig_perf_route_path);
    defer allocator.free(text_expected_bsearch_zig_perf_route);
    for (EXPECTED_BSEARCH_ZIG_PERF_ROUTE) |marker| try guard.requireMarker(text_expected_bsearch_zig_perf_route, marker);
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
    const text_expected_bsearch_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_bsearch_cases_path);
    const text_expected_bsearch_cases = try guard.readUtf8File(io, allocator, text_expected_bsearch_cases_path);
    defer allocator.free(text_expected_bsearch_cases);
    for (EXPECTED_BSEARCH_CASES) |marker| try guard.requireMarker(text_expected_bsearch_cases, marker);
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

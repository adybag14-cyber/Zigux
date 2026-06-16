const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_PERF_THRESHOLD_MARKERS=pass";
pub const self_test_pass_marker = "PHASE6_PERF_THRESHOLD_MARKERS_SELF_TEST=pass";

const REQUIRED_SURVEY_SNIPPETS = [_][]const u8{
    "the exact posture below was re-read from current `master` on `2026-05-27`",
    "`iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`",
    "`len15` at `reps = 4_000`, `len64` at `reps = 2_000`, and `len1024` at `reps = 250`",
    "`query_count = 16`",
    "`std.math.log2_int_ceil(usize, case.len) + 1`",
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

const REQUIRED_BASE64_FIXTURE_SNIPPETS = [_][]const u8{
    ".label = \"STD_PAD\"",
    ".label = \"STD_NO_PAD\"",
    ".label = \"URLSAFE_PAD\"",
    ".label = \"URLSAFE_NO_PAD\"",
    ".label = \"IMAP_PAD\"",
    ".label = \"IMAP_NO_PAD\"",
    ".iterations = 12000",
    ".max_encode_slowdown_pct = 150",
    ".max_decode_slowdown_pct = 325",
};

const REQUIRED_BSEARCH_FIXTURE_SNIPPETS = [_][]const u8{
    ".{ .label = \"len15\", .len = representative_ascending_values.len, .reps = 4_000 }",
    ".{ .label = \"len64\", .len = 64, .reps = 2_000 }",
    ".{ .label = \"len1024\", .len = 1_024, .reps = 250 }",
    "pub const query_count: usize = 16;",
};

const REQUIRED_CHECKSUM_FIXTURE_SNIPPETS = [_][]const u8{
    ".{ .label = \"64B\", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 }",
    ".{ .label = \"1501B\", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 }",
    ".{ .label = \"IPV4_20B\", .header = &ip_fast_csum_ipv4_20b, .iterations = 600_000, .max_slowdown_pct = 100 }",
    ".{ .label = \"IPV4_20B_UPDATED\", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 }",
    ".{ .label = \"IPV4_24B\", .header = &ip_fast_csum_ipv4_24b, .iterations = 500_000, .max_slowdown_pct = 100 }",
    ".{ .label = \"IPV4_60B\", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 }",
};

const REQUIRED_HEXDUMP_FIXTURE_SNIPPETS = [_][]const u8{
    ".label = \"16B-plain-g1\"",
    ".reps = 40_000",
    ".max_slowdown_pct = 175",
    ".label = \"32B-ascii-g2\"",
    ".reps = 10_000",
    ".max_slowdown_pct = 550",
    ".label = \"16B-ascii-g4\"",
    ".reps = 20_000",
    ".label = \"16B-ascii-g8\"",
    ".max_slowdown_pct = 600",
};

const REQUIRED_BSEARCH_PERF_SNIPPETS = [_][]const u8{
    "const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;",
    "const average_budget = max_compare_budget;",
    "const worst_case_budget = max_compare_budget;",
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

const EXPECTED_BSEARCH_FORMULA = [_][]const u8{
    "std.math.log2_int_ceil(len) + 1",
};

const EXPECTED_CHECKSUM_PAYLOAD_LABELS = [_][]const u8{
    "64B",
    "1501B",
};

const EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS = [_][]const u8{
    "IPV4_20B",
    "IPV4_20B_UPDATED",
    "IPV4_24B",
    "IPV4_60B",
};

const EXPECTED_HEXDUMP_LABELS = [_][]const u8{
    "16B-plain-g1",
    "32B-ascii-g2",
    "16B-ascii-g4",
    "16B-ascii-g8",
};

const EXPECTED_BSEARCH_CASES = [_][]const u8{
    "{label:len15",
    "reps:4000}",
    "{label:len64",
    "reps:2000}",
    "{label:len1024",
    "reps:250}",
};

const EXPECTED_CHECKSUM_CASES = [_][]const u8{
    "{label:64B",
    "iterations:200000",
    "max_slowdown_pct:150}",
    "{label:1501B",
    "iterations:12000",
    "max_slowdown_pct:150}",
};

const EXPECTED_CHECKSUM_IPV4_CASES = [_][]const u8{
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

const EXPECTED_HEXDUMP_CASES = [_][]const u8{
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
    const text_required_survey_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_required_survey_snippets_path);
    const text_required_survey_snippets = try guard.readUtf8File(io, allocator, text_required_survey_snippets_path);
    defer allocator.free(text_required_survey_snippets);
    for (REQUIRED_SURVEY_SNIPPETS) |marker| try guard.requireMarker(text_required_survey_snippets, marker);
    const text_required_base64_fixture_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_required_base64_fixture_snippets_path);
    const text_required_base64_fixture_snippets = try guard.readUtf8File(io, allocator, text_required_base64_fixture_snippets_path);
    defer allocator.free(text_required_base64_fixture_snippets);
    for (REQUIRED_BASE64_FIXTURE_SNIPPETS) |marker| try guard.requireMarker(text_required_base64_fixture_snippets, marker);
    const text_required_bsearch_fixture_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_required_bsearch_fixture_snippets_path);
    const text_required_bsearch_fixture_snippets = try guard.readUtf8File(io, allocator, text_required_bsearch_fixture_snippets_path);
    defer allocator.free(text_required_bsearch_fixture_snippets);
    for (REQUIRED_BSEARCH_FIXTURE_SNIPPETS) |marker| try guard.requireMarker(text_required_bsearch_fixture_snippets, marker);
    const text_required_checksum_fixture_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_required_checksum_fixture_snippets_path);
    const text_required_checksum_fixture_snippets = try guard.readUtf8File(io, allocator, text_required_checksum_fixture_snippets_path);
    defer allocator.free(text_required_checksum_fixture_snippets);
    for (REQUIRED_CHECKSUM_FIXTURE_SNIPPETS) |marker| try guard.requireMarker(text_required_checksum_fixture_snippets, marker);
    const text_required_hexdump_fixture_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_required_hexdump_fixture_snippets_path);
    const text_required_hexdump_fixture_snippets = try guard.readUtf8File(io, allocator, text_required_hexdump_fixture_snippets_path);
    defer allocator.free(text_required_hexdump_fixture_snippets);
    for (REQUIRED_HEXDUMP_FIXTURE_SNIPPETS) |marker| try guard.requireMarker(text_required_hexdump_fixture_snippets, marker);
    const text_required_bsearch_perf_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_required_bsearch_perf_snippets_path);
    const text_required_bsearch_perf_snippets = try guard.readUtf8File(io, allocator, text_required_bsearch_perf_snippets_path);
    defer allocator.free(text_required_bsearch_perf_snippets);
    for (REQUIRED_BSEARCH_PERF_SNIPPETS) |marker| try guard.requireMarker(text_required_bsearch_perf_snippets, marker);
    const text_expected_surveyed_head_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_expected_surveyed_head_path);
    const text_expected_surveyed_head = try guard.readUtf8File(io, allocator, text_expected_surveyed_head_path);
    defer allocator.free(text_expected_surveyed_head);
    for (EXPECTED_SURVEYED_HEAD) |marker| try guard.requireMarker(text_expected_surveyed_head, marker);
    const text_expected_evidence_lane_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_expected_evidence_lane_scope_path);
    const text_expected_evidence_lane_scope = try guard.readUtf8File(io, allocator, text_expected_evidence_lane_scope_path);
    defer allocator.free(text_expected_evidence_lane_scope);
    for (EXPECTED_EVIDENCE_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_evidence_lane_scope, marker);
    const text_expected_parity_lane_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_expected_parity_lane_scope_path);
    const text_expected_parity_lane_scope = try guard.readUtf8File(io, allocator, text_expected_parity_lane_scope_path);
    defer allocator.free(text_expected_parity_lane_scope);
    for (EXPECTED_PARITY_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_parity_lane_scope, marker);
    const text_expected_base64_labels_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_expected_base64_labels_path);
    const text_expected_base64_labels = try guard.readUtf8File(io, allocator, text_expected_base64_labels_path);
    defer allocator.free(text_expected_base64_labels);
    for (EXPECTED_BASE64_LABELS) |marker| try guard.requireMarker(text_expected_base64_labels, marker);
    const text_expected_bsearch_labels_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_expected_bsearch_labels_path);
    const text_expected_bsearch_labels = try guard.readUtf8File(io, allocator, text_expected_bsearch_labels_path);
    defer allocator.free(text_expected_bsearch_labels);
    for (EXPECTED_BSEARCH_LABELS) |marker| try guard.requireMarker(text_expected_bsearch_labels, marker);
    const text_expected_bsearch_formula_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_expected_bsearch_formula_path);
    const text_expected_bsearch_formula = try guard.readUtf8File(io, allocator, text_expected_bsearch_formula_path);
    defer allocator.free(text_expected_bsearch_formula);
    for (EXPECTED_BSEARCH_FORMULA) |marker| try guard.requireMarker(text_expected_bsearch_formula, marker);
    const text_expected_checksum_payload_labels_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_expected_checksum_payload_labels_path);
    const text_expected_checksum_payload_labels = try guard.readUtf8File(io, allocator, text_expected_checksum_payload_labels_path);
    defer allocator.free(text_expected_checksum_payload_labels);
    for (EXPECTED_CHECKSUM_PAYLOAD_LABELS) |marker| try guard.requireMarker(text_expected_checksum_payload_labels, marker);
    const text_expected_checksum_ipv4_fast_path_labels_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_expected_checksum_ipv4_fast_path_labels_path);
    const text_expected_checksum_ipv4_fast_path_labels = try guard.readUtf8File(io, allocator, text_expected_checksum_ipv4_fast_path_labels_path);
    defer allocator.free(text_expected_checksum_ipv4_fast_path_labels);
    for (EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS) |marker| try guard.requireMarker(text_expected_checksum_ipv4_fast_path_labels, marker);
    const text_expected_hexdump_labels_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-perf-gate-survey.md");
    defer allocator.free(text_expected_hexdump_labels_path);
    const text_expected_hexdump_labels = try guard.readUtf8File(io, allocator, text_expected_hexdump_labels_path);
    defer allocator.free(text_expected_hexdump_labels);
    for (EXPECTED_HEXDUMP_LABELS) |marker| try guard.requireMarker(text_expected_hexdump_labels, marker);
    const text_expected_bsearch_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_bsearch_cases_path);
    const text_expected_bsearch_cases = try guard.readUtf8File(io, allocator, text_expected_bsearch_cases_path);
    defer allocator.free(text_expected_bsearch_cases);
    for (EXPECTED_BSEARCH_CASES) |marker| try guard.requireMarker(text_expected_bsearch_cases, marker);
    const text_expected_checksum_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_checksum_cases_path);
    const text_expected_checksum_cases = try guard.readUtf8File(io, allocator, text_expected_checksum_cases_path);
    defer allocator.free(text_expected_checksum_cases);
    for (EXPECTED_CHECKSUM_CASES) |marker| try guard.requireMarker(text_expected_checksum_cases, marker);
    const text_expected_checksum_ipv4_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_checksum_ipv4_cases_path);
    const text_expected_checksum_ipv4_cases = try guard.readUtf8File(io, allocator, text_expected_checksum_ipv4_cases_path);
    defer allocator.free(text_expected_checksum_ipv4_cases);
    for (EXPECTED_CHECKSUM_IPV4_CASES) |marker| try guard.requireMarker(text_expected_checksum_ipv4_cases, marker);
    const text_expected_hexdump_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_hexdump_cases_path);
    const text_expected_hexdump_cases = try guard.readUtf8File(io, allocator, text_expected_hexdump_cases_path);
    defer allocator.free(text_expected_hexdump_cases);
    for (EXPECTED_HEXDUMP_CASES) |marker| try guard.requireMarker(text_expected_hexdump_cases, marker);
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

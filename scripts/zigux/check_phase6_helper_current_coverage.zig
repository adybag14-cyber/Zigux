const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_HELPER_CURRENT_COVERAGE=pass";
pub const self_test_pass_marker = "PHASE6_HELPER_CURRENT_COVERAGE_SELF_TEST=pass";

const EXPECTED_PACKET = [_][]const u8{
    "phase6-helper-parity-current-coverage",
};

const EXPECTED_SURVEYED_HEAD = [_][]const u8{
    "current-master-readback-2026-05-27",
};

const EXPECTED_LANE_SCOPE = [_][]const u8{
    "exact helper coverage verification for the current Phase 6 parity packet",
};

const EXPECTED_PARENT_CATALOG = [_][]const u8{
    "Documentation/zigux/phase6-helper-parity-catalog.md",
};

const EXPECTED_COVERAGE_VERDICT = [_][]const u8{
    "All four roadmap-backed Phase 6 helper destinations are present on current master, each helper body carries embedded tests, and each helper keeps a focused replay plus a dedicated parity, perf, or route-check companion.",
};

const EXPECTED_ROADMAP_ANCHORS = [_][]const u8{
    "lib/base64.c",
    "lib/bsearch.c",
    "lib/checksum.c",
    "lib/hexdump.c",
};

const EXPECTED_HELPERS = [_][]const u8{
    "{key:base64",
    "roadmap_anchor:lib/base64.c",
    "zig_helper:lib/base64.zig",
    "helper_blob_sha:844a091999aab9a1d78f90d7719450b4e590e962",
    "embedded_helper_test_count:20",
    "selected_embedded_tests:variant-pinned convenience helpers mirror the generic apiencode and decode sweep every one-byte and two-byte tail across variants and padding modesdecode reverse maps classify every byte across all variants",
    "focused_replay:zigux/tests/phase6_base64.zig",
    "exact_companions:zigux/tests/phase6_base64_perf.zigzigux/tests/phase6_base64_c_parity.zigzigux/tests/fixtures/phase6_base64_c_harness.czigux/tests/fixtures/phase6_base64_c_parity_vectors.zigzigux/tests/phase6_base64_c_casegen.zigscripts\\zigux/check_phase6_base64_c_parity.zig",
    "}",
    "{key:bsearch",
    "roadmap_anchor:lib/bsearch.c",
    "zig_helper:lib/bsearch.zig",
    "helper_blob_sha:916a87eb91c0c3e620cf6e85c018180cdf772e58",
    "embedded_helper_test_count:11",
    "selected_embedded_tests:typed and raw searches support duplicate spans and descending C ABI pointersnative std.math.Order comparator pointers keep duplicate spans and insertion points alignedmutable wrappers keep write-through aliases with runtime-selected c abi comparator pointers",
    "focused_replay:zigux/tests/phase6_bsearch.zig",
    "exact_companions:zigux/tests/phase6_bsearch_perf.zigzigux/tests/phase6_bsearch_c_parity.zigzigux/tests/phase6_bsearch_lower_bound_c_abi.zigzigux/tests/phase6_bsearch_c_abi_budget.zigzigux/tests/fixtures/phase6_bsearch_c_harness.cscripts\\zigux/check_phase6_bsearch_c_parity.zig",
    "}",
    "{key:checksum",
    "roadmap_anchor:lib/checksum.c",
    "zig_helper:lib/checksum.zig",
    "helper_blob_sha:1cda59b1bd4e5d4e9989d2b9f4e84be62b8ccb7e",
    "embedded_helper_test_count:12",
    "selected_embedded_tests:partial and compute match reference accumulation across seeded odd payloadspseudo-header helpers match direct checksum recomputation over pseudo-header bytes and payloadipFastCsum stays aligned with compute across aligned IPv4 headers",
    "focused_replay:zigux/tests/phase6_checksum.zig",
    "exact_companions:zigux/tests/phase6_checksum_perf.zigzigux/tests/phase6_checksum_c_parity.zigzigux/tests/fixtures/phase6_checksum_c_harness.cscripts\\zigux/check_phase6_checksum_c_parity.zig",
    "}",
    "{key:hexdump",
    "roadmap_anchor:lib/hexdump.c",
    "zig_helper:lib/hexdump.zig",
    "helper_blob_sha:0fc9534ddf7e020ab00f981d5762b1703430170c",
    "embedded_helper_test_count:17",
    "selected_embedded_tests:hexDumpToBuffer matches the kernel-style 16-byte line outputhexDumpToBuffer uses native-endian grouping for 2, 4, and 8 byte groupshexDumpToBuffer follows kernel fixture normalization cases",
    "focused_replay:zigux/tests/phase6_hexdump.zig",
    "exact_companions:zigux/tests/phase6_hexdump_perf.zigzigux/tests/phase6_hexdump_perf_matrix.zigzigux/tests/phase6_hexdump_c_parity.zigzigux/tests/fixtures/phase6_hexdump_c_harness.cscripts\\zigux/check_phase6_hexdump_c_parity.zigscripts\\zigux/check_phase6_hexdump_packet.zigscripts\\zigux/check_phase6_hexdump_route.zig",
    "}",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-parity-current-coverage.md");
    defer allocator.free(text_expected_packet_path);
    const text_expected_packet = try guard.readUtf8File(io, allocator, text_expected_packet_path);
    defer allocator.free(text_expected_packet);
    for (EXPECTED_PACKET) |marker| try guard.requireMarker(text_expected_packet, marker);
    const text_expected_surveyed_head_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-parity-current-coverage.md");
    defer allocator.free(text_expected_surveyed_head_path);
    const text_expected_surveyed_head = try guard.readUtf8File(io, allocator, text_expected_surveyed_head_path);
    defer allocator.free(text_expected_surveyed_head);
    for (EXPECTED_SURVEYED_HEAD) |marker| try guard.requireMarker(text_expected_surveyed_head, marker);
    const text_expected_lane_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-parity-current-coverage.md");
    defer allocator.free(text_expected_lane_scope_path);
    const text_expected_lane_scope = try guard.readUtf8File(io, allocator, text_expected_lane_scope_path);
    defer allocator.free(text_expected_lane_scope);
    for (EXPECTED_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_lane_scope, marker);
    const text_expected_parent_catalog_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-parity-current-coverage.md");
    defer allocator.free(text_expected_parent_catalog_path);
    const text_expected_parent_catalog = try guard.readUtf8File(io, allocator, text_expected_parent_catalog_path);
    defer allocator.free(text_expected_parent_catalog);
    for (EXPECTED_PARENT_CATALOG) |marker| try guard.requireMarker(text_expected_parent_catalog, marker);
    const text_expected_coverage_verdict_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-parity-current-coverage.md");
    defer allocator.free(text_expected_coverage_verdict_path);
    const text_expected_coverage_verdict = try guard.readUtf8File(io, allocator, text_expected_coverage_verdict_path);
    defer allocator.free(text_expected_coverage_verdict);
    for (EXPECTED_COVERAGE_VERDICT) |marker| try guard.requireMarker(text_expected_coverage_verdict, marker);
    const text_expected_roadmap_anchors_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-parity-current-coverage.md");
    defer allocator.free(text_expected_roadmap_anchors_path);
    const text_expected_roadmap_anchors = try guard.readUtf8File(io, allocator, text_expected_roadmap_anchors_path);
    defer allocator.free(text_expected_roadmap_anchors);
    for (EXPECTED_ROADMAP_ANCHORS) |marker| try guard.requireMarker(text_expected_roadmap_anchors, marker);
    const text_expected_helpers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_expected_helpers_path);
    const text_expected_helpers = try guard.readUtf8File(io, allocator, text_expected_helpers_path);
    defer allocator.free(text_expected_helpers);
    for (EXPECTED_HELPERS) |marker| try guard.requireMarker(text_expected_helpers, marker);
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

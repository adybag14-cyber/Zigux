const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_SHARED_SURVEYED_HEAD=pass";
pub const self_test_pass_marker = "PHASE6_SHARED_SURVEYED_HEAD_SELF_TEST=pass";

const EXPECTED_PACKET = [_][]const u8{
    "phase6-helper-evidence",
};

const EXPECTED_PARITY_PACKET = [_][]const u8{
    "phase6-helper-parity",
};

const EXPECTED_EVIDENCE_LANE_SCOPE = [_][]const u8{
    "shared helper-evidence rows and machine-readable manifest only",
};

const EXPECTED_PARITY_LANE_SCOPE = [_][]const u8{
    "shared helper-parity rows and machine-readable manifest only",
};

const EXPECTED_ROADMAP_ANCHORS = [_][]const u8{
    "lib/base64.c",
    "lib/bsearch.c",
    "lib/checksum.c",
    "lib/hexdump.c",
};

const EXPECTED_DIRECT_COMPANIONS = [_][]const u8{
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

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-evidence-catalog.md");
    defer allocator.free(text_expected_packet_path);
    const text_expected_packet = try guard.readUtf8File(io, allocator, text_expected_packet_path);
    defer allocator.free(text_expected_packet);
    for (EXPECTED_PACKET) |marker| try guard.requireMarker(text_expected_packet, marker);
    const text_expected_parity_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-evidence-catalog.md");
    defer allocator.free(text_expected_parity_packet_path);
    const text_expected_parity_packet = try guard.readUtf8File(io, allocator, text_expected_parity_packet_path);
    defer allocator.free(text_expected_parity_packet);
    for (EXPECTED_PARITY_PACKET) |marker| try guard.requireMarker(text_expected_parity_packet, marker);
    const text_expected_evidence_lane_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-evidence-catalog.md");
    defer allocator.free(text_expected_evidence_lane_scope_path);
    const text_expected_evidence_lane_scope = try guard.readUtf8File(io, allocator, text_expected_evidence_lane_scope_path);
    defer allocator.free(text_expected_evidence_lane_scope);
    for (EXPECTED_EVIDENCE_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_evidence_lane_scope, marker);
    const text_expected_parity_lane_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-evidence-catalog.md");
    defer allocator.free(text_expected_parity_lane_scope_path);
    const text_expected_parity_lane_scope = try guard.readUtf8File(io, allocator, text_expected_parity_lane_scope_path);
    defer allocator.free(text_expected_parity_lane_scope);
    for (EXPECTED_PARITY_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_parity_lane_scope, marker);
    const text_expected_roadmap_anchors_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-evidence-catalog.md");
    defer allocator.free(text_expected_roadmap_anchors_path);
    const text_expected_roadmap_anchors = try guard.readUtf8File(io, allocator, text_expected_roadmap_anchors_path);
    defer allocator.free(text_expected_roadmap_anchors);
    for (EXPECTED_ROADMAP_ANCHORS) |marker| try guard.requireMarker(text_expected_roadmap_anchors, marker);
    const text_expected_direct_companions_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-evidence-catalog.md");
    defer allocator.free(text_expected_direct_companions_path);
    const text_expected_direct_companions = try guard.readUtf8File(io, allocator, text_expected_direct_companions_path);
    defer allocator.free(text_expected_direct_companions);
    for (EXPECTED_DIRECT_COMPANIONS) |marker| try guard.requireMarker(text_expected_direct_companions, marker);
    const text_expected_shared_direct_evidence_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-helper-evidence-catalog.md");
    defer allocator.free(text_expected_shared_direct_evidence_path);
    const text_expected_shared_direct_evidence = try guard.readUtf8File(io, allocator, text_expected_shared_direct_evidence_path);
    defer allocator.free(text_expected_shared_direct_evidence);
    for (EXPECTED_SHARED_DIRECT_EVIDENCE) |marker| try guard.requireMarker(text_expected_shared_direct_evidence, marker);
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

const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_SHARED_REPLAY_INVENTORY=pass";
pub const self_test_pass_marker = "PHASE6_SHARED_REPLAY_INVENTORY_SELF_TEST=pass";

const EXPECTED_PACKET = [_][]const u8{
    "phase6-helper-evidence",
};

const EXPECTED_PARITY_PACKET = [_][]const u8{
    "phase6-helper-parity",
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

const EXPECTED_DIRECT_COMPANION_CHECKERS = [_][]const u8{
    "scripts\\zigux/check_phase6_base64_bsearch_perf_markers.zig",
    "scripts\\zigux/check_phase6_checksum_hexdump_perf_markers.zig",
    "scripts\\zigux/check_phase6_perf_threshold_markers.zig",
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

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_packet_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_helper_evidence_manifest.json");
    defer allocator.free(text_expected_packet_path);
    const text_expected_packet = try guard.readUtf8File(io, allocator, text_expected_packet_path);
    defer allocator.free(text_expected_packet);
    for (EXPECTED_PACKET) |marker| try guard.requireMarker(text_expected_packet, marker);
    const text_expected_parity_packet_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_helper_evidence_manifest.json");
    defer allocator.free(text_expected_parity_packet_path);
    const text_expected_parity_packet = try guard.readUtf8File(io, allocator, text_expected_parity_packet_path);
    defer allocator.free(text_expected_parity_packet);
    for (EXPECTED_PARITY_PACKET) |marker| try guard.requireMarker(text_expected_parity_packet, marker);
    const text_expected_surveyed_head_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_helper_evidence_manifest.json");
    defer allocator.free(text_expected_surveyed_head_path);
    const text_expected_surveyed_head = try guard.readUtf8File(io, allocator, text_expected_surveyed_head_path);
    defer allocator.free(text_expected_surveyed_head);
    for (EXPECTED_SURVEYED_HEAD) |marker| try guard.requireMarker(text_expected_surveyed_head, marker);
    const text_expected_evidence_lane_scope_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_helper_evidence_manifest.json");
    defer allocator.free(text_expected_evidence_lane_scope_path);
    const text_expected_evidence_lane_scope = try guard.readUtf8File(io, allocator, text_expected_evidence_lane_scope_path);
    defer allocator.free(text_expected_evidence_lane_scope);
    for (EXPECTED_EVIDENCE_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_evidence_lane_scope, marker);
    const text_expected_parity_lane_scope_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_helper_evidence_manifest.json");
    defer allocator.free(text_expected_parity_lane_scope_path);
    const text_expected_parity_lane_scope = try guard.readUtf8File(io, allocator, text_expected_parity_lane_scope_path);
    defer allocator.free(text_expected_parity_lane_scope);
    for (EXPECTED_PARITY_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_parity_lane_scope, marker);
    const text_expected_direct_companion_checkers_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_helper_evidence_manifest.json");
    defer allocator.free(text_expected_direct_companion_checkers_path);
    const text_expected_direct_companion_checkers = try guard.readUtf8File(io, allocator, text_expected_direct_companion_checkers_path);
    defer allocator.free(text_expected_direct_companion_checkers);
    for (EXPECTED_DIRECT_COMPANION_CHECKERS) |marker| try guard.requireMarker(text_expected_direct_companion_checkers, marker);
    const text_expected_shared_replay_inventory_path = try guard.joinPath(allocator, root, "zigux/tests/phase6_helper_evidence_manifest.json");
    defer allocator.free(text_expected_shared_replay_inventory_path);
    const text_expected_shared_replay_inventory = try guard.readUtf8File(io, allocator, text_expected_shared_replay_inventory_path);
    defer allocator.free(text_expected_shared_replay_inventory);
    for (EXPECTED_SHARED_REPLAY_INVENTORY) |marker| try guard.requireMarker(text_expected_shared_replay_inventory, marker);
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

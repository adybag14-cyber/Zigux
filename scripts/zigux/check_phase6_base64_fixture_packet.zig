const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_BASE64_FIXTURE_PACKET=pass";
pub const self_test_pass_marker = "PHASE6_BASE64_FIXTURE_PACKET_SELF_TEST=pass";

const EXPECTED_SLICE_SNIPPETS = [_][]const u8{
    "- helper-local corpus checker: `scripts\\zigux/check_phase6_base64_corpus_determinism.zig`",
    "- exact fixture-owned corpus counts on current `master`: 22 standard encode cases, 18 variant encode cases, 22 standard decode cases, 18 variant decode cases, 16 invalid decode cases, and 6 perf replay cases, all centralized in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by `zigux/tests/phase6_base64.zig` or `zigux/tests/phase6_base64_perf.zig`",
    "- exact helper-local perf replay packet: ordered labels `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each with `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, owned once in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by the helper-local perf gate",
};

const EXPECTED_FIXTURE_SURFACES = [_][]const u8{
    "zigux/tests/fixtures/phase6_base64_vectors.zig",
};

const EXPECTED_CHECKER_SURFACES = [_][]const u8{
    "scripts\\zigux/check_phase6_base64_corpus_determinism.zig",
};

const EXPECTED_MISSING_COMPANIONS = [_][]const u8{
    "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/phase6_base64_c_casegen.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "scripts\\zigux/check_phase6_base64_c_parity.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_slice_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-base64-slice.md");
    defer allocator.free(text_expected_slice_snippets_path);
    const text_expected_slice_snippets = try guard.readUtf8File(io, allocator, text_expected_slice_snippets_path);
    defer allocator.free(text_expected_slice_snippets);
    for (EXPECTED_SLICE_SNIPPETS) |marker| try guard.requireMarker(text_expected_slice_snippets, marker);
    const text_expected_fixture_surfaces_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-base64-slice.md");
    defer allocator.free(text_expected_fixture_surfaces_path);
    const text_expected_fixture_surfaces = try guard.readUtf8File(io, allocator, text_expected_fixture_surfaces_path);
    defer allocator.free(text_expected_fixture_surfaces);
    for (EXPECTED_FIXTURE_SURFACES) |marker| try guard.requireMarker(text_expected_fixture_surfaces, marker);
    const text_expected_checker_surfaces_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-base64-slice.md");
    defer allocator.free(text_expected_checker_surfaces_path);
    const text_expected_checker_surfaces = try guard.readUtf8File(io, allocator, text_expected_checker_surfaces_path);
    defer allocator.free(text_expected_checker_surfaces);
    for (EXPECTED_CHECKER_SURFACES) |marker| try guard.requireMarker(text_expected_checker_surfaces, marker);
    const text_expected_missing_companions_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-base64-slice.md");
    defer allocator.free(text_expected_missing_companions_path);
    const text_expected_missing_companions = try guard.readUtf8File(io, allocator, text_expected_missing_companions_path);
    defer allocator.free(text_expected_missing_companions);
    for (EXPECTED_MISSING_COMPANIONS) |marker| try guard.requireMarker(text_expected_missing_companions, marker);
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

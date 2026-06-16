const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_BASE64_CORPUS_DETERMINISM=pass";
pub const self_test_pass_marker = "PHASE6_BASE64_CORPUS_DETERMINISM_SELF_TEST=pass";

const EXPECTED_PERF_LABELS = [_][]const u8{
    "STD_PAD",
    "STD_NO_PAD",
    "URLSAFE_PAD",
    "URLSAFE_NO_PAD",
    "IMAP_PAD",
    "IMAP_NO_PAD",
};

const EXPECTED_SLICE_SNIPPETS = [_][]const u8{
    "- shared kernel-derived encode, decode, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig` and consumed directly by `zigux/tests/phase6_base64.zig`",
    "- exact fixture-owned corpus counts on current `master`: 22 standard encode cases, 18 variant encode cases, 22 standard decode cases, 18 variant decode cases, 16 invalid decode cases, and 6 perf replay cases, all centralized in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by `zigux/tests/phase6_base64.zig` or `zigux/tests/phase6_base64_perf.zig`",
    "- helper-local corpus checker: `scripts\\zigux/check_phase6_base64_corpus_determinism.zig`",
    "- a representative external C-vs-Zig portability replay through `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts\\zigux/check_phase6_base64_c_parity.zig`, covering standard padded and unpadded cases plus URL-safe, IMAP, and malformed decode spot checks",
};

const EXPECTED_HELPER_TEST_SNIPPETS = [_][]const u8{
    "const fixtures = @import(\"fixtures/phase6_base64_vectors.zig\");",
    "for (fixtures.standard_cases) |case| {",
    "for (fixtures.variant_cases) |case| {",
    "for (fixtures.standard_decode_cases) |case| {",
    "for (fixtures.invalid_decode_cases) |case| {",
    "for (fixtures.variant_decode_cases) |case| {",
};

const EXPECTED_PERF_TEST_SNIPPETS = [_][]const u8{
    "const fixtures = @import(\"fixtures/phase6_base64_vectors.zig\");",
    "fn validatePerfMatrix() !void {",
    "for (fixtures.perf_cases, 0..) |case, idx| {",
    "try validatePerfMatrix();",
};

const EXPECTED_C_PARITY_TEST_SNIPPETS = [_][]const u8{
    "const parity = @import(\"fixtures/phase6_base64_c_parity_vectors.zig\");",
    "for (parity.encode_cases) |case| {",
    "for (parity.decode_cases) |case| {",
    "for (parity.invalid_cases) |case| {",
};

const EXPECTED_CASEGEN_SNIPPETS = [_][]const u8{
    "const shared = @import(\"fixtures/phase6_base64_vectors.zig\");",
    "const parity = @import(\"fixtures/phase6_base64_c_parity_vectors.zig\");",
    "for (parity.encode_cases) |case| {",
    "for (parity.decode_cases) |case| {",
    "for (parity.invalid_cases) |case| {",
    "try std.testing.expectEqual(@as(usize, 40), line_count);",
};

const EXPECTED_PARITY_SHIM = [_][]const u8{
    "pub usingnamespace @import(\"fixtures/phase6_base64_c_parity_vectors.zig\");\n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_perf_labels_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-base64-slice.md");
    defer allocator.free(text_expected_perf_labels_path);
    const text_expected_perf_labels = try guard.readUtf8File(io, allocator, text_expected_perf_labels_path);
    defer allocator.free(text_expected_perf_labels);
    for (EXPECTED_PERF_LABELS) |marker| try guard.requireMarker(text_expected_perf_labels, marker);
    const text_expected_slice_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-base64-slice.md");
    defer allocator.free(text_expected_slice_snippets_path);
    const text_expected_slice_snippets = try guard.readUtf8File(io, allocator, text_expected_slice_snippets_path);
    defer allocator.free(text_expected_slice_snippets);
    for (EXPECTED_SLICE_SNIPPETS) |marker| try guard.requireMarker(text_expected_slice_snippets, marker);
    const text_expected_helper_test_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-base64-slice.md");
    defer allocator.free(text_expected_helper_test_snippets_path);
    const text_expected_helper_test_snippets = try guard.readUtf8File(io, allocator, text_expected_helper_test_snippets_path);
    defer allocator.free(text_expected_helper_test_snippets);
    for (EXPECTED_HELPER_TEST_SNIPPETS) |marker| try guard.requireMarker(text_expected_helper_test_snippets, marker);
    const text_expected_perf_test_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-base64-slice.md");
    defer allocator.free(text_expected_perf_test_snippets_path);
    const text_expected_perf_test_snippets = try guard.readUtf8File(io, allocator, text_expected_perf_test_snippets_path);
    defer allocator.free(text_expected_perf_test_snippets);
    for (EXPECTED_PERF_TEST_SNIPPETS) |marker| try guard.requireMarker(text_expected_perf_test_snippets, marker);
    const text_expected_c_parity_test_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-base64-slice.md");
    defer allocator.free(text_expected_c_parity_test_snippets_path);
    const text_expected_c_parity_test_snippets = try guard.readUtf8File(io, allocator, text_expected_c_parity_test_snippets_path);
    defer allocator.free(text_expected_c_parity_test_snippets);
    for (EXPECTED_C_PARITY_TEST_SNIPPETS) |marker| try guard.requireMarker(text_expected_c_parity_test_snippets, marker);
    const text_expected_casegen_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-base64-slice.md");
    defer allocator.free(text_expected_casegen_snippets_path);
    const text_expected_casegen_snippets = try guard.readUtf8File(io, allocator, text_expected_casegen_snippets_path);
    defer allocator.free(text_expected_casegen_snippets);
    for (EXPECTED_CASEGEN_SNIPPETS) |marker| try guard.requireMarker(text_expected_casegen_snippets, marker);
    const text_expected_parity_shim_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-base64-slice.md");
    defer allocator.free(text_expected_parity_shim_path);
    const text_expected_parity_shim = try guard.readUtf8File(io, allocator, text_expected_parity_shim_path);
    defer allocator.free(text_expected_parity_shim);
    for (EXPECTED_PARITY_SHIM) |marker| try guard.requireMarker(text_expected_parity_shim, marker);
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

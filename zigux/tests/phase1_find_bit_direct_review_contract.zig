const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase 1 closure keeps find_bit direct review parked and helper-local" {
    const closure = try readRepoFile("Documentation/zigux/phase1-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "For `tools/lib/find_bit.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass.");
    try expectContains(closure, "The shipped direct anchors already cover same-word start-mask scans, head-word and tail-word inclusive-boundary starts, single-word tail inclusive-boundary reachability");
    try expectContains(closure, "byte-aligned `clump8` forward-skip behavior");
    try expectContains(closure, "final-word last-aligned-byte isolation for both `clump8` and `getValue8()`");
    try expectContains(closure, "the public, Linux-style, and underscore alias surfaces including the shipped `andnot` scan entry points");
    try expectContains(closure, "This helper should only reopen if a fresh reread finds drift in those direct anchors or in the committed shared find-bit parity fields");
    try expectContains(closure, "do not widen this helper-local reminder into older closure-side validator names by default");
}

test "phase 1 closure keeps the find_bit tie breaker narrow" {
    const closure = try readRepoFile("Documentation/zigux/phase1-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route");
    try expectContains(closure, "keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors");
    try expectContains(closure, "zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors");
    try expectContains(closure, "do not reopen older validator-first cues or neighboring helper families by default");
    try expectContains(closure, "helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`");
    try expectContains(closure, "`clump8 past-end scans return without reading bitmap words` no-read anchor");
    try expectContains(closure, "find first and next set bits across words, with andnot gaps explicit");
    try expectContains(closure, "including andnot");
}

test "phase 1 manifest keeps the find_bit direct anchors named" {
    const manifest = try readRepoFile("zigux/tests/fixtures/phase1_helper_manifest.json", 128 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"tools/lib/find_bit.zig\"");
    try expectContains(manifest, "test \\\"find first and next set bits across words, with andnot gaps explicit\\\"");
    try expectContains(manifest, "test \\\"single-word next scans honor start masks\\\"");
    try expectContains(manifest, "test \\\"single-word tail windows keep the last in-range next matches reachable from an inclusive start\\\"");
    try expectContains(manifest, "test \\\"clump8 past-end scans return without reading bitmap words\\\"");
    try expectContains(manifest, "test \\\"getValue8 reads the last aligned byte of a word without folding in the next word\\\"");
    try expectContains(manifest, "test \\\"low-level underscore aliases mirror the primary find helpers, including andnot\\\"");
    try expectContains(manifest, "test \\\"Linux-style aliases mirror the primary find helpers, including andnot\\\"");
    try expectContains(manifest, "\"andnot_scan_entrypoints\"");
    try expectContains(manifest, "\"single_word_tail_inclusive_boundary_anchor\"");
    try expectContains(manifest, "helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary");
}

test "tools lib find_bit keeps the direct review anchors executable" {
    const helper = try readRepoFile("tools/lib/find_bit.zig", 128 * 1024);
    defer std.testing.allocator.free(helper);

    try expectContains(helper, "test \"find first and next set bits across words, with andnot gaps explicit\"");
    try expectContains(helper, "test \"single-word next scans honor start masks\"");
    try expectContains(helper, "test \"single-word tail windows keep the last in-range next matches reachable from an inclusive start\"");
    try expectContains(helper, "test \"clump8 past-end scans return without reading bitmap words\"");
    try expectContains(helper, "test \"getValue8 reads the last aligned byte of a word without folding in the next word\"");
    try expectContains(helper, "test \"low-level underscore aliases mirror the primary find helpers, including andnot\"");
    try expectContains(helper, "test \"Linux-style aliases mirror the primary find helpers, including andnot\"");
    try expectContains(helper, "pub fn findFirstAndNotBit");
    try expectContains(helper, "pub fn find_first_andnot_bit");
    try expectContains(helper, "pub fn _find_next_andnot_bit");
}

test "find_bit direct review contract rejects stale generic alias wording" {
    const manifest = try readRepoFile("zigux/tests/fixtures/phase1_helper_manifest.json", 128 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectNotContains(manifest, "\"linux_alias_anchor\": \"test \\\"Linux-style aliases mirror the primary find helpers\\\"\"");
    try expectNotContains(manifest, "\"underscore_alias_anchor\": \"test \\\"low-level underscore aliases mirror the primary find helpers\\\"\"");
}

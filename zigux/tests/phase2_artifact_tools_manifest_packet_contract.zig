const std = @import("std");
const testing = std.testing;

const artifact_manifest_paths = [_][]const u8{
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
};

const artifact_consumers = [_][]const u8{
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-fixdep-diff.py",
};

const manifest_notes = [_][]const u8{
    "The artifact diff helper provides deterministic comparison output for fixture-backed scripts-root checks in both the kconfig bridge and fixdep parity packets.",
    "Keep `scripts/zigux/check-phase2-artifact-tools-manifest.py` explicit so the bounded Phase 2 artifact-support manifest fails closed beside the broader Phase 2 tool packet.",
    "Keep future Phase 2 artifact-diff follow-up bounded to live consumers like `scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-fixdep-diff.py` plus directly readable fixture packets before widening into broader closure routes.",
    "Keep the legacy `sha256` compatibility alias explicit as the path that normalizes to the shipped `bytes` comparison surface in `scripts/zigux/artifact_diff.py`.",
};

fn readText(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn requireExactOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try testing.expectEqual(@as(usize, 1), count);
}

test "phase2 docs and review surfaces keep artifact tools manifest visible" {
    const docs_readme = try readText("Documentation/zigux/README.md");
    defer testing.allocator.free(docs_readme);
    const review_checklist = try readText("Documentation/zigux/review-checklist.md");
    defer testing.allocator.free(review_checklist);
    const scripts_readme = try readText("scripts/zigux/README.md");
    defer testing.allocator.free(scripts_readme);
    const tests_readme = try readText("zigux/tests/README.md");
    defer testing.allocator.free(tests_readme);

    for (artifact_manifest_paths) |path| {
        try requireContains(docs_readme, path);
        try requireContains(review_checklist, path);
        try requireContains(scripts_readme, path);
        try requireContains(tests_readme, path);
    }

    try requireContains(docs_readme, "artifact-tools");
    try requireContains(review_checklist, "artifact-support");
    try requireContains(scripts_readme, "artifact-support");
    try requireContains(tests_readme, "artifact-tools");
}

test "phase2 artifact manifest pins helper consumers and supported modes" {
    const manifest = try readText("zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    defer testing.allocator.free(manifest);
    const checker = try readText("scripts/zigux/check-phase2-artifact-tools-manifest.py");
    defer testing.allocator.free(checker);

    try requireContains(manifest, "\"phase\": \"Phase 2\"");
    try requireContains(manifest, "\"status\": \"active\"");
    try requireContains(manifest, "\"scope\": \"artifact-diff support for fixture-backed scripts/zigux validation\"");
    try requireContains(manifest, "\"supported_modes\": [\n      \"text\",\n      \"json\",\n      \"bytes\"\n    ]");

    for (artifact_consumers) |path| {
        try requireContains(manifest, path);
        try requireContains(checker, path);
    }

    try requireContains(checker, "PRIMARY_TOOL_MARKERS");
    try requireContains(checker, "EXPECTED_CONSUMER_MARKERS");
    try requireContains(checker, "load_primary_tool_supported_modes");
    try requireContains(checker, "PHASE2_ARTIFACT_TOOLS_MANIFEST=pass");
}

test "phase2 artifact notes stay exact and ordered" {
    const manifest = try readText("zigux/tests/fixtures/phase2_artifact_tools_manifest.json");
    defer testing.allocator.free(manifest);
    const checker = try readText("scripts/zigux/check-phase2-artifact-tools-manifest.py");
    defer testing.allocator.free(checker);

    for (manifest_notes) |note| {
        try requireContains(manifest, note);
        try requireContains(checker, note);
        try requireExactOnce(manifest, note);
    }

    try requireOrdered(manifest, manifest_notes[0], manifest_notes[1]);
    try requireOrdered(manifest, manifest_notes[1], manifest_notes[2]);
    try requireOrdered(manifest, manifest_notes[2], manifest_notes[3]);
}

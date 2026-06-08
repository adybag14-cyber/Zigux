const std = @import("std");
const testing = std.testing;

const max_file_size = 4 * 1024 * 1024;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "docs root and checklist keep Phase 3 substrate packet explicit" {
    const allocator = testing.allocator;

    const docs_root = try readFile(allocator, "Documentation/zigux/README.md");
    defer allocator.free(docs_root);
    const checklist = try readFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(checklist);

    try requireContains(docs_root, "Phase 3 notes");
    try requireContains(docs_root, "Documentation/zigux/phase3-validator-support-surface.md");
    try requireContains(docs_root, "Documentation/zigux/phase3-export-uapi-boundary-survey.md");
    try requireContains(docs_root, "Documentation/zigux/phase3-abi-header-family-survey.md");
    try requireContains(docs_root, "Documentation/zigux/phase3-bitmap-cpumask-slice.md");
    try requireContains(docs_root, "Documentation/zigux/phase3-list-hlist-slice.md");
    try requireContains(docs_root, "zigux/tests/fixtures/phase3_abi_manifest.json");
    try requireContains(docs_root, "make -C zigux phase3-export-uapi-layout-test");
    try requireContains(docs_root, "broader shared replay or header-family completion claims");

    try requireContains(checklist, "if the change touches the shared Phase 3 ABI/runtime packet");
    try requireContains(checklist, "Documentation/zigux/phase3-validator-support-surface.md");
    try requireContains(checklist, "scripts/zigux/check-phase3-bitmap-cpumask.py");
    try requireContains(checklist, "zigux/tests/phase3_export_uapi_c_header_smoke.c");
    try requireContains(checklist, "keep any broader shared replay or broader header-family completion claims framed as repo-reality gaps");
}

test "validator support and export survey agree on bounded current surfaces" {
    const allocator = testing.allocator;

    const support = try readFile(allocator, "Documentation/zigux/phase3-validator-support-surface.md");
    defer allocator.free(support);
    const export_survey = try readFile(allocator, "Documentation/zigux/phase3-export-uapi-boundary-survey.md");
    defer allocator.free(export_survey);

    try requireContains(support, "one bounded `dev_t` starter packet");
    try requireContains(support, "one focused helper-local `err_ptr` / `xarray` interop slice");
    try requireContains(support, "one focused helper-local `xarray_slot` classifier slice");
    try requireContains(support, "one focused helper-local `idr_slot` classifier slice");
    try requireContains(support, "one bounded helper-local `bitmap` / `cpumask` starter slice");
    try requireContains(support, "one bounded helper-local `list_head` / `hlist` starter-plus-dump slice");
    try requireContains(support, "one adjacent export/UAPI layout replay pair");
    try requireContains(support, "Do not treat this bounded packet as the broader export/UAPI survey, catalog, or shared Phase 3 replay packet.");

    try requireContains(export_survey, "PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig");
    try requireContains(export_survey, "PHASE3_ABI_H_PATH=include/zigux/abi.h");
    try requireContains(export_survey, "PHASE3_LAYOUT_REPLAY_PATH=zigux/tests/phase3_export_uapi_layout.zig");
    try requireContains(export_survey, "PHASE3_C_HEADER_SMOKE_PATH=zigux/tests/phase3_export_uapi_c_header_smoke.c");
    try requireContains(export_survey, "PHASE3_ABI_EXPORT_MAKE_ROUTE=make -C zigux phase3-abi-export");
    try requireContains(export_survey, "broader curated UAPI families and wider export-shim coverage");
    try requireOrder(export_survey, "## Status Markers", "## Current Boundary Gap");
}

test "scripts tests and manifest keep retired generated dump outside active packet" {
    const allocator = testing.allocator;

    const scripts_readme = try readFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    const tests_readme = try readFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);
    const manifest = try readFile(allocator, "zigux/tests/fixtures/phase3_abi_manifest.json");
    defer allocator.free(manifest);

    try requireContains(scripts_readme, "Phase 3 flow - the current scripts-root reminder packet");
    try requireContains(scripts_readme, "make -C zigux phase3-abi-export");
    try requireContains(scripts_readme, "make -C zigux phase3-low-level-wrappers-test");
    try requireContains(scripts_readme, "broader subsystem ownership behavior");

    try requireContains(tests_readme, "## Phase 3 shared substrate packet");
    try requireContains(tests_readme, "current shared Phase 3 route: `make -C zigux phase3-validate`");
    try requireContains(tests_readme, "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig");
    try requireContains(tests_readme, "full interop parity remain outside");

    try requireContains(manifest, "\"current_dump\": \"zigux/tests/phase3_abi_dump_current.zig\"");
    try requireContains(manifest, "\"retired_dump\": \"zigux/tests/phase3_abi_dump.zig\"");
    try requireContains(manifest, "\"retired_expected_fixture\": \"zigux/tests/fixtures/phase3_abi/expected.json\"");
    try requireContains(manifest, "\"must_stay_out_of_packet_files\"");
    try requireContains(manifest, "\"must_stay_out_of_replay_routes\"");
    try requireContains(manifest, "\"repo_reality_gaps\": []");
    try requireNotContains(manifest, "\"replay_routes\": [\n    \"zigux/tests/phase3_abi_dump.zig\"");
}

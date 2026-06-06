const std = @import("std");

const validator_path = "scripts/zigux/validate-phase2-closure.py";
const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";
const closure_path = "Documentation/zigux/phase2-closure.md";

const optional_archive_path =
    "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const optional_parts_manifest_path =
    "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts/manifest.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

test "closure validator keeps legacy archive paths optional before missing-surface checks" {
    const allocator = std.testing.allocator;
    const validator = try readFile(allocator, validator_path);
    defer allocator.free(validator);

    try requireContains(validator, "OPTIONAL_MANIFEST_SURFACE_PATHS = {");
    try requireContains(validator, optional_archive_path);
    try requireContains(validator, optional_parts_manifest_path);
    try requireContains(
        validator,
        "if value in OPTIONAL_MANIFEST_SURFACE_PATHS and not (root / value).exists():",
    );
    try requireContains(validator, "continue");
    try requireContains(validator, "MISSING_MANIFEST_SURFACE");
    try requireBefore(
        validator,
        "if value in OPTIONAL_MANIFEST_SURFACE_PATHS and not (root / value).exists():",
        "issues.append((\"MISSING_MANIFEST_SURFACE\", f\"{key}:{value}\"))",
    );
}

test "tool manifest keeps archive support present without repo-reality gaps" {
    const allocator = std.testing.allocator;
    const manifest = try readFile(allocator, manifest_path);
    defer allocator.free(manifest);

    try requireContains(manifest, "\"archive_support\"");
    try requireContains(manifest, "\"third_party/README.md\"");
    try requireContains(manifest, optional_archive_path);
    try requireContains(manifest, "\"repo_reality_gaps\": []");
    try std.testing.expect(std.mem.indexOf(u8, manifest, optional_parts_manifest_path) == null);
}

test "closure note names the parked gap packet instead of treating optional archive as a gap" {
    const allocator = std.testing.allocator;
    const closure = try readFile(allocator, closure_path);
    defer allocator.free(closure);

    try requireContains(closure, "`PHASE2_STATUS=parked`");
    try requireContains(closure, "`PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`");
    try requireContains(closure, "kconfig bridge packet remains fixture-backed");
    try std.testing.expect(std.mem.indexOf(u8, closure, optional_parts_manifest_path) == null);
}
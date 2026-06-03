const std = @import("std");

const max_file_size = 256 * 1024;
const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";
const validator_path = "scripts/zigux/validate-phase2-closure.py";
const closure_path = "Documentation/zigux/phase2-closure.md";

const archive_name = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const archive_path = "third_party/" ++ archive_name;
const archive_parts_manifest_path = archive_path ++ ".parts/manifest.json";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(max_file_size),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase2 manifest keeps archive support explicit and narrow" {
    const allocator = std.testing.allocator;
    const manifest = try readFile(allocator, manifest_path);
    defer allocator.free(manifest);

    try expectContains(manifest, "\"archive_support\": [");
    try expectContains(manifest, "\"third_party/README.md\"");
    try expectContains(manifest, "\"" ++ archive_path ++ "\"");
    try expectNotContains(manifest, "\"" ++ archive_parts_manifest_path ++ "\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
}

test "closure validator treats missing archive payloads as optional surfaces only" {
    const allocator = std.testing.allocator;
    const validator = try readFile(allocator, validator_path);
    defer allocator.free(validator);

    try expectContains(validator, "OPTIONAL_MANIFEST_SURFACE_PATHS = {");
    try expectContains(validator, "\"" ++ archive_path ++ "\"");
    try expectContains(validator, "\"" ++ archive_parts_manifest_path ++ "\"");
    try expectContains(validator, "if value in OPTIONAL_MANIFEST_SURFACE_PATHS and not (root / value).exists():");
    try expectContains(validator, "continue");
}

test "closure note remains parked on the shared manifest packet" {
    const allocator = std.testing.allocator;
    const closure = try readFile(allocator, closure_path);
    defer allocator.free(closure);

    try expectContains(closure, "PHASE2_STATUS=parked");
    try expectContains(closure, "manifest: `" ++ manifest_path ++ "`");
    try expectContains(closure, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
}

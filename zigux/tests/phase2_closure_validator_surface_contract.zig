const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

const validator_pair_line =
    "PHASE2_CLOSURE_VALIDATORS=" ++
    "zig run scripts/zigux/validate_phase2.zig," ++
    "zig run scripts/zigux/validate_phase2_closure.zig";

const shared_routes_line =
    "PHASE2_SHARED_MAKE_ROUTES=" ++
    "make -C zigux phase2-toolchain," ++
    "make -C zigux phase2-tools," ++
    "make -C zigux phase2-kconfig," ++
    "make -C zigux phase2-cross," ++
    "make -C zigux phase2-genksyms," ++
    "make -C zigux phase2-fixdep," ++
    "make -C zigux phase2-validate," ++
    "make -C zigux phase2";

test "phase 2 closure note and manifest expose the validator pair as a public surface" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);

    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 256 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(closure_note, "shared validator pair: `zig run scripts/zigux/validate_phase2.zig` and `zig run scripts/zigux/validate_phase2_closure.zig`");
    try expectContains(closure_note, validator_pair_line);
    try expectContains(closure_note, shared_routes_line);
    try expectContains(manifest, "\"validators\": [");
    try expectContains(manifest, "\"scripts\zigux/validate_phase2.zig\"");
    try expectContains(manifest, "\"scripts\zigux/validate_phase2_closure.zig\"");
    try expectBefore(
        manifest,
        "\"scripts\zigux/validate_phase2.zig\"",
        "\"scripts\zigux/validate_phase2_closure.zig\"",
    );
}

test "phase 2 closure validator pins the required closure packet files" {
    const validator = try readRepoFile("scripts\zigux/validate_phase2_closure.zig", 128 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "PHASE2_CLOSURE_REL = Path(\"Documentation/zigux/phase2-closure.md\")");
    try expectContains(validator, "PHASE2_VALIDATE_REL = Path(\"scripts\zigux/validate_phase2.zig\")");
    try expectContains(validator, "PHASE2_CLOSURE_VALIDATE_REL = Path(\"scripts\zigux/validate_phase2_closure.zig\")");
    try expectContains(validator, "PHASE2_TOOL_MANIFEST_REL = Path(\"zigux/tests/fixtures/phase2_tool_manifest.json\")");
    try expectContains(validator, "PHASE2_ARTIFACT_TOOLS_MANIFEST_REL = Path(\"zigux/tests/fixtures/phase2_artifact_tools_manifest.json\")");
    try expectContains(validator, "GENKSYMS_MANIFEST_REL = Path(\"zigux/tests/fixtures/genksyms_bridge/manifest.json\")");
    try expectContains(validator, "\"MISSING_REQUIRED_FILE\"");
    try expectBefore(
        validator,
        "PHASE2_VALIDATE_REL,",
        "PHASE2_CLOSURE_VALIDATE_REL,",
    );
}

test "phase 2 closure validator keeps stable public result and failure markers" {
    const validator = try readRepoFile("scripts\zigux/validate_phase2_closure.zig", 128 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass");
    try expectContains(validator, "PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT=");
    try expectContains(validator, "PHASE2_CLOSURE_VALIDATION=fail");
    try expectContains(validator, "PHASE2_CLOSURE_VALIDATION=pass");
    try expectContains(validator, "PHASE2_CLOSURE_STATUS=parked");
    try expectContains(validator, "PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure");
    try expectContains(validator, "PHASE2_CLOSURE_REMAINING_GAPS=");
    try expectContains(validator, "MISSING_CLOSURE_LINE");
    try expectContains(validator, "MISSING_CLOSURE_MARKER");
    try expectContains(validator, "MISSING_MANIFEST_SURFACE");
    try expectBefore(
        validator,
        "print(\"PHASE2_CLOSURE_VALIDATION=pass\")",
        "print(\"PHASE2_CLOSURE_STATUS=parked\")",
    );
}

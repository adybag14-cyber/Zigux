const std = @import("std");

fn readWorkspaceFile(
    io: anytype,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    _ = limit;
    // These survey inputs are repo-owned review surfaces, so avoid brittle
    // per-file caps that drift as docs and boundary references grow.
    return std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        allocator,
        .limited(std.math.maxInt(usize)),
    );
}

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
    }
}

test "runtime loader non-owner boundary survey keeps config-surface and export parity surfaces explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
        128 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const manifest = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/runtime_loader_gap_manifest.json",
        64 * 1024,
    );
    defer std.testing.allocator.free(manifest);

    const phase9_build = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase9_build.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    const scripts_readme = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "scripts/zigux/README.md",
        256 * 1024,
    );
    defer std.testing.allocator.free(scripts_readme);

    const conf_bridge = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "scripts/zigux/kconfig/conf_bridge.zig",
        256 * 1024,
    );
    defer std.testing.allocator.free(conf_bridge);

    const confdata_bridge = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "scripts/zigux/kconfig/confdata_bridge.zig",
        256 * 1024,
    );
    defer std.testing.allocator.free(confdata_bridge);

    const rust_exports = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "rust/exports.c",
        16 * 1024,
    );
    defer std.testing.allocator.free(rust_exports);

    const export_shim = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/kernel/export_shim.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(export_shim);

    try expectContainsAll(survey_note, &.{
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "rust/exports.c",
        "zigux/kernel/export_shim.zig",
        "Phase 2 config-surface bridge packet",
        "Phase 3 export-boundary packet",
        "boundary references instead of Phase 9 runtime evidence",
    });
    try expectContainsAll(manifest, &.{
        "\"surface\": \"scripts/zigux/kconfig/conf_bridge.zig\"",
        "\"surface\": \"scripts/zigux/kconfig/confdata_bridge.zig\"",
        "\"surface\": \"rust/exports.c\"",
        "\"surface\": \"zigux/kernel/export_shim.zig\"",
        "\"boundary_kind\": \"config_surface_bridge\"",
        "\"boundary_kind\": \"export_boundary\"",
        "\"owning_phase\": \"Phase 2\"",
        "\"owning_phase\": \"Phase 3\"",
    });
    try expectContainsAll(phase9_build, &.{
        "runtime_loader_allocator_init_flow.zig",
        "runtime_loader_non_owner_boundary_survey.zig",
        "phase9-runtime-loader-allocator-init-flow-tests",
        "phase9-runtime-loader-non-owner-boundary-survey-tests",
        "allocator-init-flow",
        "non-owner-boundary",
    });
    try expectContainsAll(scripts_readme, &.{
        "check-phase9-loader-substrate-plan.py --self-test",
        "check-phase9-loader-substrate-plan.py",
        "make -C zigux phase9-loader-gap-survey",
        "make -C zigux phase9-loader-commit-alignment-survey",
        "make -C zigux phase9-non-owner-boundary-survey",
    });
    try expectContainsAll(conf_bridge, &.{
        "pub const Mode = enum",
        ".syncconfig => \"--syncconfig\"",
        ".olddefconfig => \"--olddefconfig\"",
        ".helpnewconfig => \"--helpnewconfig\"",
        "\"KCONFIG_CONFIG\"",
        "\"KCONFIG_AUTOCONFIG\"",
        "\"KCONFIG_AUTOHEADER\"",
        "\"KCONFIG_NOSILENTUPDATE\"",
        "\"KCONFIG_SEED\"",
        "\"KCONFIG_PROBABILITY\"",
    });
    try expectContainsAll(confdata_bridge, &.{
        "const EntryKind = enum",
        ".tristate => \"tristate\"",
        ".string => \"string\"",
        ".int => \"int\"",
        ".hex => \"hex\"",
        ".value => \"value\"",
        ".unset => \"unset\"",
        "pub fn parseConfig",
        "\"counts\"",
        "\"entries\"",
    });
    try expectContainsAll(rust_exports, &.{
        "#define EXPORT_SYMBOL_RUST_GPL(sym) extern int sym; EXPORT_SYMBOL_GPL(sym)",
        "#include \"exports_core_generated.h\"",
        "#include \"exports_bindings_generated.h\"",
        "#include \"exports_kernel_generated.h\"",
        "#ifndef CONFIG_RUST_INLINE_HELPERS",
        "#ifdef CONFIG_RUST_BUILD_ASSERT_ALLOW",
        "EXPORT_SYMBOL_RUST_GPL(rust_build_error);",
    });
    try expectContainsAll(export_shim, &.{
        "pub fn normalize(status: abi.ExportStatus) abi.ExportStatus",
        "pub fn ok(facility: abi.Facility) abi.ExportStatus",
        "pub fn errno(code: i32, facility: abi.Facility) abi.ExportStatus",
        "pub fn isOk(status: abi.ExportStatus) bool",
        "pub fn isCompatibleHeader(boundary_header: abi.BoundaryHeader) bool",
        "pub fn isCanonicalHeader(boundary_header: abi.BoundaryHeader) bool",
        "abi.STATUS_FLAG_ERROR",
    });
}

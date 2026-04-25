const std = @import("std");
const libfs = @import("libfs");

test "phase13 libfs exposes the statfs starter anchored to libfs.c" {
    const descriptor = libfs.LibFsHelperLab.descriptor();
    try std.testing.expectEqualStrings("libfs_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("fs/libfs.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_statfs_defaults);
    try std.testing.expect(descriptor.provides_lookup_policy);
    try std.testing.expect(!descriptor.touches_live_dcache);
    try std.testing.expect(!descriptor.touches_live_inode_state);

    const summary = libfs.LibFsHelperLab.simpleStatFs(0x12345678ABCDEF01, @as(u64, 0xBEEF));
    try std.testing.expectEqualStrings("fs/libfs.c", summary.anchor);
    try std.testing.expectEqual(@as(u32, 0xABCDEF01), summary.fsid.val[0]);
    try std.testing.expectEqual(@as(u32, 0x12345678), summary.fsid.val[1]);
    try std.testing.expectEqual(@as(u64, 0xBEEF), summary.fs_type);
    try std.testing.expectEqual(@as(u32, libfs.page_size), summary.block_size);
    try std.testing.expectEqual(@as(u32, libfs.name_max), summary.name_len_max);
}

test "phase13 libfs lookup policy marks negative dentries for immediate discard" {
    try std.testing.expect(libfs.LibFsHelperLab.alwaysDeleteDentry());

    const decision = try libfs.LibFsHelperLab.simpleLookup(.{
        .name_len = 12,
        .has_dentry_operations = false,
        .dont_cache_negative = false,
        .directory_is_casefolded = false,
    });
    try std.testing.expectEqualStrings("fs/libfs.c", decision.anchor);
    try std.testing.expect(decision.should_mark_dont_cache);
    try std.testing.expect(decision.should_add_negative_dentry);
    try std.testing.expect(decision.returns_null);
    try std.testing.expect(!decision.casefold_passthrough);
}

test "phase13 libfs lookup keeps casefold passthrough and rejects long names" {
    const casefolded = try libfs.LibFsHelperLab.simpleLookup(.{
        .name_len = libfs.name_max,
        .has_dentry_operations = true,
        .dont_cache_negative = true,
        .directory_is_casefolded = true,
    });
    try std.testing.expect(!casefolded.should_mark_dont_cache);
    try std.testing.expect(!casefolded.should_add_negative_dentry);
    try std.testing.expect(casefolded.returns_null);
    try std.testing.expect(casefolded.casefold_passthrough);

    try std.testing.expectError(error.NameTooLong, libfs.LibFsHelperLab.simpleLookup(.{
        .name_len = libfs.name_max + 1,
        .has_dentry_operations = false,
        .dont_cache_negative = false,
        .directory_is_casefolded = false,
    }));
}

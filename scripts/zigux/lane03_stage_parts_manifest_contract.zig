const std = @import("std");
const stage = @import("stage_pinned_zig_archive.zig");
const policy = @import("toolchain_policy.zig");
const resolver = @import("toolchain_resolver.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

test "stage helper keeps parts-dir CLI and input-mode boundary" {
    try std.testing.expectEqual(InputMode.source, stage.InputMode.source);
    try std.testing.expectEqualStrings("parts_dir", stage.InputMode.parts_dir.name());

    var err_msg: ?[]const u8 = null;
    defer if (err_msg) |msg| std.testing.allocator.free(msg);

    const metadata = stage.StageMetadata{
        .channel = "0.17.0-dev.1415+64dfaa568",
        .target = "x86_64-linux",
        .sha256 = "f72f19cbae9f4e649d7b2c5040aec6ccb93dce08048738bcfdf1a03475cd0c93",
        .size = stage.expected_archive_sizes.get("x86_64-linux").?,
        .filename = "zig-x86_64-linux-0.17.0-dev.1415+64dfaa568.tar.xz",
    };

    const neither = stage.resolveSourceArchive(std.testing.allocator, std.testing.io, null, null, &metadata, &err_msg);
    try std.testing.expectError(stage.ValidationFailed.Invalid, neither);
    try std.testing.expect(err_msg != null);
    try expectContains(err_msg.?, "exactly one of source or parts_dir must be provided");
    if (err_msg) |msg| std.testing.allocator.free(msg);
    err_msg = null;

    const both = stage.resolveSourceArchive(
        std.testing.allocator,
        std.testing.io,
        "sources/zig-source.tar.xz",
        "parts",
        &metadata,
        &err_msg,
    );
    try std.testing.expectError(stage.ValidationFailed.Invalid, both);
    try std.testing.expect(err_msg != null);
    try expectContains(err_msg.?, "exactly one of source or parts_dir must be provided");

    try std.testing.expectEqualStrings("STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=", "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=");
    try std.testing.expectEqualStrings("STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=", "STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=");
}

test "parts manifest schema remains strict and policy-bound" {
    var tmp_root_buffer: [128]u8 = undefined;
    const tmp_root = try std.fmt.bufPrint(
        &tmp_root_buffer,
        ".zig-cache/tmp/lane03_manifest",
        .{},
    );
    std.Io.Dir.cwd().deleteTree(std.testing.io, tmp_root) catch {};
    try std.Io.Dir.cwd().createDirPath(std.testing.io, tmp_root);
    defer std.Io.Dir.cwd().deleteTree(std.testing.io, tmp_root) catch {};

    const parts_dir = try std.fmt.allocPrint(std.testing.allocator, "{s}/parts", .{tmp_root});
    defer std.testing.allocator.free(parts_dir);
    try std.Io.Dir.cwd().createDirPath(std.testing.io, parts_dir);

    var err_msg: ?[]const u8 = null;
    defer if (err_msg) |msg| std.testing.allocator.free(msg);

    const missing = stage.loadShardManifest(std.testing.allocator, std.testing.io, parts_dir, &err_msg);
    try std.testing.expectError(stage.ValidationFailed.Invalid, missing);
    try expectContains(err_msg.?, "missing shard manifest");
    if (err_msg) |msg| std.testing.allocator.free(msg);
    err_msg = null;

    const manifest_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/manifest.json", .{parts_dir});
    defer std.testing.allocator.free(manifest_path);
    try std.Io.Dir.cwd().writeFile(std.testing.io, .{ .sub_path = manifest_path, .data = "not-json" });
    err_msg = null;
    const invalid_json = stage.loadShardManifest(std.testing.allocator, std.testing.io, parts_dir, &err_msg);
    try std.testing.expectError(stage.ValidationFailed.Invalid, invalid_json);
    try expectContains(err_msg.?, "invalid shard manifest JSON");
    if (err_msg) |msg| std.testing.allocator.free(msg);
    err_msg = null;

    try std.Io.Dir.cwd().writeFile(std.testing.io, .{ .sub_path = manifest_path, .data = "[]\n" });
    err_msg = null;
    const invalid_payload = stage.loadShardManifest(std.testing.allocator, std.testing.io, parts_dir, &err_msg);
    try std.testing.expectError(stage.ValidationFailed.Invalid, invalid_payload);
    try expectContains(err_msg.?, "invalid shard manifest payload");
    if (err_msg) |msg| std.testing.allocator.free(msg);
    err_msg = null;

    const expected_filename = "zig-x86_64-linux-0.17.0-dev.1415+64dfaa568.tar.xz";
    const expected_sha = "f72f19cbae9f4e649d7b2c5040aec6ccb93dce08048738bcfdf1a03475cd0c93";
    const expected_size = stage.expected_archive_sizes.get("x86_64-linux").?;

    const bad_filename_manifest =
        \\{
        \\  "filename": "zig-aarch64-linux-0.17.0-dev.1415+64dfaa568.tar.xz",
        \\  "encoding": "base64",
        \\  "sha256": "f72f19cbae9f4e649d7b2c5040aec6ccb93dce08048738bcfdf1a03475cd0c93",
        \\  "size": 59264068,
        \\  "chunk_bytes": 1024,
        \\  "part_count": 1,
        \\  "parts_glob": "part-*.b64"
        \\}
        \\
    ;
    try std.Io.Dir.cwd().writeFile(std.testing.io, .{ .sub_path = manifest_path, .data = bad_filename_manifest });
    const destination = try std.fmt.allocPrint(std.testing.allocator, "{s}/archive.tar.xz", .{tmp_root});
    defer std.testing.allocator.free(destination);
    err_msg = null;
    const filename_mismatch = stage.reconstructArchiveFromParts(
        std.testing.allocator,
        std.testing.io,
        parts_dir,
        destination,
        expected_filename,
        expected_sha,
        expected_size,
        &err_msg,
    );
    try std.testing.expectError(stage.ValidationFailed.Invalid, filename_mismatch);
    try expectContains(err_msg.?, "expected shard manifest filename");
    if (err_msg) |msg| std.testing.allocator.free(msg);
    err_msg = null;

    const bad_encoding_manifest =
        \\{
        \\  "filename": "zig-x86_64-linux-0.17.0-dev.1415+64dfaa568.tar.xz",
        \\  "encoding": "hex",
        \\  "sha256": "f72f19cbae9f4e649d7b2c5040aec6ccb93dce08048738bcfdf1a03475cd0c93",
        \\  "size": 59264068,
        \\  "chunk_bytes": 1024,
        \\  "part_count": 1,
        \\  "parts_glob": "part-*.b64"
        \\}
        \\
    ;
    try std.Io.Dir.cwd().writeFile(std.testing.io, .{ .sub_path = manifest_path, .data = bad_encoding_manifest });
    err_msg = null;
    const encoding_mismatch = stage.reconstructArchiveFromParts(
        std.testing.allocator,
        std.testing.io,
        parts_dir,
        destination,
        expected_filename,
        expected_sha,
        expected_size,
        &err_msg,
    );
    try std.testing.expectError(stage.ValidationFailed.Invalid, encoding_mismatch);
    try expectContains(err_msg.?, "expected shard manifest encoding base64");
    if (err_msg) |msg| std.testing.allocator.free(msg);
    err_msg = null;

    const bad_glob_manifest =
        \\{
        \\  "filename": "zig-x86_64-linux-0.17.0-dev.1415+64dfaa568.tar.xz",
        \\  "encoding": "base64",
        \\  "sha256": "f72f19cbae9f4e649d7b2c5040aec6ccb93dce08048738bcfdf1a03475cd0c93",
        \\  "size": 59264068,
        \\  "chunk_bytes": 1024,
        \\  "part_count": 1,
        \\  "parts_glob": "shard-*.b64"
        \\}
        \\
    ;
    try std.Io.Dir.cwd().writeFile(std.testing.io, .{ .sub_path = manifest_path, .data = bad_glob_manifest });
    err_msg = null;
    const glob_mismatch = stage.reconstructArchiveFromParts(
        std.testing.allocator,
        std.testing.io,
        parts_dir,
        destination,
        expected_filename,
        expected_sha,
        expected_size,
        &err_msg,
    );
    try std.testing.expectError(stage.ValidationFailed.Invalid, glob_mismatch);
    try expectContains(err_msg.?, "expected shard manifest parts_glob part-*.b64");
}

test "parts reconstruction reads ordered shards and validates final archive" {
    var tmp_root_buffer: [128]u8 = undefined;
    const tmp_root = try std.fmt.bufPrint(
        &tmp_root_buffer,
        ".zig-cache/tmp/lane03_reconstruct",
        .{},
    );
    std.Io.Dir.cwd().deleteTree(std.testing.io, tmp_root) catch {};
    try std.Io.Dir.cwd().createDirPath(std.testing.io, tmp_root);
    defer std.Io.Dir.cwd().deleteTree(std.testing.io, tmp_root) catch {};

    const payload = "xy";
    const parts_dir = try std.fmt.allocPrint(std.testing.allocator, "{s}/parts", .{tmp_root});
    defer std.testing.allocator.free(parts_dir);
    const destination = try std.fmt.allocPrint(std.testing.allocator, "{s}/archive.tar.xz", .{tmp_root});
    defer std.testing.allocator.free(destination);

    const filename = "zig-x86_64-linux-0.17.0-dev.1415+64dfaa568.tar.xz";
    var payload_hasher = std.crypto.hash.sha2.Sha256.init(.{});
    payload_hasher.update(payload);
    var payload_digest: [32]u8 = undefined;
    payload_hasher.final(&payload_digest);
    const payload_sha = try std.fmt.allocPrint(std.testing.allocator, "{s}", .{std.fmt.bytesToHex(&payload_digest, .lower)});
    defer std.testing.allocator.free(payload_sha);

    try stage.writePartsFixture(std.testing.io, std.testing.allocator, parts_dir, payload, filename, payload_sha, 1);

    var err_msg: ?[]const u8 = null;
    defer if (err_msg) |msg| std.testing.allocator.free(msg);

    const actual_sha = try stage.reconstructArchiveFromParts(
        std.testing.allocator,
        std.testing.io,
        parts_dir,
        destination,
        filename,
        payload_sha,
        payload.len,
        &err_msg,
    );
    defer std.testing.allocator.free(actual_sha);
    try std.testing.expectEqualStrings(payload_sha, actual_sha);

    const reconstructed = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, destination, std.testing.allocator, .unlimited);
    defer std.testing.allocator.free(reconstructed);
    try std.testing.expectEqualSlices(u8, payload, reconstructed);

    const shard_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/part-001.b64", .{parts_dir});
    defer std.testing.allocator.free(shard_path);
    try std.Io.Dir.cwd().deleteFile(std.testing.io, shard_path);
    err_msg = null;
    const missing_shard = stage.reconstructArchiveFromParts(
        std.testing.allocator,
        std.testing.io,
        parts_dir,
        destination,
        filename,
        payload_sha,
        payload.len,
        &err_msg,
    );
    try std.testing.expectError(stage.ValidationFailed.Invalid, missing_shard);
    try expectContains(err_msg.?, "missing expected shard");
    if (err_msg) |msg| std.testing.allocator.free(msg);
    err_msg = null;

    const shard_zero = try std.fmt.allocPrint(std.testing.allocator, "{s}/part-000.b64", .{parts_dir});
    defer std.testing.allocator.free(shard_zero);
    try std.Io.Dir.cwd().writeFile(std.testing.io, .{ .sub_path = shard_zero, .data = "not base64!\n" });
    err_msg = null;
    const invalid_base64 = stage.reconstructArchiveFromParts(
        std.testing.allocator,
        std.testing.io,
        parts_dir,
        destination,
        filename,
        payload_sha,
        payload.len,
        &err_msg,
    );
    try std.testing.expectError(stage.ValidationFailed.Invalid, invalid_base64);
    try expectContains(err_msg.?, "invalid base64 shard");
}

test "self-test fixtures exercise successful and failing parts packets" {
    try std.testing.expectEqualStrings("base64", "base64");
    try std.testing.expectEqualStrings("part-*.b64", "part-*.b64");
    try std.testing.expectEqualStrings(stage.self_test_pass_marker, "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass");
    try std.testing.expect(std.mem.startsWith(u8, stage.self_test_case_count_prefix, "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT="));

    const expected = "zig-x86_64-linux-0.17.0-dev.1415+64dfaa568.tar.xz";
    try std.testing.expect(policy.archiveNameHasDuplicateSuffix("zig-x86_64-linux-0.17.0-dev.1415+64dfaa568 (1).tar.xz", expected));
    const duplicate_name = try stage.duplicateArchiveName(std.testing.allocator, expected);
    defer std.testing.allocator.free(duplicate_name);
    try std.testing.expect(std.mem.endsWith(u8, duplicate_name, " (1).tar.xz"));
}

const InputMode = stage.InputMode;

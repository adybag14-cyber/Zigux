const std = @import("std");

const ContractError = error{
    InvalidManifest,
    MissingMarker,
    OutOfOrderMarker,
};

const expected_target = "x86_64-linux";
const expected_channel = "0.17.0-dev.758+748e7c5e3";
const expected_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const expected_size: u64 = 59_410_844;
const expected_filename = "zig-" ++ expected_target ++ "-" ++ expected_channel ++ ".tar.xz";
const expected_parts_dir = "third_party/" ++ expected_filename ++ ".parts";

const PartsManifest = struct {
    filename: []const u8,
    encoding: []const u8,
    sha256: []const u8,
    size: u64,
    chunk_bytes: u64,
    part_count: u32,
    parts_glob: []const u8,
};

fn requireContains(text: []const u8, marker: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, text, marker) == null) return error.MissingMarker;
}

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) ContractError!void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingMarker;
    if (earlier_index >= later_index) return error.OutOfOrderMarker;
}

fn requirePartsManifest(manifest: PartsManifest) ContractError!void {
    if (!std.mem.eql(u8, manifest.filename, expected_filename)) return error.InvalidManifest;
    if (!std.mem.eql(u8, manifest.encoding, "base64")) return error.InvalidManifest;
    if (!std.mem.eql(u8, manifest.sha256, expected_sha256)) return error.InvalidManifest;
    if (manifest.size != expected_size) return error.InvalidManifest;
    if (manifest.chunk_bytes == 0) return error.InvalidManifest;
    if (manifest.part_count == 0) return error.InvalidManifest;
    if (!std.mem.eql(u8, manifest.parts_glob, "part-*.b64")) return error.InvalidManifest;
}

fn partName(buffer: []u8, index: u32) []const u8 {
    return std.fmt.bufPrint(buffer, "part-{d:0>3}.b64", .{index}) catch unreachable;
}

fn requireSequentialParts(part_names: []const []const u8, part_count: u32) ContractError!void {
    if (part_names.len != part_count) return error.InvalidManifest;

    var name_buffer: [12]u8 = undefined;
    for (part_names, 0..) |actual, index| {
        const expected = partName(&name_buffer, @intCast(index));
        if (!std.mem.eql(u8, actual, expected)) return error.InvalidManifest;
    }
}

fn checkStageHelperPartsContract(helper_text: []const u8) ContractError!void {
    const ordered_markers = [_][]const u8{
        "load_shard_manifest(parts_dir)",
        "require_manifest_string(manifest, \"filename\", manifest_path)",
        "require_manifest_string(manifest, \"encoding\", manifest_path)",
        "require_manifest_string(manifest, \"sha256\", manifest_path)",
        "require_manifest_int(manifest, \"size\", manifest_path)",
        "require_manifest_int(manifest, \"part_count\", manifest_path)",
        "require_manifest_int(manifest, \"chunk_bytes\", manifest_path)",
        "require_manifest_string(manifest, \"parts_glob\", manifest_path)",
        "for index in range(part_count):",
        "shard_path = parts_dir / f\"part-{index:03d}.b64\"",
        "base64.b64decode(encoded, validate=True)",
        "return validate_source_archive(",
    };

    for (ordered_markers) |marker| {
        try requireContains(helper_text, marker);
    }
    for (ordered_markers[0 .. ordered_markers.len - 1], ordered_markers[1..]) |earlier, later| {
        try requireOrder(helper_text, earlier, later);
    }

    try requireContains(helper_text, "expected shard manifest filename");
    try requireContains(helper_text, "expected shard manifest encoding base64");
    try requireContains(helper_text, "expected shard manifest parts_glob part-*.b64");
    try requireContains(helper_text, "missing expected shard:");
    try requireContains(helper_text, "invalid base64 shard:");
    try requireContains(helper_text, "input_mode == \"parts_dir\"");
}

fn checkWorkflowStagesPartsBeforeFallback(workflow_text: []const u8) ContractError!void {
    try requireContains(workflow_text, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try requireContains(workflow_text, "if [ ! -d \"$repo_archive_parts_dir\" ]; then");
    try requireContains(workflow_text, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try requireContains(workflow_text, "--parts-dir \"$repo_archive_parts_dir\"");
    try requireContains(workflow_text, "if try_local_archive; then");
    try requireContains(workflow_text, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");

    try requireOrder(workflow_text, "--parts-dir \"$repo_archive_parts_dir\"", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireOrder(workflow_text, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "community-mirrors.txt");
    try requireOrder(workflow_text, "community-mirrors.txt", "try_download \"$ZIGUX_ZIG_URL\"");
}

fn checkReadmeNamesCurrentPartsPath(readme_text: []const u8) ContractError!void {
    try requireContains(readme_text, "`" ++ expected_target ++ "`");
    try requireContains(readme_text, "`" ++ expected_channel ++ "`");
    try requireContains(readme_text, "`third_party/" ++ expected_filename ++ "`");
    try requireContains(readme_text, "`" ++ expected_parts_dir ++ "`");
    try requireContains(readme_text, "`" ++ expected_sha256 ++ "`");
    try requireContains(readme_text, "`59410844` bytes");
}

const current_manifest = PartsManifest{
    .filename = expected_filename,
    .encoding = "base64",
    .sha256 = expected_sha256,
    .size = expected_size,
    .chunk_bytes = 786_432,
    .part_count = 3,
    .parts_glob = "part-*.b64",
};

const current_stage_helper_excerpt =
    \\\ndef reconstruct_archive_from_parts(parts_dir, destination, *, expected_filename, expected_sha, expected_size):
    \\\n    manifest_path = parts_dir / "manifest.json"
    \\\n    manifest = load_shard_manifest(parts_dir)
    \\\n    filename = require_manifest_string(manifest, "filename", manifest_path)
    \\\n    encoding = require_manifest_string(manifest, "encoding", manifest_path)
    \\\n    sha256 = require_manifest_string(manifest, "sha256", manifest_path)
    \\\n    size = require_manifest_int(manifest, "size", manifest_path)
    \\\n    part_count = require_manifest_int(manifest, "part_count", manifest_path)
    \\\n    require_manifest_int(manifest, "chunk_bytes", manifest_path)
    \\\n    parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)
    \\\n    if filename != expected_filename:
    \\\n        raise ValueError("expected shard manifest filename")
    \\\n    if encoding != "base64":
    \\\n        raise ValueError("expected shard manifest encoding base64")
    \\\n    if parts_glob != "part-*.b64":
    \\\n        raise ValueError("expected shard manifest parts_glob part-*.b64")
    \\\n    for index in range(part_count):
    \\\n        shard_path = parts_dir / f"part-{index:03d}.b64"
    \\\n        if not shard_path.exists():
    \\\n            raise ValueError(f"missing expected shard: {shard_path.name}")
    \\\n        chunk = base64.b64decode(encoded, validate=True)
    \\\n        raise ValueError(f"invalid base64 shard: {shard_path.name}")
    \\\n    return validate_source_archive(
    \\\n        destination,
    \\\n    )
    \\\nassert input_mode == "parts_dir"
;

const current_workflow_excerpt =
    \\\nrepo_archive_parts_dir="${repo_archive_path}.parts"
    \\\nif [ ! -d "$repo_archive_parts_dir" ]; then
    \\\n  return 1
    \\\nfi
    \\\npython3 scripts/zigux/stage-pinned-zig-archive.py \
    \\\n  --root "$GITHUB_WORKSPACE" \
    \\\n  --parts-dir "$repo_archive_parts_dir" || return 1
    \\\nif try_local_archive; then
    \\\n  download_success=1
    \\\nelif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
    \\\n  download_success=1
    \\\nelif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\\n  true
    \\\nfi
    \\\ntry_download "$ZIGUX_ZIG_URL"
;

const current_readme_excerpt =
    \\\n- target: `x86_64-linux`
    \\\n- channel: `0.17.0-dev.758+748e7c5e3`
    \\\n- file: `third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz`
    \\\n- sha256: `0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6`
    \\\n- size: `59410844` bytes
    \\\nIf the exact archive file is absent but `third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts` is present, bootstrap stages the same pinned payload locally.
;

test "lane05 archive parts manifest matches live pinned policy" {
    try requirePartsManifest(current_manifest);
}

test "lane05 archive parts require sequential base64 shards" {
    const part_names = [_][]const u8{ "part-000.b64", "part-001.b64", "part-002.b64" };
    try requireSequentialParts(&part_names, current_manifest.part_count);
}

test "lane05 archive parts reject missing or out-of-order shards" {
    const missing = [_][]const u8{ "part-000.b64", "part-002.b64" };
    try std.testing.expectError(error.InvalidManifest, requireSequentialParts(&missing, current_manifest.part_count));

    const out_of_order = [_][]const u8{ "part-001.b64", "part-000.b64", "part-002.b64" };
    try std.testing.expectError(error.InvalidManifest, requireSequentialParts(&out_of_order, current_manifest.part_count));
}

test "lane05 stage helper keeps manifest validation before reconstruction" {
    try checkStageHelperPartsContract(current_stage_helper_excerpt);
}

test "lane05 workflow stages parts before network fallback" {
    try checkWorkflowStagesPartsBeforeFallback(current_workflow_excerpt);
}

test "lane05 README names the current parts path and digest" {
    try checkReadmeNamesCurrentPartsPath(current_readme_excerpt);
}

test "lane05 archive parts reject stale channel and digest markers" {
    const stale_manifest = PartsManifest{
        .filename = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
        .encoding = "base64",
        .sha256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
        .size = 58_159_088,
        .chunk_bytes = 786_432,
        .part_count = 3,
        .parts_glob = "part-*.b64",
    };

    try std.testing.expectError(error.InvalidManifest, requirePartsManifest(stale_manifest));
}

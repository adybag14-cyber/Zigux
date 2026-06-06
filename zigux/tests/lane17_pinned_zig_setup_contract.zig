const std = @import("std");
const config = @import("config");

const ContractError = error{
    MissingMarker,
    ReorderedMarker,
};

fn readWorkflow() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        config.workflow_path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn requireOrdered(source: []const u8, markers: []const []const u8) ContractError!void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOf(u8, source[cursor..], marker) orelse {
            std.debug.print("missing ordered marker after byte {d}: {s}\n", .{ cursor, marker });
            return error.MissingMarker;
        };
        cursor += found + marker.len;
    }
}

fn setupBlock(workflow: []const u8) ContractError![]const u8 {
    const start_marker = "      - name: Setup pinned Zig toolchain\n";
    const end_marker = "\n      - name: Compile current scripts\n";
    const compact_end_marker = "      - name: Compile current scripts";
    const start = std.mem.indexOf(u8, workflow, start_marker) orelse return error.MissingMarker;
    const after_start = start + start_marker.len;
    const end_relative = std.mem.indexOf(u8, workflow[after_start..], end_marker) orelse
        std.mem.indexOf(u8, workflow[after_start..], compact_end_marker) orelse
        return error.MissingMarker;
    return workflow[after_start .. after_start + end_relative];
}

fn requireNoLegacySetupAction(block: []const u8) ContractError!void {
    const stale_actions = [_][]const u8{
        "uses: goto-bus-stop/setup-zig",
        "uses: mlugg/setup-zig",
        "uses: actions/setup-zig",
    };
    for (stale_actions) |marker| {
        if (std.mem.indexOf(u8, block, marker) != null) {
            std.debug.print("stale setup action should stay out of pinned setup block: {s}\n", .{marker});
            return error.ReorderedMarker;
        }
    }
}

test "pinned Zig setup derives archive identity and canonical release from policy" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);
    const block = try setupBlock(workflow);

    try requireNoLegacySetupAction(block);
    try requireOrdered(block, &.{
        "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
        "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]",
        "if len(targets) != 1:",
        "target = targets[0]",
        "channel = policy[\"channel\"]",
        "filename = f\"zig-{target}-{channel}.tar.xz\"",
        "canonical_repo = \"adybag14-cyber/zig\"",
        "canonical_tag = \"upstream-748e7c5e39fc\"",
        "url = f\"https://ziglang.org/builds/{filename}\"",
        "canonical_url = f\"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}\"",
        "print(f\"ZIGUX_ZIG_TARGET='{target}'\")",
        "print(f\"ZIGUX_ZIG_CHANNEL='{channel}'\")",
        "print(f\"ZIGUX_ZIG_FILENAME='{filename}'\")",
        "print(f\"ZIGUX_ZIG_URL='{url}'\")",
        "print(f\"ZIGUX_ZIG_CANONICAL_URL='{canonical_url}'\")",
    });
}

test "local archive and parts staging are verified before network fallback" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);
    const block = try setupBlock(workflow);

    try requireOrdered(block, &.{
        "archive_path=\".zig-toolchain/$ZIGUX_ZIG_FILENAME\"",
        "extract_root=\"$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL\"",
        "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
        "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
        "try_local_archive() {",
        "if [ ! -f \"$repo_archive_path\" ]; then",
        "if [ ! -d \"$repo_archive_parts_dir\" ]; then",
        "python3 scripts/zigux/stage-pinned-zig-archive.py",
        "--parts-dir \"$repo_archive_parts_dir\" || return 1",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
        "tar -xJf \"$repo_archive_path\" -C .zig-toolchain",
        "zig_path=\"$extract_root/zig\"",
        "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"",
        "rm -rf \"$extract_root\"",
        "return 1",
    });
}

test "download fallback remains canonical then mirrors then direct with final path handoff" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);
    const block = try setupBlock(workflow);

    try requireOrdered(block, &.{
        "try_download() {",
        "if curl -L --fail \"$url\" -o \"$archive_path\"; then",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
        "tar -xJf \"$archive_path\" -C .zig-toolchain",
        "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"",
        "download_success=0",
        "if try_local_archive; then",
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
        "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"",
        "if [ \"$download_success\" -ne 1 ]; then",
        "if try_download \"$ZIGUX_ZIG_URL\"; then",
        "if [ \"$download_success\" -ne 1 ]; then",
        "echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2",
        "exit 1",
        "zig_path=\"$extract_root/zig\"",
        "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
        "\"$zig_path\" version",
    });
}

test "contract fails closed on stale setup action or missing canonical fallback" {
    const stale_action =
        \\      - name: Setup pinned Zig toolchain
        \\        uses: goto-bus-stop/setup-zig@v2
        \\
        \\      - name: Compile current scripts
    ;
    try std.testing.expectError(error.ReorderedMarker, requireNoLegacySetupAction(try setupBlock(stale_action)));

    const missing_canonical =
        \\      - name: Setup pinned Zig toolchain
        \\        run: |
        \\          set -euxo pipefail
        \\          download_success=0
        \\          if try_local_archive; then
        \\            download_success=1
        \\          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\            download_success=1
        \\          fi
        \\
        \\      - name: Compile current scripts
    ;
    const block = try setupBlock(missing_canonical);
    try std.testing.expectError(error.MissingMarker, requireOrdered(block, &.{
        "if try_local_archive; then",
        "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    }));
}

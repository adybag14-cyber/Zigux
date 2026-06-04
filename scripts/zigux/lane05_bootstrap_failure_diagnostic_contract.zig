const std = @import("std");

const ContractError = error{
    MissingMarker,
    OutOfOrderMarker,
};

const expected_channel = "0.17.0-dev.758+748e7c5e3";
const expected_sha256 = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const expected_size = "59410844";
const expected_filename = "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz";
const expected_parts_dir = "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts";

const failure_diagnostic =
    "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org";

fn requireContains(text: []const u8, marker: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, text, marker) == null) return error.MissingMarker;
}

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) ContractError!void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingMarker;
    if (earlier_index >= later_index) return error.OutOfOrderMarker;
}

fn checkPolicy(policy: []const u8) ContractError!void {
    try requireContains(policy, "\"channel\": \"" ++ expected_channel ++ "\"");
    try requireContains(policy, "\"minimum_version\": \"" ++ expected_channel ++ "\"");
    try requireContains(policy, "\"x86_64-linux\": \"" ++ expected_sha256 ++ "\"");
    try requireContains(policy, "\"archive_target_scope\"");
    try requireContains(policy, "\"x86_64-linux\"");
    try requireContains(policy, "\"channel_minimum_lockstep\": true");
}

fn checkReadme(readme: []const u8) ContractError!void {
    try requireContains(readme, "`" ++ expected_channel ++ "`");
    try requireContains(readme, "`third_party/" ++ expected_filename ++ "`");
    try requireContains(readme, "`" ++ expected_parts_dir ++ "`");
    try requireContains(readme, "`" ++ expected_sha256 ++ "`");
    try requireContains(readme, "`" ++ expected_size ++ "` bytes");
}

fn checkWorkflow(workflow: []const u8) ContractError!void {
    try requireContains(workflow, "canonical_repo = \"adybag14-cyber/zig\"");
    try requireContains(workflow, "canonical_tag = \"upstream-748e7c5e39fc\"");
    try requireContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requireContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try requireContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try requireContains(workflow, "try_local_archive");
    try requireContains(workflow, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try requireContains(workflow, "community-mirrors.txt");
    try requireContains(workflow, "try_download \"$ZIGUX_ZIG_URL\"");
    try requireContains(workflow, failure_diagnostic);

    try requireOrder(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try requireOrder(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"", "community-mirrors.txt");
    try requireOrder(workflow, "community-mirrors.txt", "if try_download \"$ZIGUX_ZIG_URL\"");
    try requireOrder(workflow, "if try_download \"$ZIGUX_ZIG_URL\"", failure_diagnostic);
    try requireOrder(workflow, failure_diagnostic, "exit 1");
}

fn checkLane05BootstrapFailureDiagnostic(
    workflow: []const u8,
    policy: []const u8,
    readme: []const u8,
) ContractError!void {
    try checkPolicy(policy);
    try checkReadme(readme);
    try checkWorkflow(workflow);
}

const current_policy =
    \\{
    \\  "phase": "Phase 2",
    \\  "channel": "0.17.0-dev.758+748e7c5e3",
    \\  "minimum_version": "0.17.0-dev.758+748e7c5e3",
    \\  "archive_sha256": {
    \\    "x86_64-linux": "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6"
    \\  },
    \\  "upgrade_policy": {
    \\    "channel_minimum_lockstep": true,
    \\    "archive_target_scope": [
    \\      "x86_64-linux"
    \\    ],
    \\    "required_make_routes": [
    \\      "phase2-toolchain"
    \\    ]
    \\  }
    \\}
;

const current_readme =
    \\# Zigux third-party archives
    \\
    \\- channel: `0.17.0-dev.758+748e7c5e3`
    \\- file: `third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz`
    \\- parts: `third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts`
    \\- sha256: `0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6`
    \\- size: `59410844` bytes
;

const current_workflow =
    \\canonical_repo = "adybag14-cyber/zig"
    \\canonical_tag = "upstream-748e7c5e39fc"
    \\repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
    \\repo_archive_parts_dir="${repo_archive_path}.parts"
    \\python3 scripts/zigux/stage-pinned-zig-archive.py --root "$GITHUB_WORKSPACE" --parts-dir "$repo_archive_parts_dir" || return 1
    \\if try_local_archive; then
    \\  download_success=1
    \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
    \\  download_success=1
    \\elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\  while IFS= read -r mirror_url; do
    \\    if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
    \\      download_success=1
    \\    fi
    \\  done < "$mirror_file"
    \\fi
    \\if [ "$download_success" -ne 1 ]; then
    \\  if try_download "$ZIGUX_ZIG_URL"; then
    \\    download_success=1
    \\  fi
    \\fi
    \\if [ "$download_success" -ne 1 ]; then
    \\  echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2
    \\  exit 1
    \\fi
;

test "lane05 bootstrap failure diagnostic names every fallback source" {
    try checkLane05BootstrapFailureDiagnostic(current_workflow, current_policy, current_readme);
}

test "lane05 bootstrap failure diagnostic rejects a missing mirror source" {
    const stale_workflow =
        \\canonical_repo = "adybag14-cyber/zig"
        \\canonical_tag = "upstream-748e7c5e39fc"
        \\repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
        \\repo_archive_parts_dir="${repo_archive_path}.parts"
        \\python3 scripts/zigux/stage-pinned-zig-archive.py
        \\if try_local_archive; then
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\fi
        \\if try_download "$ZIGUX_ZIG_URL"; then
        \\fi
        \\echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, or ziglang.org' >&2
        \\exit 1
    ;

    try std.testing.expectError(
        error.MissingMarker,
        checkLane05BootstrapFailureDiagnostic(stale_workflow, current_policy, current_readme),
    );
}

test "lane05 bootstrap failure diagnostic stays after direct ziglang fallback" {
    const stale_workflow =
        \\canonical_repo = "adybag14-cyber/zig"
        \\canonical_tag = "upstream-748e7c5e39fc"
        \\repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
        \\repo_archive_parts_dir="${repo_archive_path}.parts"
        \\python3 scripts/zigux/stage-pinned-zig-archive.py
        \\if try_local_archive; then
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\fi
        \\echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2
        \\if try_download "$ZIGUX_ZIG_URL"; then
        \\fi
        \\exit 1
    ;

    try std.testing.expectError(
        error.OutOfOrderMarker,
        checkLane05BootstrapFailureDiagnostic(stale_workflow, current_policy, current_readme),
    );
}

test "lane05 bootstrap failure diagnostic rejects stale attached archive identity" {
    const stale_policy =
        \\{
        \\  "channel": "0.17.0-dev.87+9b177a7d2",
        \\  "minimum_version": "0.17.0-dev.87+9b177a7d2",
        \\  "archive_sha256": {
        \\    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
        \\  },
        \\  "upgrade_policy": {
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["x86_64-linux"]
        \\  }
        \\}
    ;

    try std.testing.expectError(
        error.MissingMarker,
        checkLane05BootstrapFailureDiagnostic(current_workflow, stale_policy, current_readme),
    );
}

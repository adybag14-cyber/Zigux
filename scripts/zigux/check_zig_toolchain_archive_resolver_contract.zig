const std = @import("std");

const checker_path = "scripts/zigux/check-zig-toolchain.py";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

const ContractError = error{
    MissingCheckerMarker,
    MissingPolicyMarker,
};

fn requireContains(haystack: []const u8, needle: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        return error.MissingCheckerMarker;
    }
}

fn requirePolicyContains(haystack: []const u8, needle: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        return error.MissingPolicyMarker;
    }
}

fn checkCheckerSource(source: []const u8) ContractError!void {
    try requireContains(source, "def policy_archive_filename(target: str, channel: str) -> str:");
    try requireContains(source, "return f\"zig-{target}-{channel}.tar.xz\"");
    try requireContains(source, "def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:");
    try requireContains(source, "add_search_root(root / \"third_party\")");
    try requireContains(source, "add_search_root(root / \"agent_files\")");
    try requireContains(source, "add_search_root(parent / \"agent_files\")");
    try requireContains(source, "ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile");
    try requireContains(source, "archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool");
    try requireContains(source, "return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)");
    try requireContains(source, "def select_matching_policy_archive(");
    try requireContains(source, "multiple repo-local pinned archive candidates matched");
    try requireContains(source, "def resolve_policy_archive(");
    try requireContains(source, "archive target must be explicit when policy covers multiple archive targets");
    try requireContains(source, "def expected_archive_metadata(");
    try requireContains(source, "archive target {archive_target!r} is not pinned");
    try requireContains(source, "def validate_policy_archive(path: Path, archive_target: str, *, policy_path: Path = TOOLCHAIN_POLICY)");
    try requireContains(source, "expected archive filename {expected_filename} for {archive_target}, got {path.name}");
    try requireContains(source, "expected sha256 {expected_sha} for {archive_target}, got {actual_sha}");
}

fn checkPolicySource(source: []const u8) ContractError!void {
    try requirePolicyContains(source, "\"phase\": \"Phase 2\"");
    try requirePolicyContains(source, "\"channel_minimum_lockstep\": true");
    try requirePolicyContains(source, "\"archive_target_scope\": [");
    try requirePolicyContains(source, "\"x86_64-linux\"");
    try requirePolicyContains(source, "\"required_make_routes\": [");
    try requirePolicyContains(source, "\"phase2-toolchain\"");
}

fn readRepoFile(context: std.process.Init, allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(context.io, relative_path, allocator, .limited(1024 * 1024));
}

pub fn main(context: std.process.Init) !void {
    const allocator = context.gpa;
    const checker = try readRepoFile(context, allocator, checker_path);
    defer allocator.free(checker);
    const policy = try readRepoFile(context, allocator, policy_path);
    defer allocator.free(policy);

    try checkCheckerSource(checker);
    try checkPolicySource(policy);
}

test "checker archive resolver keeps repo-local search and duplicate suffix markers" {
    const source =
        \\ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(r"^(?P<stem>.+) \((?P<copy>\d+)\)(?P<suffix>\.tar\.xz)$")
        \\def policy_archive_filename(target: str, channel: str) -> str:
        \\    return f"zig-{target}-{channel}.tar.xz"
        \\def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:
        \\    add_search_root(root / ".zig-toolchain")
        \\    add_search_root(root / "toolchains")
        \\    add_search_root(root / ".toolchains")
        \\    add_search_root(root / "third_party")
        \\    add_search_root(root / "agent_files")
        \\        add_search_root(parent / "agent_files")
        \\def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:
        \\    return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)
    ;
    try checkCheckerSource(source ++
        \\def select_matching_policy_archive(
        \\    raise ValueError("multiple repo-local pinned archive candidates matched")
        \\def resolve_policy_archive(
        \\    raise ValueError("archive target must be explicit when policy covers multiple archive targets")
        \\def expected_archive_metadata(
        \\    raise ValueError(f"archive target {archive_target!r} is not pinned")
        \\def validate_policy_archive(path: Path, archive_target: str, *, policy_path: Path = TOOLCHAIN_POLICY)
        \\    f"expected archive filename {expected_filename} for {archive_target}, got {path.name}"
        \\    f"expected sha256 {expected_sha} for {archive_target}, got {actual_sha}"
    );
}

test "policy remains a phase2 exact-channel archive contract" {
    const source =
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.758+748e7c5e3",
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
    try checkPolicySource(source);
}

test "missing resolver markers fail closed" {
    try std.testing.expectError(error.MissingCheckerMarker, checkCheckerSource("def resolve_policy_archive(): pass"));
    try std.testing.expectError(error.MissingPolicyMarker, checkPolicySource("{\"phase\":\"Phase 1\"}"));
}

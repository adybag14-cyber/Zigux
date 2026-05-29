const std = @import("std");

const CheckerContract = struct {
    source: []const u8,

    fn require(self: CheckerContract, marker: []const u8) !void {
        try std.testing.expect(std.mem.indexOf(u8, self.source, marker) != null);
    }

    fn requireInOrder(self: CheckerContract, earlier: []const u8, later: []const u8) !void {
        const earlier_index = std.mem.indexOf(u8, self.source, earlier) orelse return error.MissingEarlierMarker;
        const later_index = std.mem.indexOf(u8, self.source, later) orelse return error.MissingLaterMarker;
        try std.testing.expect(earlier_index < later_index);
    }
};

fn loadCheckerContract(allocator: std.mem.Allocator) !CheckerContract {
    const source = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "scripts/zigux/check-zig-toolchain.py",
        allocator,
        .limited(256 * 1024),
    );
    return .{ .source = source };
}

test "repo-local zig search roots keep pinned toolchains ahead of ambient PATH" {
    const contract = try loadCheckerContract(std.testing.allocator);
    defer std.testing.allocator.free(contract.source);

    try contract.require("def iter_zig_search_roots(root: Path = ROOT) -> list[Path]:");
    try contract.require("add_search_root(root / \".zig-toolchain\")");
    try contract.require("add_search_root(root / \"toolchains\")");
    try contract.require("add_search_root(root / \".toolchains\")");
    try contract.require("for parent in root.parents:");
    try contract.require("add_search_root(parent / \".toolchains\")");
    try contract.require("add_search_root(parent / \"toolchains\")");

    try contract.requireInOrder(
        "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):",
        "return which(\"zig\")",
    );
}

test "pinned channel candidate layout checks both root zig and bin zig forms" {
    const contract = try loadCheckerContract(std.testing.allocator);
    defer std.testing.allocator.free(contract.source);

    try contract.require("def iter_repo_local_zig_candidates(");
    try contract.require("pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"");
    try contract.require("add_candidate(base / \"zig\")");
    try contract.require("add_candidate(base / \"bin\" / \"zig\")");
    try contract.require("add_candidate_roots(base / pinned_dirname)");
    try contract.require("add_candidate_roots(child / pinned_dirname)");
    try contract.require("if path not in candidates:");

    try contract.requireInOrder(
        "if pinned_channel is not None:",
        "for base in zig_search_roots:",
    );
    try contract.requireInOrder(
        "add_candidate_roots(base / pinned_dirname)",
        "add_candidate_roots(child / pinned_dirname)",
    );
}

test "explicit zig path short circuits repo-local discovery" {
    const contract = try loadCheckerContract(std.testing.allocator);
    defer std.testing.allocator.free(contract.source);

    try contract.require("def normalize_explicit_zig_path(explicit_zig: str) -> str:");
    try contract.require("if explicit_zig is not None:");
    try contract.require("return normalize_explicit_zig_path(explicit_zig)");
    try contract.require("raise ValueError(f\"explicit zig path does not exist: {normalized}\")");
    try contract.require("raise ValueError(f\"explicit zig path is a directory, expected an executable file: {normalized}\")");

    try contract.requireInOrder(
        "if explicit_zig is not None:",
        "pinned_channel = load_pinned_channel(policy_path)",
    );
}

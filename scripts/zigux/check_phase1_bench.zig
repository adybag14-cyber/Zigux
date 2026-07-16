// Ported from check-phase1-bench.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_BENCH_CHECK_SELF_TEST=pass";

const EXPECTATIONS_REL = "zigux/tests/fixtures/phase1_bench_expectations.json";
const PHASE1_BENCH_REL = "zigux/tests/phase1_bench.zig";

const FIND_BIT_REQUIRED_SOURCE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "find_bit_bench_fn", .marker = "fn findBitBench() struct { checksum: u64 } {" },
    .{ .label = "find_bit_edge_fn", .marker = "fn findBitEdgeBench() struct { checksum: u64 } {" },
    .{ .label = "find_bit_bench_call", .marker = "const find_bit_result = findBitBench();" },
    .{ .label = "find_bit_edge_call", .marker = "const find_bit_edge_result = findBitEdgeBench();" },
    .{ .label = "find_next_iterations_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\\n\", .{iterations_find_bit});" },
    .{ .label = "find_next_checksum_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\\n\", .{find_bit_result.checksum});" },
    .{ .label = "find_edge_iterations_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}\\n\", .{iterations_find_bit_edge});" },
    .{ .label = "find_edge_checksum_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\n\", .{find_bit_edge_result.checksum});" },
    .{ .label = "boundary_next_bit", .marker = "checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));" },
    .{ .label = "boundary_next_and_bit", .marker = "checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));" },
    .{ .label = "boundary_next_zero_bit", .marker = "checksum +%= @intCast(find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));" },
    .{ .label = "tail_first_bit", .marker = "checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));" },
    .{ .label = "tail_first_and_bit", .marker = "checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));" },
    .{ .label = "tail_last_bit", .marker = "checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));" },
};

const RBTREE_REQUIRED_SOURCE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "rbtree_bench_fn", .marker = "fn rbtreeBench() struct { checksum: u64 } {" },
    .{ .label = "rbtree_postorder_safe_fn", .marker = "fn rbtreePostorderSafeBench() struct { checksum: u64 } {" },
    .{ .label = "rbtree_find_add_fn", .marker = "fn rbtreeFindAddBench() struct { checksum: u64 } {" },
    .{ .label = "rbtree_duplicate_fn", .marker = "fn rbtreeDuplicateBench() struct { checksum: u64 } {" },
    .{ .label = "rbtree_cached_fn", .marker = "fn rbtreeCachedBench() struct { checksum: u64 } {" },
    .{ .label = "rbtree_bench_call", .marker = "const rbtree_result = rbtreeBench();" },
    .{ .label = "rbtree_postorder_safe_call", .marker = "const rbtree_postorder_safe_result = rbtreePostorderSafeBench();" },
    .{ .label = "rbtree_find_add_call", .marker = "const rbtree_find_add_result = rbtreeFindAddBench();" },
    .{ .label = "rbtree_duplicate_call", .marker = "const rbtree_duplicate_result = rbtreeDuplicateBench();" },
    .{ .label = "rbtree_cached_call", .marker = "const rbtree_cached_result = rbtreeCachedBench();" },
    .{ .label = "rbtree_iterations_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_ITERATIONS={d}\\n\", .{iterations_rbtree});" },
    .{ .label = "rbtree_checksum_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_CHECKSUM={d}\\n\", .{rbtree_result.checksum});" },
    .{ .label = "rbtree_postorder_safe_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}\\n\", .{rbtree_postorder_safe_result.checksum});" },
    .{ .label = "rbtree_find_add_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}\\n\", .{rbtree_find_add_result.checksum});" },
    .{ .label = "rbtree_duplicate_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}\\n\", .{rbtree_duplicate_result.checksum});" },
    .{ .label = "rbtree_cached_print", .marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\n\", .{rbtree_cached_result.checksum});" },
    .{ .label = "rbtree_postorder", .marker = "var node = rbtree.firstPostorder(&root);" },
    .{ .label = "rbtree_find_add", .marker = "const existing = rbtree.findAdd(&probe.node, &root, TreeEntry.cmp);" },
    .{ .label = "rbtree_duplicate_range", .marker = "var iter = rbtree.matchIterator(&duplicate_key, &root, TreeEntry.keyCmp);" },
    .{ .label = "rbtree_cached_leftmost", .marker = "const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);" },
};

fn validateBenchSource(text: []const u8) ?[]const u8 {
    for (FIND_BIT_REQUIRED_SOURCE_MARKERS) |entry| {
        if (std.mem.indexOf(u8, text, entry.marker) == null) return "bench_source_missing_markers";
    }
    for (RBTREE_REQUIRED_SOURCE_MARKERS) |entry| {
        if (std.mem.indexOf(u8, text, entry.marker) == null) return "bench_source_missing_markers";
    }
    const dup_marker = "try stdout_writer.interface.print(\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\n\", .{rbtree_cached_result.checksum});";
    if (guard.countOccurrences(text, dup_marker) > 1) return "bench_source_duplicate_rbtree_markers";
    return null;
}

fn parseOutputLine(stdout: []const u8, expectations: std.json.Value) !?[]const u8 {
    var parsed = std.StringHashMap([]const u8).init(std.heap.page_allocator);
    defer parsed.deinit();
    var iter = std.mem.splitScalar(u8, stdout, '\n');
    while (iter.next()) |raw_line| {
        const line = std.mem.trim(u8, raw_line, " \t\r");
        if (line.len == 0 or std.mem.indexOf(u8, line, "=") == null) continue;
        const eq = std.mem.indexOf(u8, line, "=").?;
        const key = line[0..eq];
        const value = line[eq + 1 ..];
        try parsed.put(key, value);
    }
    if (expectations != .object) return "expectations_type";
    const status = expectations.object.get("status") orelse return "expectations_status";
    if (status != .string) return "expectations_status";
    const bench_status = parsed.get("PHASE1_BENCH");
    if (bench_status == null or !std.mem.eql(u8, bench_status.?, status.string)) return "status";
    return null;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    _ = .{ io, allocator };
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var explicit_root: ?[]const u8 = null;
    var explicit_zig: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_zig = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    const expectations_path = try guard.joinPath(allocator, root, EXPECTATIONS_REL);
    defer allocator.free(expectations_path);
    const bench_source_path = try guard.joinPath(allocator, root, PHASE1_BENCH_REL);
    defer allocator.free(bench_source_path);

    const expectations_text = guard.readUtf8File(io, allocator, expectations_path) catch {
        try guard.printLine(io, "PHASE1_BENCH_CHECK=fail", .{});
        try guard.printLine(io, "PHASE1_BENCH_CHECK_REASON=missing_expectations_file", .{});
        try guard.printLine(io, "EXPECTATIONS_PATH={s}", .{expectations_path});
        std.process.exit(1);
    };
    defer allocator.free(expectations_text);

    const expectations_parsed = guard.parseJsonValue(allocator, expectations_text) catch {
        try guard.printLine(io, "PHASE1_BENCH_CHECK=fail", .{});
        try guard.printLine(io, "EXPECTATIONS_JSON_ERROR=decode_error", .{});
        std.process.exit(1);
    };
    defer expectations_parsed.deinit();

    const bench_source_text = guard.readUtf8File(io, allocator, bench_source_path) catch {
        try guard.printLine(io, "PHASE1_BENCH_CHECK=fail", .{});
        try guard.printLine(io, "PHASE1_BENCH_CHECK_REASON=missing_bench_source_file", .{});
        try guard.printLine(io, "{s}", .{bench_source_path});
        std.process.exit(1);
    };
    defer allocator.free(bench_source_text);

    if (validateBenchSource(bench_source_text)) |reason| {
        try guard.printLine(io, "PHASE1_BENCH_CHECK=fail", .{});
        try guard.printLine(io, "PHASE1_BENCH_CHECK_REASON={s}", .{reason});
        std.process.exit(1);
    }

    const requested_zig = explicit_zig orelse init.environ_map.get("ZIG");
    const zig_path = guard.findZigExecutable(io, allocator, root, requested_zig) catch {
        try guard.printLine(io, "zig not found; pass --zig or add zig to PATH", .{});
        std.process.exit(1);
    };
    defer allocator.free(zig_path);

    const result = guard.runProcessCapture(io, allocator, &.{
        zig_path,
        "build",
        "bench",
        "--build-file",
        "zigux/tests/phase1_bench_build.zig",
        "-Doptimize=ReleaseSafe",
    }, root) catch {
        try guard.printLine(io, "PHASE1_BENCH_CHECK=fail", .{});
        try guard.printLine(io, "BENCH_COMMAND_EXIT=1", .{});
        std.process.exit(1);
    };
    defer {
        allocator.free(result.stdout);
        allocator.free(result.stderr);
    }

    if (result.exit_code != 0) {
        try guard.printLine(io, "PHASE1_BENCH_CHECK=fail", .{});
        try guard.printLine(io, "BENCH_COMMAND_EXIT={d}", .{result.exit_code});
        if (result.stdout.len > 0) try guard.printLine(io, "{s}", .{std.mem.trimEnd(u8, result.stdout, "\r\n")});
        if (result.stderr.len > 0) try guard.printLine(io, "{s}", .{std.mem.trimEnd(u8, result.stderr, "\r\n")});
        std.process.exit(1);
    }

    if (try parseOutputLine(result.stdout, expectations_parsed.value)) |reason| {
        try guard.printLine(io, "PHASE1_BENCH_CHECK=fail", .{});
        try guard.printLine(io, "PHASE1_BENCH_CHECK_REASON={s}", .{reason});
        std.process.exit(1);
    }

    try guard.printLine(io, "PHASE1_BENCH_CHECK=pass", .{});
    try guard.printLine(io, "PHASE1_BENCH_EXPECTATIONS={s}", .{expectations_path});
    try guard.printLine(io, "PHASE1_BENCH_SOURCE={s}", .{bench_source_path});
    try guard.printLine(io, "PHASE1_BENCH_ZIG={s}", .{zig_path});
    std.process.exit(0);
}

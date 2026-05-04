const std = @import("std");
const bitmap_diff = @import("bitmap_diff");

const sample_iterations: usize = 2048;
const sample_count: usize = 3;

fn median3(a: u64, b: u64, c: u64) u64 {
    return a + b + c - @min(a, @min(b, c)) - @max(a, @max(b, c));
}

fn benchTime(io: std.Io) i96 {
    return std.Io.Clock.awake.now(io).nanoseconds;
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    const summary = bitmap_diff.runThresholdReplay(sample_iterations);
    var ns_per_run: [sample_count]u64 = undefined;

    for (0..sample_count) |sample_index| {
        const started_at = benchTime(io);
        const candidate = bitmap_diff.runThresholdReplay(sample_iterations);
        const elapsed = benchTime(io) - started_at;
        if (candidate.checksum != summary.checksum or
            candidate.final_weight != summary.final_weight or
            candidate.final_first_set != summary.final_first_set or
            candidate.final_first_zero != summary.final_first_zero or
            candidate.final_nth_seven != summary.final_nth_seven or
            candidate.final_render_len != summary.final_render_len)
        {
            return error.NonDeterministicBitmapBench;
        }
        ns_per_run[sample_index] = @max(@as(u64, @intCast(elapsed)), 1);
    }

    const median_ns_per_run = median3(ns_per_run[0], ns_per_run[1], ns_per_run[2]);
    const ns_per_iteration = @max(
        @as(
            u64,
            @intCast(@divFloor(
                @as(i96, @intCast(median_ns_per_run)),
                @as(i96, @intCast(sample_iterations)),
            )),
        ),
        1,
    );

    std.debug.print(
        "phase4-bitmap-bench iterations={} samples={} median_ns_per_run={} ns_per_iteration={} checksum=0x{x} final_weight={} final_first_set={} final_first_zero={} final_nth_seven={} final_render_len={}\n",
        .{
            sample_iterations,
            sample_count,
            median_ns_per_run,
            ns_per_iteration,
            summary.checksum,
            summary.final_weight,
            summary.final_first_set,
            summary.final_first_zero,
            summary.final_nth_seven,
            summary.final_render_len,
        },
    );
}

const std = @import("std");
const bitmap_view = @import("bitmap_view");

pub const CpuMaskView = struct {
    bitmap: bitmap_view.BitmapView,

    pub fn init(words: []const usize, cpu_capacity: usize) CpuMaskView {
        return .{
            .bitmap = bitmap_view.BitmapView.init(words, cpu_capacity),
        };
    }

    pub fn hasCpu(self: CpuMaskView, cpu: usize) bool {
        return self.bitmap.isSet(cpu);
    }

    pub fn countPresentCpus(self: CpuMaskView) usize {
        return self.bitmap.countSetBits();
    }

    pub fn firstCpu(self: CpuMaskView) ?usize {
        return self.bitmap.firstSetBit();
    }

    pub fn nextCpu(self: CpuMaskView, start_cpu: usize) ?usize {
        return self.bitmap.nextSetBit(start_cpu);
    }

    pub fn firstMissingCpu(self: CpuMaskView) ?usize {
        return self.bitmap.firstClearBit();
    }

    pub fn nextMissingCpu(self: CpuMaskView, start_cpu: usize) ?usize {
        return self.bitmap.nextClearBit(start_cpu);
    }

    pub fn eql(self: CpuMaskView, other: CpuMaskView) bool {
        return self.bitmap.eql(other.bitmap);
    }

    pub fn isSubsetOf(self: CpuMaskView, other: CpuMaskView) bool {
        return self.bitmap.isSubsetOf(other.bitmap);
    }

    pub fn intersects(self: CpuMaskView, other: CpuMaskView) bool {
        return self.bitmap.intersects(other.bitmap);
    }
};

test "cpumask view can walk present and missing cpus from a bounded start point" {
    const words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 4) |
            (@as(usize, 1) << 7),
        std.math.maxInt(usize),
    };
    const view = CpuMaskView.init(words[0..], 8);

    try std.testing.expectEqual(@as(?usize, 1), view.nextCpu(0));
    try std.testing.expectEqual(@as(?usize, 4), view.nextCpu(2));
    try std.testing.expectEqual(@as(?usize, 7), view.nextCpu(7));
    try std.testing.expectEqual(@as(?usize, null), view.nextCpu(8));

    try std.testing.expectEqual(@as(?usize, 0), view.nextMissingCpu(0));
    try std.testing.expectEqual(@as(?usize, 2), view.nextMissingCpu(2));
    try std.testing.expectEqual(@as(?usize, 5), view.nextMissingCpu(5));
    try std.testing.expectEqual(@as(?usize, null), view.nextMissingCpu(8));
}

test "cpumask view keeps cpu presence and gaps explicit" {
    const words = [_]usize{
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 3) |
            (@as(usize, 1) << 5),
    };
    const view = CpuMaskView.init(words[0..], 8);

    try std.testing.expect(view.hasCpu(0));
    try std.testing.expect(!view.hasCpu(1));
    try std.testing.expect(view.hasCpu(5));
    try std.testing.expectEqual(@as(usize, 3), view.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 0), view.firstCpu());
    try std.testing.expectEqual(@as(?usize, 1), view.firstMissingCpu());
}

test "cpumask view equality ignores tail noise but catches active cpu drift" {
    const cpu_capacity = bitmap_view.word_bits + 4;
    const first_words = [_]usize{
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << 6),
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 3) |
            (@as(usize, 1) << 8),
    };
    const same_active_words = [_]usize{
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << 6),
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 3) |
            (@as(usize, 1) << 11),
    };
    const missing_active_words = [_]usize{
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << 6),
        @as(usize, 1) << 1,
    };

    const first = CpuMaskView.init(first_words[0..], cpu_capacity);
    const same_active = CpuMaskView.init(same_active_words[0..], cpu_capacity);
    const missing_active = CpuMaskView.init(missing_active_words[0..], cpu_capacity);

    try std.testing.expect(first.eql(same_active));
    try std.testing.expect(!first.eql(missing_active));
}

test "cpumask view keeps subset and overlap checks bounded to the declared capacity" {
    const base_words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 4) |
            (@as(usize, 1) << 6),
        std.math.maxInt(usize),
    };
    const superset_words = [_]usize{
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 4) |
            (@as(usize, 1) << 6) |
            (@as(usize, 1) << 7),
        0,
    };
    const disjoint_words = [_]usize{
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 2),
        0,
    };

    const base = CpuMaskView.init(base_words[0..], 8);
    const superset = CpuMaskView.init(superset_words[0..], 8);
    const disjoint = CpuMaskView.init(disjoint_words[0..], 8);

    try std.testing.expect(base.isSubsetOf(superset));
    try std.testing.expect(!superset.isSubsetOf(base));
    try std.testing.expect(base.intersects(superset));
    try std.testing.expect(!base.intersects(disjoint));
}

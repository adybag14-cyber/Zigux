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

    pub fn firstMissingCpu(self: CpuMaskView) ?usize {
        return self.bitmap.firstClearBit();
    }

    pub fn isSubsetOf(self: CpuMaskView, other: CpuMaskView) bool {
        return self.bitmap.isSubsetOf(other.bitmap);
    }

    pub fn intersects(self: CpuMaskView, other: CpuMaskView) bool {
        return self.bitmap.intersects(other.bitmap);
    }
};

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

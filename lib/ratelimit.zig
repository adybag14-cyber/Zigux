// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub const RATELIMIT_MSG_ON_RELEASE: u64 = 1 << 0;
pub const RATELIMIT_INITIALIZED: u64 = 1 << 63;

pub const RatelimitState = struct {
    interval: i64,
    burst: i64,
    begin: u64 = 0,
    n_left: i64 = 0,
    missed: u64 = 0,
    flags: u64 = 0,

    pub fn init(interval: i64, burst: i64) RatelimitState {
        return .{ .interval = interval, .burst = burst };
    }

    pub fn initWithFlags(interval: i64, burst: i64, flags: u64) RatelimitState {
        return .{ .interval = interval, .burst = burst, .flags = flags & ~RATELIMIT_INITIALIZED };
    }

    pub fn check(self: *RatelimitState, now: u64) bool {
        return ___ratelimit(self, now);
    }

    pub fn resetMiss(self: *RatelimitState) u64 {
        const missed = self.missed;
        self.missed = 0;
        return missed;
    }

    pub fn incMiss(self: *RatelimitState) void {
        if (self.missed != std.math.maxInt(u64)) self.missed += 1;
    }

    fn initialized(self: RatelimitState) bool {
        return (self.flags & RATELIMIT_INITIALIZED) != 0;
    }

    fn startWindow(self: *RatelimitState, now: u64) void {
        self.begin = now;
        self.n_left = self.burst;
        self.flags |= RATELIMIT_INITIALIZED;
    }
};

pub fn ___ratelimit(rs: *RatelimitState, now: u64) bool {
    const interval = rs.interval;
    const burst = rs.burst;
    var ret = false;

    if (interval <= 0 or burst <= 0) {
        ret = interval == 0 or burst > 0;
        if (rs.initialized() and !(interval == 0 and burst == 0)) {
            rs.flags &= ~RATELIMIT_INITIALIZED;
        }
        if (!ret) rs.incMiss();
        return ret;
    }

    if (!rs.initialized()) {
        rs.startWindow(now);
    }

    const expires = rs.begin +% @as(u64, @intCast(interval));
    if (now > expires) {
        rs.startWindow(now);
        if ((rs.flags & RATELIMIT_MSG_ON_RELEASE) == 0) {
            _ = rs.resetMiss();
        }
    }

    if (rs.n_left > 0) {
        rs.n_left -= 1;
        ret = true;
    }

    if (!ret) rs.incMiss();
    return ret;
}

test "ratelimit consumes burst budget" {
    var rs = RatelimitState.init(10, 2);

    try std.testing.expect(rs.check(100));
    try std.testing.expectEqual(@as(i64, 1), rs.n_left);
    try std.testing.expect(rs.check(101));
    try std.testing.expectEqual(@as(i64, 0), rs.n_left);
    try std.testing.expect(!rs.check(102));
    try std.testing.expectEqual(@as(u64, 1), rs.missed);
}

test "ratelimit resets only after interval has passed" {
    var rs = RatelimitState.init(10, 1);

    try std.testing.expect(rs.check(100));
    try std.testing.expect(!rs.check(101));
    try std.testing.expect(!rs.check(110));
    try std.testing.expectEqual(@as(u64, 2), rs.missed);

    try std.testing.expect(rs.check(111));
    try std.testing.expectEqual(@as(u64, 111), rs.begin);
    try std.testing.expectEqual(@as(i64, 0), rs.n_left);
    try std.testing.expectEqual(@as(u64, 0), rs.missed);
}

test "ratelimit zero interval never limits" {
    var rs = RatelimitState.init(0, 0);

    try std.testing.expect(rs.check(100));
    try std.testing.expect(rs.check(101));
    try std.testing.expectEqual(@as(u64, 0), rs.missed);
}

test "ratelimit zero burst with positive interval always limits" {
    var rs = RatelimitState.init(10, 0);

    try std.testing.expect(!rs.check(100));
    try std.testing.expect(!rs.check(111));
    try std.testing.expectEqual(@as(u64, 2), rs.missed);
}

test "ratelimit release flag preserves missed count across reset" {
    var rs = RatelimitState.initWithFlags(10, 1, RATELIMIT_MSG_ON_RELEASE);

    try std.testing.expect(rs.check(100));
    try std.testing.expect(!rs.check(101));
    try std.testing.expect(!rs.check(102));
    try std.testing.expectEqual(@as(u64, 2), rs.missed);
    try std.testing.expect(rs.check(111));
    try std.testing.expectEqual(@as(u64, 2), rs.missed);
}

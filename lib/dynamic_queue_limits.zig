// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub const BITS_PER_LONG: u64 = 64;
pub const DQL_HIST_LEN: usize = 4;
pub const UINT_MAX: u32 = std.math.maxInt(u32);
pub const DQL_MAX_OBJECT: u32 = UINT_MAX / 16;
pub const DQL_MAX_LIMIT: u32 = (UINT_MAX / 2) - DQL_MAX_OBJECT;

pub const Dql = struct {
    num_queued: u32 = 0,
    adj_limit: u32 = 0,
    last_obj_cnt: u32 = 0,
    stall_thrs: u16 = 0,
    history_head: u64 = 0,
    history: [DQL_HIST_LEN]u64 = .{ 0, 0, 0, 0 },

    limit: u32 = 0,
    num_completed: u32 = 0,
    prev_ovlimit: u32 = 0,
    prev_num_queued: u32 = 0,
    prev_last_obj_cnt: u32 = 0,
    lowest_slack: u32 = UINT_MAX,
    slack_start_time: u64 = 0,

    max_limit: u32 = DQL_MAX_LIMIT,
    min_limit: u32 = 0,
    slack_hold_time: u32 = 0,

    stall_max: u16 = 0,
    last_reap: u64 = 0,
    stall_cnt: u64 = 0,
    now: u64 = 0,

    pub fn init(hold_time: u32) Dql {
        var dql = Dql{ .slack_hold_time = hold_time };
        dql.resetAt(0);
        return dql;
    }

    pub fn setJiffies(self: *Dql, now: u64) void {
        self.now = now;
    }

    pub fn reset(self: *Dql) void {
        self.resetAt(self.now);
    }

    pub fn resetAt(self: *Dql, now: u64) void {
        self.now = now;
        self.limit = self.min_limit;
        self.num_queued = 0;
        self.num_completed = 0;
        self.last_obj_cnt = 0;
        self.prev_num_queued = 0;
        self.prev_last_obj_cnt = 0;
        self.prev_ovlimit = 0;
        self.lowest_slack = UINT_MAX;
        self.slack_start_time = now;
        self.last_reap = now;
        self.history_head = now / BITS_PER_LONG;
        self.history = .{ 0, 0, 0, 0 };
        self.adj_limit = self.limit;
    }

    pub fn queued(self: *Dql, count: u32) bool {
        if (count > DQL_MAX_OBJECT) return false;
        self.last_obj_cnt = count;
        self.num_queued +%= count;
        if (self.stall_thrs != 0) self.queueStall();
        return true;
    }

    pub fn avail(self: *const Dql) i32 {
        return clampI32(@as(i64, self.adj_limit) - @as(i64, self.num_queued));
    }

    pub fn completed(self: *Dql, count: u32) void {
        std.debug.assert(count <= self.num_queued -% self.num_completed);

        const num_queued = self.num_queued;
        const stall_thrs = self.stall_thrs;
        const completed_now = self.num_completed +% count;
        var limit = self.limit;
        var ovlimit = posdiff(num_queued -% self.num_completed, limit);
        const inprogress = num_queued -% completed_now;
        const prev_inprogress = self.prev_num_queued -% self.num_completed;
        const all_prev_completed = afterEq(completed_now, self.prev_num_queued);

        if ((ovlimit != 0 and inprogress == 0) or (self.prev_ovlimit != 0 and all_prev_completed)) {
            const grown = @as(u64, limit) + @as(u64, posdiff(completed_now, self.prev_num_queued)) + @as(u64, self.prev_ovlimit);
            limit = clampU32(grown, self.min_limit, self.max_limit);
            self.slack_start_time = self.now;
            self.lowest_slack = UINT_MAX;
        } else if (inprogress != 0 and prev_inprogress != 0 and !all_prev_completed) {
            const slack_basis = @as(u64, limit) + @as(u64, self.prev_ovlimit);
            const completed_delta = completed_now -% self.num_completed;
            var slack = posdiffWide(slack_basis, @as(u64, completed_delta) * 2);
            const slack_last_objs = if (self.prev_ovlimit != 0)
                posdiff(self.prev_last_obj_cnt, self.prev_ovlimit)
            else
                0;

            slack = @max(slack, slack_last_objs);
            if (slack < self.lowest_slack) self.lowest_slack = slack;

            if (self.now > self.slack_start_time +% self.slack_hold_time) {
                limit = posdiff(limit, self.lowest_slack);
                self.slack_start_time = self.now;
                self.lowest_slack = UINT_MAX;
            }
        }

        limit = clampU32(limit, self.min_limit, self.max_limit);
        if (limit != self.limit) {
            self.limit = limit;
            ovlimit = 0;
        }

        self.adj_limit = limit +% completed_now;
        self.prev_ovlimit = ovlimit;
        self.prev_last_obj_cnt = self.last_obj_cnt;
        self.num_completed = completed_now;
        self.prev_num_queued = num_queued;
        self.checkStall(stall_thrs);
    }

    fn queueStall(self: *Dql) void {
        const now_hi = self.now / BITS_PER_LONG;
        if (now_hi != self.history_head) {
            var slot = self.history_head + 1;
            while (slot <= now_hi and slot <= self.history_head + DQL_HIST_LEN) : (slot += 1) {
                self.history[@intCast(slot % DQL_HIST_LEN)] = 0;
            }
            if (now_hi > self.history_head + DQL_HIST_LEN) {
                self.history = .{ 0, 0, 0, 0 };
            }
            self.history_head = now_hi;
        }

        const bit: u6 = @intCast(self.now % BITS_PER_LONG);
        self.history[@intCast(now_hi % DQL_HIST_LEN)] |= @as(u64, 1) << bit;
    }

    fn checkStall(self: *Dql, stall_thrs: u16) void {
        if (stall_thrs == 0) return;
        const threshold: u64 = stall_thrs;
        if (self.now < self.last_reap +% threshold) return;

        const history_span = DQL_HIST_LEN * BITS_PER_LONG;
        var start = if (self.now >= history_span) self.now - history_span + 1 else 0;
        if (start < self.last_reap + 1) start = self.last_reap + 1;

        var end = self.now;
        if (end > threshold / 2) end -= threshold / 2;
        if (start <= end) {
            var t = start;
            while (t <= end) : (t += 1) {
                if (self.historyBit(t)) {
                    self.stall_cnt += 1;
                    const span = self.now - t;
                    self.stall_max = @max(self.stall_max, @as(u16, @intCast(@min(span, std.math.maxInt(u16)))));
                    break;
                }
            }
        }
        self.last_reap = self.now;
    }

    fn historyBit(self: *const Dql, t: u64) bool {
        const slot = (t / BITS_PER_LONG) % DQL_HIST_LEN;
        const bit: u6 = @intCast(t % BITS_PER_LONG);
        return (self.history[@intCast(slot)] & (@as(u64, 1) << bit)) != 0;
    }
};

pub fn dql_init(dql: *Dql, hold_time: u32) void {
    dql.* = Dql.init(hold_time);
}

pub fn dql_reset(dql: *Dql) void {
    dql.reset();
}

pub fn dql_queued(dql: *Dql, count: u32) bool {
    return dql.queued(count);
}

pub fn dql_avail(dql: *const Dql) i32 {
    return dql.avail();
}

pub fn dql_completed(dql: *Dql, count: u32) void {
    dql.completed(count);
}

fn posdiff(a: u32, b: u32) u32 {
    return if (a > b) a - b else 0;
}

fn posdiffWide(a: u64, b: u64) u32 {
    if (a <= b) return 0;
    return @intCast(@min(a - b, std.math.maxInt(u32)));
}

fn afterEq(a: u32, b: u32) bool {
    return a >= b;
}

fn clampU32(value: anytype, min_value: u32, max_value: u32) u32 {
    const wide: u64 = value;
    return @intCast(@min(@max(wide, min_value), max_value));
}

fn clampI32(value: i64) i32 {
    return @intCast(@min(@max(value, std.math.minInt(i32)), std.math.maxInt(i32)));
}

test "dql init reset and queued update availability" {
    var dql = Dql.init(50);

    try std.testing.expectEqual(DQL_MAX_LIMIT, dql.max_limit);
    try std.testing.expectEqual(@as(u32, 0), dql.limit);
    try std.testing.expectEqual(@as(i32, 0), dql_avail(&dql));
    try std.testing.expect(dql_queued(&dql, 10));
    try std.testing.expectEqual(@as(u32, 10), dql.num_queued);
    try std.testing.expectEqual(@as(i32, -10), dql_avail(&dql));
    try std.testing.expect(!dql_queued(&dql, DQL_MAX_OBJECT + 1));

    dql.min_limit = 8;
    dql.resetAt(7);
    try std.testing.expectEqual(@as(u32, 8), dql.limit);
    try std.testing.expectEqual(@as(i32, 8), dql_avail(&dql));
}

test "dql completed grows limit when queue starves" {
    var dql = Dql.init(10);
    dql.max_limit = 1000;
    dql.resetAt(0);

    try std.testing.expect(dql_queued(&dql, 100));
    dql_completed(&dql, 100);

    try std.testing.expectEqual(@as(u32, 100), dql.limit);
    try std.testing.expectEqual(@as(u32, 200), dql.adj_limit);
    try std.testing.expectEqual(@as(u32, 100), dql.num_completed);
    try std.testing.expectEqual(@as(i32, 100), dql_avail(&dql));
}

test "dql completed shrinks limit after slack hold time" {
    var dql = Dql.init(10);
    dql.max_limit = 1000;
    dql.resetAt(0);

    try std.testing.expect(dql_queued(&dql, 100));
    dql_completed(&dql, 100);
    try std.testing.expectEqual(@as(u32, 100), dql.limit);

    dql.setJiffies(1);
    try std.testing.expect(dql_queued(&dql, 100));
    dql_completed(&dql, 50);
    try std.testing.expectEqual(@as(u32, 100), dql.limit);

    dql.setJiffies(20);
    dql_completed(&dql, 25);
    try std.testing.expectEqual(@as(u32, 50), dql.limit);
    try std.testing.expectEqual(@as(u32, UINT_MAX), dql.lowest_slack);
}

test "dql stall history records delayed completion" {
    var dql = Dql.init(10);
    dql.stall_thrs = 10;
    dql.max_limit = 1000;
    dql.resetAt(0);

    dql.setJiffies(10);
    try std.testing.expect(dql_queued(&dql, 1));
    dql.setJiffies(30);
    dql_completed(&dql, 1);

    try std.testing.expectEqual(@as(u64, 1), dql.stall_cnt);
    try std.testing.expectEqual(@as(u16, 20), dql.stall_max);
    try std.testing.expectEqual(@as(u64, 30), dql.last_reap);
}

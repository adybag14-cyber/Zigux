// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub const Once = struct {
    done: bool = false,

    pub fn init() Once {
        return .{ .done = false };
    }

    pub fn start(self: *const Once) bool {
        return !self.done;
    }

    pub fn doneWork(self: *Once) void {
        self.done = true;
    }

    pub fn sleepableStart(self: *const Once) bool {
        return self.start();
    }

    pub fn sleepableDoneWork(self: *Once) void {
        self.doneWork();
    }

    pub fn run(self: *Once, comptime func: fn () void) void {
        if (!self.start()) return;
        func();
        self.doneWork();
    }

    pub fn sleepableRun(self: *Once, comptime func: fn () void) void {
        self.run(func);
    }
};

pub const SleepableOnce = Once;

pub fn __do_once_start(done: *const bool) bool {
    return !done.*;
}

pub fn __do_once_done(done: *bool) void {
    done.* = true;
}

pub const __do_once_sleepable_start = __do_once_start;
pub const __do_once_sleepable_done = __do_once_done;

test "once start returns true then false after done" {
    var once = Once.init();

    try std.testing.expect(once.start());
    once.doneWork();
    try std.testing.expect(!once.start());
}

test "once sleepable aliases mirror the same state transition" {
    var once = SleepableOnce.init();

    try std.testing.expect(once.sleepableStart());
    once.sleepableDoneWork();
    try std.testing.expect(!once.sleepableStart());
}

var run_calls: usize = 0;

fn countRun() void {
    run_calls += 1;
}

test "once run executes callback only once" {
    run_calls = 0;

    var once = Once.init();
    once.run(countRun);
    once.run(countRun);

    try std.testing.expectEqual(@as(usize, 1), run_calls);
    try std.testing.expect(once.done);
}

test "once C-style helpers operate on external done flag" {
    var done = false;

    try std.testing.expect(__do_once_start(&done));
    __do_once_done(&done);
    try std.testing.expect(!__do_once_start(&done));
    try std.testing.expect(!__do_once_sleepable_start(&done));
}

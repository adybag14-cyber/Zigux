pub const NOTIFIER_CHAIN_FLAG_EMPTY: u32 = 1;
pub const NOTIFIER_CHAIN_FLAG_TERMINATED: u32 = 2;
pub const NOTIFIER_CHAIN_FLAG_TRUNCATED: u32 = 4;
pub const NOTIFIER_CHAIN_FLAG_SELF_LOOP: u32 = 8;
pub const NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING: u32 = 16;

pub const NotifierBlockRef = extern struct {
    notifier_call: ?*const anyopaque,
    next: ?*const NotifierBlockRef,
    priority: i32,
};

pub const RawNotifierHeadRef = extern struct {
    head: ?*const NotifierBlockRef,
};

pub const NotifierChainView = extern struct {
    head: ?*const RawNotifierHeadRef,
    max_nodes: u32,
    reserved: u32 = 0,
};

pub const NotifierChainSummary = extern struct {
    length: u32,
    highest_priority: i32,
    lowest_priority: i32,
    flags: u32,
};

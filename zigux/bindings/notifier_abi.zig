pub const NOTIFIER_CHAIN_FLAG_EMPTY: u32 = 1;
pub const NOTIFIER_CHAIN_FLAG_TERMINATED: u32 = 2;
pub const NOTIFIER_CHAIN_FLAG_TRUNCATED: u32 = 4;
pub const NOTIFIER_CHAIN_FLAG_SELF_LOOP: u32 = 8;

pub const NotifierBlockRef = extern struct {
    notifier_call_addr: usize,
    next_addr: usize,
    priority: i32,
    reserved: u32,
};

pub const RawNotifierHeadRef = extern struct {
    head_addr: usize,
};

pub const NotifierChainView = extern struct {
    head_addr: usize,
    max_nodes: u32,
    reserved: u32,
};

pub const NotifierChainSummary = extern struct {
    length: u32,
    flags: u32,
    highest_priority: i32,
    lowest_priority: i32,
};

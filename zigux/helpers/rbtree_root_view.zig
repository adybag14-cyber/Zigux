const rbtree = @import("rbtree_bindings");

pub const KNOWN_FLAG_MASK = rbtree.KNOWN_FLAG_MASK;

pub fn empty() rbtree.RootView {
    return rbtree.empty();
}

pub fn uncached(root_addr: usize) rbtree.RootView {
    return rbtree.uncached(root_addr);
}

pub fn cached(root_addr: usize, leftmost_addr: usize) rbtree.RootView {
    return rbtree.cached(root_addr, leftmost_addr);
}

pub fn hasOnlyKnownFlags(view: rbtree.RootView) bool {
    return rbtree.hasOnlyKnownFlags(view);
}

pub fn hasRoot(view: rbtree.RootView) bool {
    return rbtree.hasRoot(view);
}

pub fn canonicalize(view: rbtree.RootView) ?rbtree.RootView {
    return rbtree.canonicalize(view);
}

pub fn isCanonical(view: rbtree.RootView) bool {
    return rbtree.isCanonical(view);
}

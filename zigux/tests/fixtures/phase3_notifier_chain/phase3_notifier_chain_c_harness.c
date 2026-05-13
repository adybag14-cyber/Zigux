#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

enum notifier_result {
    NOTIFY_DONE = 0,
    NOTIFY_OK = 1,
    NOTIFY_STOP = 2,
};

struct notifier_block {
    uintptr_t notifier_call;
    uintptr_t next;
    int32_t priority;
};

static size_t notifier_len(const struct notifier_block *head) {
    size_t count = 0;
    const struct notifier_block *node = head;
    while (node != NULL) {
        count += 1;
        node = (const struct notifier_block *)node->next;
    }
    return count;
}

static bool has_nonincreasing_priority(const struct notifier_block *head) {
    const struct notifier_block *node = head;
    if (node == NULL) {
        return true;
    }

    int32_t previous_priority = node->priority;
    node = (const struct notifier_block *)node->next;
    while (node != NULL) {
        if (node->priority > previous_priority) {
            return false;
        }
        previous_priority = node->priority;
        node = (const struct notifier_block *)node->next;
    }
    return true;
}

static void write_scenario(const char *name, const struct notifier_block *head) {
    const struct notifier_block *node = head;
    const struct notifier_block *last = NULL;
    size_t index = 0;

    printf("\"%s\":{\"len\":%zu,\"first_priority\":", name, notifier_len(head));
    if (head != NULL) {
        printf("%d", head->priority);
    } else {
        fputs("null", stdout);
    }

    while (node != NULL) {
        last = node;
        node = (const struct notifier_block *)node->next;
    }

    fputs(",\"last_priority\":", stdout);
    if (last != NULL) {
        printf("%d", last->priority);
    } else {
        fputs("null", stdout);
    }

    printf(",\"nonincreasing\":%s,\"priorities\":[",
           has_nonincreasing_priority(head) ? "true" : "false");

    node = head;
    while (node != NULL) {
        if (index != 0) {
            fputc(',', stdout);
        }
        printf("%d", node->priority);
        node = (const struct notifier_block *)node->next;
        index += 1;
    }

    fputs("]}", stdout);
}

int main(void) {
    struct notifier_block ordered_tail = {
        .notifier_call = 0,
        .next = 0,
        .priority = -4,
    };
    struct notifier_block ordered_middle = {
        .notifier_call = 0,
        .next = (uintptr_t)&ordered_tail,
        .priority = 3,
    };
    struct notifier_block ordered_head = {
        .notifier_call = 0,
        .next = (uintptr_t)&ordered_middle,
        .priority = 12,
    };
    struct notifier_block unordered_tail = {
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    struct notifier_block unordered_head = {
        .notifier_call = 0,
        .next = (uintptr_t)&unordered_tail,
        .priority = 1,
    };

    fputc('{', stdout);
    write_scenario("empty", NULL);
    fputc(',', stdout);
    write_scenario("ordered", &ordered_head);
    fputc(',', stdout);
    write_scenario("unordered", &unordered_head);
    printf(",\"results\":{\"done\":%u,\"ok\":%u,\"stop\":%u}}\n",
           NOTIFY_DONE,
           NOTIFY_OK,
           NOTIFY_STOP);
    return 0;
}

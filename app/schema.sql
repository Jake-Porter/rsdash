CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game TEXT NOT NULL CHECK(game IN ('rs3','osrs')),
    rsn TEXT NOT NULL,
    UNIQUE(game, rsn)
);

CREATE TABLE IF NOT EXISTS xp_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    skill TEXT NOT NULL,
    level INTEGER NOT NULL,
    xp INTEGER NOT NULL,
    captured_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_xp_account_skill_time ON xp_snapshots(account_id, skill, captured_at);

CREATE TABLE IF NOT EXISTS boss_kc_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    activity TEXT NOT NULL,
    score INTEGER NOT NULL,
    captured_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_kc_account_activity_time ON boss_kc_snapshots(account_id, activity, captured_at);

CREATE TABLE IF NOT EXISTS activity_feed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    event_type TEXT NOT NULL,
    text TEXT NOT NULL,
    details TEXT,
    occurred_at TEXT,
    raw_hash TEXT NOT NULL UNIQUE,
    fetched_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_feed_account_time ON activity_feed(account_id, id);

CREATE TABLE IF NOT EXISTS weekly_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL DEFAULT 'weekly' CHECK(category IN ('daily','weekly')),
    sort_order INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS weekly_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES weekly_tasks(id),
    period_start TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    UNIQUE(task_id, period_start)
);

CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    title TEXT NOT NULL,
    notes TEXT,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','done')),
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS goal_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL REFERENCES goals(id),
    note TEXT NOT NULL,
    created_at TEXT NOT NULL
);

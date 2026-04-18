CREATE TABLE IF NOT EXISTS servers (
    guild_id            BIGINT PRIMARY KEY,
    region_count        INTEGER DEFAULT 50,
    setup_at            TIMESTAMP DEFAULT NOW(),
    turn                INTEGER DEFAULT 1,
    paused              BOOLEAN DEFAULT FALSE,
    turn_interval_hours INTEGER DEFAULT 24
);

CREATE TABLE IF NOT EXISTS players (
    discord_id      BIGINT,
    server_id       BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    gold            INTEGER DEFAULT 300,
    food            INTEGER DEFAULT 200,
    materials       INTEGER DEFAULT 200,
    influence       INTEGER DEFAULT 0,
    prestige        INTEGER DEFAULT 0,
    grace_until     TIMESTAMP,
    registered_at   TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (discord_id, server_id)
);

CREATE TABLE IF NOT EXISTS regions (
    id              SERIAL PRIMARY KEY,
    server_id       BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    terrain         TEXT NOT NULL,
    seed_x          FLOAT NOT NULL,
    seed_y          FLOAT NOT NULL,
    adjacency       INTEGER[] DEFAULT '{}',
    owner_id        BIGINT,
    dev             INTEGER DEFAULT 0,
    stabilized      BOOLEAN DEFAULT TRUE,
    is_spawn        BOOLEAN DEFAULT FALSE,
    captured_at     TIMESTAMP,
    last_action_at  TIMESTAMP
);

CREATE TABLE IF NOT EXISTS buildings (
    id          SERIAL PRIMARY KEY,
    server_id   BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    region_id   INTEGER REFERENCES regions(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    tier        INTEGER DEFAULT 1,
    built_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS units (
    id              SERIAL PRIMARY KEY,
    server_id       BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    owner_id        BIGINT NOT NULL,
    home_region     INTEGER REFERENCES regions(id) ON DELETE SET NULL,
    current_region  INTEGER REFERENCES regions(id) ON DELETE SET NULL,
    unit_type       TEXT NOT NULL,
    size            INTEGER DEFAULT 0,
    is_levy         BOOLEAN DEFAULT TRUE,
    army_id         INTEGER
);

CREATE TABLE IF NOT EXISTS armies (
    id          SERIAL PRIMARY KEY,
    server_id   BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    owner_id    BIGINT NOT NULL,
    name        TEXT,
    region_id   INTEGER REFERENCES regions(id) ON DELETE SET NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS frontlines (
    id              SERIAL PRIMARY KEY,
    server_id       BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    region_id       INTEGER REFERENCES regions(id) ON DELETE CASCADE,
    attacker_id     BIGINT,
    defender_id     BIGINT,
    attacker_army   INTEGER REFERENCES armies(id) ON DELETE SET NULL,
    defender_army   INTEGER REFERENCES armies(id) ON DELETE SET NULL,
    started_at      TIMESTAMP DEFAULT NOW(),
    resolved        BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS research (
    id          SERIAL PRIMARY KEY,
    server_id   BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    player_id   BIGINT NOT NULL,
    research_id TEXT NOT NULL,
    unlocked_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (server_id, player_id, research_id)
);

CREATE TABLE IF NOT EXISTS traditions (
    id              SERIAL PRIMARY KEY,
    server_id       BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    player_id       BIGINT NOT NULL,
    tradition_id    TEXT NOT NULL,
    unlocked_at     TIMESTAMP DEFAULT NOW(),
    UNIQUE (server_id, player_id, tradition_id)
);

CREATE TABLE IF NOT EXISTS treaties (
    id              SERIAL PRIMARY KEY,
    server_id       BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    player_a        BIGINT NOT NULL,
    player_b        BIGINT NOT NULL,
    treaty_type     TEXT NOT NULL,
    status          TEXT DEFAULT 'pending',
    offered_at      TIMESTAMP DEFAULT NOW(),
    resolved_at     TIMESTAMP,
    expires_at      TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wars (
    id              SERIAL PRIMARY KEY,
    server_id       BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    attacker_id     BIGINT NOT NULL,
    defender_id     BIGINT NOT NULL,
    declared_at     TIMESTAMP DEFAULT NOW(),
    hostilities_at  TIMESTAMP,
    ended_at        TIMESTAMP,
    active          BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS market_orders (
    id          SERIAL PRIMARY KEY,
    server_id   BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    player_id   BIGINT NOT NULL,
    resource    TEXT NOT NULL,
    amount      INTEGER NOT NULL,
    price       INTEGER NOT NULL,
    order_type  TEXT NOT NULL,
    filled      BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_prices (
    server_id   BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    resource    TEXT NOT NULL,
    price       INTEGER NOT NULL,
    updated_at  TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (server_id, resource)
);

CREATE TABLE IF NOT EXISTS events_log (
    id          SERIAL PRIMARY KEY,
    server_id   BIGINT REFERENCES servers(guild_id) ON DELETE CASCADE,
    turn        INTEGER,
    event_type  TEXT NOT NULL,
    target      TEXT,
    description TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

INSERT INTO market_prices (server_id, resource, price)
SELECT guild_id, 'gold', 1 FROM servers
UNION ALL
SELECT guild_id, 'food', 2 FROM servers
UNION ALL
SELECT guild_id, 'materials', 3 FROM servers
ON CONFLICT DO NOTHING;

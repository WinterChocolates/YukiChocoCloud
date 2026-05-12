CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(64)   NOT NULL UNIQUE,
    hashed_password VARCHAR(128) NOT NULL,
    is_admin    BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_users_username ON users (username);


CREATE TABLE files (
    id          SERIAL PRIMARY KEY,
    owner_id    INTEGER       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id   INTEGER       REFERENCES files(id) ON DELETE CASCADE,
    name        VARCHAR(255)  NOT NULL,
    is_dir      BOOLEAN       NOT NULL DEFAULT FALSE,
    is_deleted  BOOLEAN       NOT NULL DEFAULT FALSE,
    size        BIGINT        NOT NULL DEFAULT 0,
    storage_path VARCHAR(1024),
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_files_owner_id   ON files (owner_id);
CREATE INDEX ix_files_parent_id  ON files (parent_id);
CREATE INDEX ix_files_is_deleted ON files (is_deleted);


CREATE TABLE shares (
    id          SERIAL PRIMARY KEY,
    file_id     INTEGER       NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    token       VARCHAR(64)   NOT NULL UNIQUE,
    password    VARCHAR(128),
    expire_at   TIMESTAMP,
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_shares_file_id ON shares (file_id);
CREATE INDEX ix_shares_token   ON shares (token);


INSERT INTO users (username, hashed_password, is_admin)
VALUES ('yukichoco', '$2b$12$y/NR0muIUZrZOWT86PqhwOhXBX6vCzip6l7h7mHcTY9baDj6SmFva', true);
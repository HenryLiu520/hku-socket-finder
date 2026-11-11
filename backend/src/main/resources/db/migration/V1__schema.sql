-- V1: schema for Socket Finder (CCST9003 R21)
-- one row per socket, not per room: that is the unit of the whole design

CREATE TABLE account (
  id            BIGSERIAL PRIMARY KEY,
  email         VARCHAR(120) NOT NULL UNIQUE,
  display_name  VARCHAR(80)  NOT NULL,
  role          VARCHAR(16)  NOT NULL CHECK (role IN ('STUDENT','MAINTENANCE')),
  password_hash VARCHAR(120) NOT NULL,
  created_at    TIMESTAMP    NOT NULL DEFAULT now()
);

CREATE TABLE building (
  id   BIGSERIAL PRIMARY KEY,
  code VARCHAR(16) NOT NULL UNIQUE,
  name VARCHAR(80) NOT NULL
);

CREATE TABLE floor (
  id          BIGSERIAL PRIMARY KEY,
  building_id BIGINT      NOT NULL REFERENCES building(id) ON DELETE CASCADE,
  level       VARCHAR(16) NOT NULL,
  plan_image  VARCHAR(160),
  UNIQUE (building_id, level)
);

CREATE TABLE room (
  id       BIGSERIAL PRIMARY KEY,
  floor_id BIGINT      NOT NULL REFERENCES floor(id) ON DELETE CASCADE,
  code     VARCHAR(32) NOT NULL UNIQUE,
  name     VARCHAR(80) NOT NULL
);

CREATE TABLE seat (
  id      BIGSERIAL PRIMARY KEY,
  room_id BIGINT      NOT NULL REFERENCES room(id) ON DELETE CASCADE,
  label   VARCHAR(16) NOT NULL,
  x       INT         NOT NULL DEFAULT 0,
  y       INT         NOT NULL DEFAULT 0
);

CREATE TABLE socket (
  id              BIGSERIAL PRIMARY KEY,
  seat_id         BIGINT      NOT NULL REFERENCES seat(id) ON DELETE CASCADE,
  kind            VARCHAR(16) NOT NULL DEFAULT 'WALL',
  state           VARCHAR(16) NOT NULL DEFAULT 'UNKNOWN'
                  CHECK (state IN ('WORKING','BROKEN','REPAIRED','UNKNOWN')),
  last_checked_at TIMESTAMP
);
CREATE INDEX idx_socket_seat  ON socket (seat_id);
CREATE INDEX idx_socket_state ON socket (state);

CREATE TABLE report (
  id             BIGSERIAL PRIMARY KEY,
  socket_id      BIGINT      NOT NULL REFERENCES socket(id) ON DELETE CASCADE,
  account_id     BIGINT      NOT NULL REFERENCES account(id),
  reported_state VARCHAR(16) NOT NULL CHECK (reported_state IN ('WORKING','BROKEN')),
  created_at     TIMESTAMP   NOT NULL DEFAULT now()
);
CREATE INDEX idx_report_socket_time ON report (socket_id, created_at DESC);
CREATE INDEX idx_report_account     ON report (account_id, socket_id, created_at DESC);

CREATE TABLE repair (
  id         BIGSERIAL PRIMARY KEY,
  socket_id  BIGINT      NOT NULL REFERENCES socket(id) ON DELETE CASCADE,
  staff_id   BIGINT      NOT NULL REFERENCES account(id),
  note       VARCHAR(200),
  created_at TIMESTAMP   NOT NULL DEFAULT now()
);

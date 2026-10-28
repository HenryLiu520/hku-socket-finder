-- V2: one floor, three rooms, seats and sockets typed in by hand (Chi Wah level 1)
INSERT INTO building (code, name) VALUES ('CW', 'Chi Wah Learning Commons');

INSERT INTO floor (building_id, level)
SELECT id, 'L1' FROM building WHERE code = 'CW';

INSERT INTO room (floor_id, code, name)
SELECT f.id, v.code, v.name
FROM floor f
JOIN building b ON b.id = f.building_id
JOIN (VALUES
  ('CW-L1-A', 'Open study area A'),
  ('CW-L1-B', 'Open study area B'),
  ('CW-L1-C', 'Group room C')
) AS v(code, name) ON TRUE
WHERE b.code = 'CW' AND f.level = 'L1';

-- six seats per room, two sockets on every other seat
INSERT INTO seat (room_id, label, x, y)
SELECT r.id, s.label, s.x, s.y
FROM room r
JOIN (VALUES
  ('1', 1, 1), ('2', 2, 1), ('3', 3, 1),
  ('4', 1, 2), ('5', 2, 2), ('6', 3, 2)
) AS s(label, x, y) ON TRUE
WHERE r.code LIKE 'CW-L1-%';

INSERT INTO socket (seat_id, kind, state, last_checked_at)
SELECT s.id, 'WALL', 'UNKNOWN', NULL
FROM seat s
JOIN room r ON r.id = s.room_id
WHERE r.code LIKE 'CW-L1-%'
  AND s.label IN ('1', '2', '4', '5');

INSERT INTO socket (seat_id, kind, state, last_checked_at)
SELECT s.id, 'SHARED_STRIP', 'UNKNOWN', NULL
FROM seat s
JOIN room r ON r.id = s.room_id
WHERE r.code LIKE 'CW-L1-%'
  AND s.label IN ('2', '5');

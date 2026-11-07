-- Demo state for the pitch: a handful of cases that make the colours, the ages
-- and the reporter counts mean something on screen.
-- Run:  psql -h 127.0.0.1 -p 5433 -U ran -d socketfinder -v ON_ERROR_STOP=1 -f scripts/demo-reset.sql

BEGIN;

DELETE FROM repair;
DELETE FROM report;

UPDATE socket SET state = 'UNKNOWN', last_checked_at = NULL;

CREATE OR REPLACE FUNCTION demo_report(p_code text, p_state text, p_hours int) RETURNS void AS $$
DECLARE
    v_socket bigint;
    v_acc1   bigint;
    v_acc2   bigint;
BEGIN
    SELECT s.id INTO v_socket FROM socket s WHERE s.code = p_code;
    IF v_socket IS NULL THEN
        RAISE NOTICE 'no socket %, skipped', p_code;
        RETURN;
    END IF;
    SELECT a.id INTO v_acc1 FROM account a WHERE a.email = 'student1@connect.hku.hk';
    SELECT a.id INTO v_acc2 FROM account a WHERE a.email = 'student2@connect.hku.hk';

    INSERT INTO report (socket_id, account_id, reported_state, created_at)
    VALUES (v_socket, v_acc1, p_state, now() - make_interval(hours => p_hours + 1)),
           (v_socket, v_acc2, p_state, now() - make_interval(hours => p_hours));

    UPDATE socket SET state = p_state, last_checked_at = now() - make_interval(hours => p_hours)
     WHERE id = v_socket;
END;
$$ LANGUAGE plpgsql;

-- CW L1-B is the room used in the video
SELECT demo_report('CW-L1-B-0002', 'NO_POWER', 52);
SELECT demo_report('CW-L1-B-0004', 'LOOSE', 2);
SELECT demo_report('CW-L1-B-0001', 'WORKING', 26);
SELECT demo_report('CW-L1-A-0002', 'WORKING', 5);

-- other buildings, so the first screen is not one empty campus
SELECT demo_report('MW-T1-0003', 'LOOSE', 6);
SELECT demo_report('MW-T1-0001', 'WORKING', 20);
SELECT demo_report('CPD-LG01-0007', 'NO_POWER', 49);
SELECT demo_report('CPD-LG01-0001', 'WORKING', 30);
SELECT demo_report('KK-101-0005', 'LOOSE', 3);
SELECT demo_report('KK-201-0002', 'WORKING', 27);

-- one record nobody touched for 45 days: it must read as old, not as fine
SELECT demo_report('KK-101-0004', 'WORKING', 45 * 24);

DROP FUNCTION demo_report(text, text, int);

COMMIT;

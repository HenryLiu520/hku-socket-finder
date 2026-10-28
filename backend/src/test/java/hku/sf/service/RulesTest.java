package hku.sf.service;

import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;

class RulesTest {

    private final LocalDateTime now = LocalDateTime.of(2026, 10, 23, 12, 0);

    @Test
    void twoReportsAreNeededToFlip() {
        assertEquals(2, Rules.reportsStillNeeded(0, 2));
        assertEquals(1, Rules.reportsStillNeeded(1, 2));
        assertEquals(0, Rules.reportsStillNeeded(2, 2));
        assertEquals(0, Rules.reportsStillNeeded(3, 2));
    }

    @Test
    void aCheckOlderThanThirtyDaysIsStale() {
        assertTrue(Rules.isStale(now.minusDays(31), now, 30));
        assertFalse(Rules.isStale(now.minusDays(29), now, 30));
        assertFalse(Rules.isStale(null, now, 30));   // never checked is unknown, not stale
    }

    @Test
    void oneReportPerAccountPerWindow() {
        assertTrue(Rules.alreadyReported(now.minusHours(2), now, 24));
        assertFalse(Rules.alreadyReported(now.minusHours(25), now, 24));
        assertFalse(Rules.alreadyReported(null, now, 24));
    }

    @Test
    void daysSinceIsNullWhenNeverChecked() {
        assertNull(Rules.daysSince(null, now));
        assertEquals(5, Rules.daysSince(now.minusDays(5), now));
    }
}

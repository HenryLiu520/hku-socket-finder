package hku.sf.service;

import hku.sf.domain.SocketState;
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
    void tenReportsADayIsTheCeiling() {
        assertFalse(Rules.overDailyQuota(9, 10));
        assertTrue(Rules.overDailyQuota(10, 10));
        assertTrue(Rules.overDailyQuota(11, 10));
    }

    @Test
    void daysSinceIsNullWhenNeverChecked() {
        assertNull(Rules.daysSince(null, now));
        assertEquals(5, Rules.daysSince(now.minusDays(5), now));
    }

    @Test
    void aNewAccountSitsAtNeutral() {
        assertEquals(0.5, Rules.score(0, 0), 1e-9);
        assertEquals(1.0, Rules.weight(0, 0), 1e-9);
    }

    @Test
    void theScoreIsAnErrorRateWithAPrior() {
        // three right, one wrong: (3 + 2.5) / (4 + 5)
        assertEquals(5.5 / 9.0, Rules.score(3, 1), 1e-9);
        assertTrue(Rules.score(20, 0) > Rules.score(3, 1));
        assertTrue(Rules.score(3, 10) < 0.5);
    }

    @Test
    void theWeightRunsFromAHalfToOneAndAHalf() {
        assertEquals(0.5 + 2.5 / 5.0, Rules.weight(0, 0), 1e-9);
        assertTrue(Rules.weight(1000, 0) <= 1.5 + 1e-9);
        assertTrue(Rules.weight(0, 1000) >= 0.5 - 1e-9);
    }

    @Test
    void twoStrangersCanFlipAndOneExpertCannot() {
        var twoStrangers = new java.util.EnumMap<hku.sf.domain.SocketState, java.util.List<Double>>(
                hku.sf.domain.SocketState.class);
        twoStrangers.put(hku.sf.domain.SocketState.LOOSE, java.util.List.of(1.0, 1.0));
        assertEquals(hku.sf.domain.SocketState.LOOSE, Rules.winningState(twoStrangers));

        var oneExpert = new java.util.EnumMap<hku.sf.domain.SocketState, java.util.List<Double>>(
                hku.sf.domain.SocketState.class);
        oneExpert.put(hku.sf.domain.SocketState.LOOSE, java.util.List.of(1.5));
        assertNull(Rules.winningState(oneExpert));       // ceiling is below the threshold
    }

    @Test
    void aDisagreementUnderTheDominanceRuleKeepsTheOldState() {
        var split = new java.util.EnumMap<hku.sf.domain.SocketState, java.util.List<Double>>(
                hku.sf.domain.SocketState.class);
        split.put(hku.sf.domain.SocketState.LOOSE, java.util.List.of(1.3));
        split.put(hku.sf.domain.SocketState.NO_POWER, java.util.List.of(0.9));
        assertNull(Rules.winningState(split));
    }

    @Test
    void onlyTheThreeHeaviestAccountsCount() {
        var crowd = new java.util.EnumMap<hku.sf.domain.SocketState, java.util.List<Double>>(
                hku.sf.domain.SocketState.class);
        crowd.put(hku.sf.domain.SocketState.WORKING, java.util.List.of(1.0, 1.0, 1.0, 0.1, 0.1));
        assertEquals(hku.sf.domain.SocketState.WORKING, Rules.winningState(crowd));
        // the two light accounts cannot carry a rival state on their own
        var light = new java.util.EnumMap<hku.sf.domain.SocketState, java.util.List<Double>>(
                hku.sf.domain.SocketState.class);
        light.put(hku.sf.domain.SocketState.WORKING, java.util.List.of(0.5, 0.5));
        assertNull(Rules.winningState(light));
    }

    @Test
    void aRepairJudgesOnlyTheReportsThatNamedItsFault() {
        assertEquals(Rules.Settlement.CONFIRM, Rules.settlementFor(SocketState.LOOSE, SocketState.LOOSE));
        assertEquals(Rules.Settlement.REFUTE, Rules.settlementFor(SocketState.NO_POWER, SocketState.LOOSE));
        // an honest "works" is not punished by a fault found later
        assertEquals(Rules.Settlement.LEAVE, Rules.settlementFor(SocketState.WORKING, SocketState.LOOSE));
        assertEquals(Rules.Settlement.LEAVE, Rules.settlementFor(SocketState.REPAIRED, SocketState.NO_POWER));
    }
}

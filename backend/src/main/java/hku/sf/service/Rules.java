package hku.sf.service;

import hku.sf.domain.SocketState;

import java.time.Duration;
import java.time.LocalDateTime;

/** Pure functions for the three rules in the plan. Kept separate so they can be tested without a database. */
public final class Rules {

    private Rules() { }

    /** How many more independent reports are needed before the state may flip. */
    public static int reportsStillNeeded(int distinctReports, int required) {
        return Math.max(0, required - distinctReports);
    }

    /** A check older than the window is shown as old, never silently trusted. */
    public static boolean isStale(LocalDateTime lastChecked, LocalDateTime now, int staleDays) {
        if (lastChecked == null) return false;
        return Duration.between(lastChecked, now).toDays() > staleDays;
    }

    public static Long daysSince(LocalDateTime lastChecked, LocalDateTime now) {
        if (lastChecked == null) return null;
        return Duration.between(lastChecked, now).toDays();
    }

    /**
     * One report per account per socket per window, and a ceiling per account per day.
     * The per-socket rule stops one person flipping a socket alone; the daily cap stops
     * someone sweeping a whole floor in an hour.
     */
    public static boolean overDailyQuota(long reportsToday, int cap) {
        return reportsToday >= cap;
    }

    /**
     * Reputation is an error rate with a prior, not a count: a new account sits at 0.5,
     * and only settled reports move it. Beta(2.5, 2.5) is the prior behind the formula.
     */
    public static double score(int confirmed, int refuted) {
        return (confirmed + 2.5) / (confirmed + refuted + 5.0);
    }

    /** What one report is worth: 0.5 to 1.5, neutral at 1.0 for a new account. */
    public static double weight(int confirmed, int refuted) {
        return 0.5 + score(confirmed, refuted);
    }

    /** Evidence needed before a state can take hold, and how far it must lead the rival. */
    public static final double EVIDENCE_THRESHOLD = 1.6;
    public static final double DOMINANCE = 1.5;
    public static final int TOP_ACCOUNTS = 3;

    /**
     * Sum the heaviest weights behind each candidate state, then pick a winner: it must
     * clear the threshold and lead every rival by half again. Because the ceiling is 1.5,
     * no single account can ever win alone, however good its record.
     */
    public static SocketState winningState(java.util.Map<SocketState, java.util.List<Double>> byState) {
        java.util.Map<SocketState, Double> sums = new java.util.EnumMap<>(SocketState.class);
        for (var e : byState.entrySet()) {
            double sum = e.getValue().stream()
                    .sorted(java.util.Comparator.reverseOrder())
                    .limit(TOP_ACCOUNTS)
                    .mapToDouble(Double::doubleValue)
                    .sum();
            sums.put(e.getKey(), sum);
        }
        SocketState best = null;
        double bestSum = 0, second = 0;
        for (var e : sums.entrySet()) {
            if (e.getValue() > bestSum) {
                second = bestSum;
                bestSum = e.getValue();
                best = e.getKey();
            } else if (e.getValue() > second) {
                second = e.getValue();
            }
        }
        if (best == null || bestSum < EVIDENCE_THRESHOLD) return null;
        if (bestSum < DOMINANCE * second) return null;      // a disputed socket keeps its state
        return best;
    }

    /** What a repair does to one report: confirms it, refutes it, or leaves it alone. */
    public enum Settlement { CONFIRM, REFUTE, LEAVE }

    /**
     * A repair judges the reports that named the fault it fixed. A report of "works" is not
     * punished by a later fault, because the socket may simply have broken after it was
     * checked; it stays unsettled rather than becoming a black mark.
     */
    public static Settlement settlementFor(SocketState reported, SocketState closed) {
        if (reported == closed) return Settlement.CONFIRM;
        boolean reportedFault = reported == SocketState.LOOSE || reported == SocketState.NO_POWER
                || reported == SocketState.BROKEN;
        boolean closedFault = closed == SocketState.LOOSE || closed == SocketState.NO_POWER
                || closed == SocketState.BROKEN;
        if (reportedFault && closedFault) return Settlement.REFUTE;   // named the wrong fault
        return Settlement.LEAVE;
    }

    /** One report per account per socket per window. */
    public static boolean alreadyReported(LocalDateTime lastReportAt, LocalDateTime now, int windowHours) {
        if (lastReportAt == null) return false;
        return Duration.between(lastReportAt, now).toHours() < windowHours;
    }
}

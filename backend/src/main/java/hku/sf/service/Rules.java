package hku.sf.service;

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

    /** One report per account per socket per window. */
    public static boolean alreadyReported(LocalDateTime lastReportAt, LocalDateTime now, int windowHours) {
        if (lastReportAt == null) return false;
        return Duration.between(lastReportAt, now).toHours() < windowHours;
    }
}

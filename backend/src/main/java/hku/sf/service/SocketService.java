package hku.sf.service;

import hku.sf.domain.*;
import hku.sf.domain.Report;
import hku.sf.repo.AccountRepository;
import hku.sf.repo.ReportRepository;
import hku.sf.repo.RepairRepository;
import hku.sf.repo.SocketRepository;
import hku.sf.web.ApiException;
import hku.sf.web.Dtos;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class SocketService {

    private final SocketRepository sockets;
    private final ReportRepository reports;
    private final RepairRepository repairs;
    private final AccountRepository accounts;

    @Value("${app.stale-days:30}") private int staleDays;
    @Value("${app.reports-needed:2}") private int reportsNeeded;
    @Value("${app.report-window-hours:24}") private int windowHours;
    @Value("${app.reports-per-day:10}") private int reportsPerDay;
    @Value("${app.evidence-window-hours:72}") private int evidenceWindowHours;

    public SocketService(SocketRepository sockets, ReportRepository reports, RepairRepository repairs,
                         AccountRepository accounts) {
        this.sockets = sockets;
        this.reports = reports;
        this.repairs = repairs;
        this.accounts = accounts;
    }

    public Dtos.SocketDto toDto(SocketPoint s, LocalDateTime now, long reportsToday) {
        return toDto(s, now, reportsToday, null);
    }

    public Dtos.SocketDto toDto(SocketPoint s, LocalDateTime now, long reportsToday, LocalDateTime lastReportAt) {
        Long days = Rules.daysSince(s.lastCheckedAt, now);
        return new Dtos.SocketDto(s.id, s.code, s.kind, s.state.name(), s.lastCheckedAt, days,
                Rules.isStale(s.lastCheckedAt, now, staleDays), reportsToday,
                Rules.reportsStillNeeded((int) reportsToday, reportsNeeded), lastReportAt);
    }

    @Transactional
    public Dtos.ReportResult report(Long socketId, Account account, String stateText) {
        SocketPoint s = sockets.findById(socketId)
                .orElseThrow(() -> new ApiException("NOT_FOUND", "No such socket", 404));

        SocketState state;
        try {
            state = SocketState.valueOf(stateText == null ? "" : stateText.trim().toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new ApiException("BAD_STATE", "Report working or broken", 400);
        }
        if (state != SocketState.WORKING && state != SocketState.LOOSE && state != SocketState.NO_POWER) {
            throw new ApiException("BAD_STATE", "Report working, loose or no power", 400);
        }

        LocalDateTime now = LocalDateTime.now();
        long mine = reports.countBySocketIdAndAccountIdAndCreatedAtAfter(socketId, account.id, now.minusHours(windowHours));
        if (mine > 0) {
            throw new ApiException("TOO_SOON", "You already reported this socket today", 429);
        }

        long today = reports.countByAccountIdAndCreatedAtAfter(account.id, java.time.LocalDate.now().atStartOfDay());
        if (Rules.overDailyQuota(today, reportsPerDay)) {
            throw new ApiException("DAILY_CAP", "That is " + reportsPerDay + " reports today, come back tomorrow", 429);
        }

        s.lastCheckedAt = now;          // a report is a check, even when the state does not move
        Report r = new Report();
        r.socket = s;
        r.account = account;
        r.reportedState = state;
        r.createdAt = now;
        reports.save(r);

        java.util.Map<SocketState, java.util.List<Double>> evidence = evidence(socketId, now);
        SocketState winner = Rules.winningState(evidence);
        boolean flipped = false;
        if (winner != null && winner != SocketState.REPAIRED && s.state != winner) {
            s.state = winner;
            s.lastCheckedAt = now;
            sockets.save(s);
            flipped = true;
        }

        double behindThisState = evidence.getOrDefault(state, java.util.List.of()).stream()
                .sorted(java.util.Comparator.reverseOrder())
                .limit(Rules.TOP_ACCOUNTS)
                .mapToDouble(Double::doubleValue)
                .sum();
        String message = flipped
                ? "State changed to " + winner.name().toLowerCase()
                : String.format(java.util.Locale.ROOT,
                    "Report saved. %.1f of %.1f evidence needed to change the state",
                    behindThisState, Rules.EVIDENCE_THRESHOLD);

        return new Dtos.ReportResult(toDto(s, now, 1), flipped, message);
    }

    @Transactional
    public Dtos.SocketDto repair(Long socketId, Account staff, String note) {
        SocketPoint s = sockets.findById(socketId)
                .orElseThrow(() -> new ApiException("NOT_FOUND", "No such socket", 404));
        LocalDateTime now = LocalDateTime.now();
        settle(s, now);
        Repair r = new Repair();
        r.socket = s;
        r.staff = staff;
        r.note = note;
        r.createdAt = now;
        repairs.save(r);
        s.state = SocketState.REPAIRED;
        s.lastCheckedAt = now;
        sockets.save(s);
        return toDto(s, now, 0);
    }

    /** What the accounts currently believe about one socket, weights included. */
    private java.util.Map<SocketState, java.util.List<Double>> evidence(Long socketId, LocalDateTime now) {
        java.util.Map<SocketState, java.util.List<Double>> byState = new java.util.EnumMap<>(SocketState.class);
        for (Object[] row : reports.lastReportPerAccount(socketId, now.minusHours(evidenceWindowHours))) {
            Long accountId = ((Number) row[0]).longValue();
            SocketState reported = SocketState.valueOf((String) row[1]);
            accounts.findById(accountId).ifPresent(a ->
                    byState.computeIfAbsent(reported, k -> new java.util.ArrayList<>())
                           .add(Rules.weight(a.confirmed, a.refuted)));
        }
        return byState;
    }

    /**
     * Closing a repair settles everybody who spoke about this socket in the window: they
     * were either right about the fault that was fixed, or they were not. This is the only
     * thing that moves a score.
     */
    private void settle(SocketPoint s, LocalDateTime now) {
        if (s.state != SocketState.LOOSE && s.state != SocketState.NO_POWER && s.state != SocketState.BROKEN) {
            return;
        }
        for (Report r : reports.unsettled(s.id, now.minusHours(evidenceWindowHours))) {
            Rules.Settlement verdict = Rules.settlementFor(r.reportedState, s.state);
            r.settledAt = now;                       // judged once, and it stops being evidence
            reports.save(r);
            if (verdict == Rules.Settlement.LEAVE) continue;
            accounts.findById(r.account.id).ifPresent(a -> {
                if (verdict == Rules.Settlement.CONFIRM) a.confirmed++; else a.refuted++;
                accounts.save(a);
            });
        }
    }

    public List<Dtos.QueueRow> queue() {
        LocalDateTime now = LocalDateTime.now();
        return sockets.queueByStates(java.util.List.of(SocketState.LOOSE, SocketState.NO_POWER, SocketState.BROKEN)).stream()
                .map(s -> new Dtos.QueueRow(
                        s.id,
                        s.code,
                        s.seat.room.floor.building.code,
                        s.seat.room.code,
                        s.seat.room.name,
                        s.seat.label,
                        Rules.daysSince(s.lastCheckedAt, now),
                        s.lastCheckedAt,
                        s.state.name(),
                        reports.countDistinctAccounts(s.id, s.state, now.minusDays(7))))
                .toList();
    }
}

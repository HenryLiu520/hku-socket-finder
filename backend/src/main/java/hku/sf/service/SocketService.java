package hku.sf.service;

import hku.sf.domain.*;
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

    @Value("${app.stale-days:30}") private int staleDays;
    @Value("${app.reports-needed:2}") private int reportsNeeded;
    @Value("${app.report-window-hours:24}") private int windowHours;

    public SocketService(SocketRepository sockets, ReportRepository reports, RepairRepository repairs) {
        this.sockets = sockets;
        this.reports = reports;
        this.repairs = repairs;
    }

    public Dtos.SocketDto toDto(SocketPoint s, LocalDateTime now, long reportsToday) {
        Long days = Rules.daysSince(s.lastCheckedAt, now);
        return new Dtos.SocketDto(s.id, s.kind, s.state.name(), s.lastCheckedAt, days,
                Rules.isStale(s.lastCheckedAt, now, staleDays), reportsToday,
                Rules.reportsStillNeeded((int) reportsToday, reportsNeeded));
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
        if (state != SocketState.WORKING && state != SocketState.BROKEN) {
            throw new ApiException("BAD_STATE", "Report working or broken", 400);
        }

        LocalDateTime now = LocalDateTime.now();
        long mine = reports.countBySocketIdAndAccountIdAndCreatedAtAfter(socketId, account.id, now.minusHours(windowHours));
        if (mine > 0) {
            throw new ApiException("TOO_SOON", "You already reported this socket today", 429);
        }

        Report r = new Report();
        r.socket = s;
        r.account = account;
        r.reportedState = state;
        r.createdAt = now;
        reports.save(r);

        long distinct = reports.countDistinctAccounts(socketId, state, now.minusHours(windowHours));
        boolean flipped = false;
        if (distinct >= reportsNeeded && s.state != state) {
            s.state = state;
            s.lastCheckedAt = now;
            sockets.save(s);
            flipped = true;
        }

        String message = flipped
                ? "State changed to " + state.name().toLowerCase()
                : "Report saved. " + Rules.reportsStillNeeded((int) distinct, reportsNeeded) + " more report(s) needed to change the state";

        return new Dtos.ReportResult(toDto(s, now, 1), flipped, message);
    }

    @Transactional
    public Dtos.SocketDto repair(Long socketId, Account staff, String note) {
        SocketPoint s = sockets.findById(socketId)
                .orElseThrow(() -> new ApiException("NOT_FOUND", "No such socket", 404));
        LocalDateTime now = LocalDateTime.now();
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

    public List<Dtos.QueueRow> queue() {
        LocalDateTime now = LocalDateTime.now();
        return sockets.queueByState(SocketState.BROKEN).stream()
                .map(s -> new Dtos.QueueRow(
                        s.id,
                        s.seat.room.floor.building.code,
                        s.seat.room.code,
                        s.seat.room.name,
                        s.seat.label,
                        Rules.daysSince(s.lastCheckedAt, now),
                        s.lastCheckedAt,
                        s.state.name(),
                        reports.countDistinctAccounts(s.id, SocketState.BROKEN, now.minusDays(7))))
                .toList();
    }
}

package hku.sf.service;

import hku.sf.domain.*;
import hku.sf.repo.*;
import hku.sf.web.ApiException;
import hku.sf.web.Dtos;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class CatalogService {

    private final BuildingRepository buildings;
    private final FloorRepository floors;
    private final RoomRepository rooms;
    private final SeatRepository seats;
    private final SocketRepository sockets;
    private final ReportRepository reports;
    private final SocketService socketService;

    public CatalogService(BuildingRepository buildings, FloorRepository floors, RoomRepository rooms,
                          SeatRepository seats, SocketRepository sockets, ReportRepository reports,
                          SocketService socketService) {
        this.buildings = buildings;
        this.floors = floors;
        this.rooms = rooms;
        this.seats = seats;
        this.sockets = sockets;
        this.reports = reports;
        this.socketService = socketService;
    }

    /** LG, then G, then the numbered floors upward. Alphabetical order puts "3" before "LG". */
    private static int floorRank(String level) {
        String l = level == null ? "" : level.trim().toUpperCase();
        if (l.equals("LG")) return 0;
        if (l.equals("G")) return 1;
        try {
            return 10 + Integer.parseInt(l);
        } catch (NumberFormatException e) {
            return 900;
        }
    }

    @Transactional(readOnly = true)
    public List<Dtos.BuildingDto> tree() {
        return buildings.findAll().stream()
                .map(b -> new Dtos.BuildingDto(b.id, b.code, b.name,
                        floors.findByBuildingIdOrderByLevel(b.id).stream()
                                .sorted(java.util.Comparator.comparingInt(f -> floorRank(f.level)))
                                .map(f -> new Dtos.FloorDto(f.id, f.level))
                                .toList()))
                .toList();
    }

    /** Every room in a building, in floor then room order, for the room picker. */
    @Transactional(readOnly = true)
    public List<Dtos.RoomOption> roomsOfBuilding(Long buildingId) {
        List<Dtos.RoomOption> out = new ArrayList<>();
        for (Floor f : floors.findByBuildingIdOrderByLevel(buildingId)) {
            for (Room r : rooms.findByFloorIdOrderByCode(f.id)) {
                out.add(new Dtos.RoomOption(r.id, r.code, r.name, f.level));
            }
        }
        return out;
    }

    @Transactional(readOnly = true)
    public List<Dtos.RoomSummaryDto> rooms(Long floorId) {
        List<Room> list = rooms.findByFloorIdOrderByCode(floorId);
        if (list.isEmpty()) return List.of();

        List<Long> roomIds = list.stream().map(r -> r.id).toList();
        List<Seat> allSeats = seats.findByRoomIdInOrderByYAscXAsc(roomIds);
        Map<Long, List<Seat>> byRoom = allSeats.stream().collect(Collectors.groupingBy(s -> s.room.id));
        List<Long> seatIds = allSeats.stream().map(s -> s.id).toList();
        List<SocketPoint> allSockets = seatIds.isEmpty() ? List.of() : sockets.findBySeatIdIn(seatIds);
        Map<Long, List<SocketPoint>> bySeat = allSockets.stream().collect(Collectors.groupingBy(s -> s.seat.id));

        List<Dtos.RoomSummaryDto> out = new ArrayList<>();
        for (Room r : list) {
            List<Seat> rs = byRoom.getOrDefault(r.id, List.of());
            int sockets_ = 0, working = 0, broken = 0, repaired = 0, loose = 0, noPower = 0, unknown = 0;
            LocalDateTime lastCheck = null;
            for (Seat s : rs) {
                for (SocketPoint sp : bySeat.getOrDefault(s.id, List.of())) {
                    sockets_++;
                    if (sp.state == SocketState.WORKING) working++;
                    if (sp.state == SocketState.LOOSE) loose++;
                    if (sp.state == SocketState.NO_POWER) noPower++;
                    if (sp.state == SocketState.BROKEN) broken++;
                    if (sp.state == SocketState.REPAIRED) repaired++;
                    if (sp.state == SocketState.UNKNOWN) unknown++;
                    if (sp.lastCheckedAt != null && (lastCheck == null || sp.lastCheckedAt.isAfter(lastCheck))) {
                        lastCheck = sp.lastCheckedAt;
                    }
                }
            }
            out.add(new Dtos.RoomSummaryDto(r.id, r.code, r.name, rs.size(), sockets_, working, broken, repaired,
                    loose, noPower, unknown, lastCheck));
        }
        return out;
    }

    @Transactional(readOnly = true)
    public Dtos.RoomDto room(Long roomId, Long accountId) {
        Room r = rooms.findById(roomId)
                .orElseThrow(() -> new ApiException("NOT_FOUND", "No such room", 404));
        LocalDateTime now = LocalDateTime.now();
        List<Seat> rs = seats.findByRoomIdOrderByYAscXAsc(roomId);
        List<Long> seatIds = rs.stream().map(s -> s.id).toList();
        List<SocketPoint> ss = seatIds.isEmpty() ? List.of() : sockets.findBySeatIdIn(seatIds);
        Map<Long, List<SocketPoint>> bySeat = ss.stream().collect(Collectors.groupingBy(s -> s.seat.id));

        // one query for every socket in the room, instead of one per socket
        Map<Long, LocalDateTime> lastReport = new HashMap<>();
        if (!ss.isEmpty()) {
            for (Object[] row : reports.lastReportTimes(ss.stream().map(x -> x.id).toList())) {
                lastReport.put((Long) row[0], (LocalDateTime) row[1]);
            }
        }

        List<Dtos.SeatDto> seatDtos = new ArrayList<>();
        for (Seat s : rs) {
            List<Dtos.SocketDto> socketDtos = new ArrayList<>();
            for (SocketPoint sp : bySeat.getOrDefault(s.id, List.of())) {
                long mine = accountId == null ? 0
                        : reports.countBySocketIdAndAccountIdAndCreatedAtAfter(sp.id, accountId, now.minusHours(24));
                socketDtos.add(socketService.toDto(sp, now, mine, lastReport.get(sp.id)));
            }
            seatDtos.add(new Dtos.SeatDto(s.id, s.label, s.x, s.y, socketDtos));
        }
        return new Dtos.RoomDto(r.id, r.code, r.name,
                r.floor.level, r.floor.building.code, r.floor.building.name, seatDtos);
    }
}

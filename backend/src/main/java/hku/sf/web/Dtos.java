package hku.sf.web;

import java.time.LocalDateTime;
import java.util.List;

public final class Dtos {

    public record LoginRequest(String email, String password) { }
    public record LoginResponse(String token, String email, String displayName, String role) { }
    public record MeResponse(Long id, String email, String displayName, String role) { }
    public record ApiError(String code, String message) { }

    public record DemoAccount(String email, String password, String displayName, String role, String note) { }

    public record BuildingDto(Long id, String code, String name, List<FloorDto> floors) { }
    public record FloorDto(Long id, String level) { }
    /** One entry in the room picker: enough to pick a room and nothing else. */
    public record RoomOption(Long id, String code, String name, String level) { }
    public record RoomSummaryDto(Long id, String code, String name, int seats, int sockets, int working, int broken, int repaired) { }

    public record SocketDto(Long id, String code, String kind, String state, LocalDateTime lastCheckedAt,
                            Long daysSinceCheck, boolean stale, long myReportsToday, int reportsStillNeeded) { }
    public record SeatDto(Long id, String label, int x, int y, List<SocketDto> sockets) { }
    public record RoomDto(Long id, String code, String name, String level, String buildingCode,
                          String buildingName, List<SeatDto> seats) { }

    public record ReportRequest(String state) { }
    public record ReportResult(SocketDto socket, boolean flipped, String message) { }

    public record QueueRow(Long socketId, String code, String building, String roomCode, String roomName,
                           String seat, Long daysBroken, LocalDateTime lastCheckedAt, String state,
                           long reporters) { }

    public record RepairRequest(String note) { }
}

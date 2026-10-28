package hku.sf.web;

import hku.sf.domain.Account;
import hku.sf.domain.Role;
import hku.sf.service.AuthService;
import hku.sf.service.SocketService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
public class SocketController {

    private final SocketService sockets;
    private final AuthService auth;

    public SocketController(SocketService sockets, AuthService auth) {
        this.sockets = sockets;
        this.auth = auth;
    }

    @PostMapping("/sockets/{socketId}/report")
    public Dtos.ReportResult report(@PathVariable Long socketId,
                                    @RequestBody Dtos.ReportRequest req,
                                    @RequestHeader(value = "Authorization", required = false) String header) {
        Account a = auth.resolve(header)
                .orElseThrow(() -> new ApiException("UNAUTHORISED", "Sign in to report", 401));
        if (a.role != Role.STUDENT) {
            throw new ApiException("FORBIDDEN", "Only students report a socket", 403);
        }
        return sockets.report(socketId, a, req.state());
    }

    @PostMapping("/sockets/{socketId}/repair")
    public Dtos.SocketDto repair(@PathVariable Long socketId,
                                 @RequestBody(required = false) Dtos.RepairRequest req,
                                 @RequestHeader(value = "Authorization", required = false) String header) {
        Account a = auth.resolve(header)
                .orElseThrow(() -> new ApiException("UNAUTHORISED", "Sign in first", 401));
        if (a.role != Role.MAINTENANCE) {
            throw new ApiException("FORBIDDEN", "Only maintenance can close a repair", 403);
        }
        return sockets.repair(socketId, a, req == null ? null : req.note());
    }

    @GetMapping("/maintenance/queue")
    public List<Dtos.QueueRow> queue(@RequestHeader(value = "Authorization", required = false) String header) {
        Account a = auth.resolve(header)
                .orElseThrow(() -> new ApiException("UNAUTHORISED", "Sign in first", 401));
        if (a.role != Role.MAINTENANCE) {
            throw new ApiException("FORBIDDEN", "Maintenance only", 403);
        }
        return sockets.queue();
    }
}

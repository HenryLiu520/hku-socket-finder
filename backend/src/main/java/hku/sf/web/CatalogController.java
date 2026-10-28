package hku.sf.web;

import hku.sf.domain.Account;
import hku.sf.service.AuthService;
import hku.sf.service.CatalogService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
public class CatalogController {

    private final CatalogService catalog;
    private final AuthService auth;

    public CatalogController(CatalogService catalog, AuthService auth) {
        this.catalog = catalog;
        this.auth = auth;
    }

    @GetMapping("/buildings")
    public List<Dtos.BuildingDto> buildings() {
        return catalog.tree();
    }

    @GetMapping("/buildings/{buildingId}/rooms")
    public List<Dtos.RoomOption> buildingRooms(@PathVariable Long buildingId) {
        return catalog.roomsOfBuilding(buildingId);
    }

    @GetMapping("/floors/{floorId}/rooms")
    public List<Dtos.RoomSummaryDto> rooms(@PathVariable Long floorId) {
        return catalog.rooms(floorId);
    }

    @GetMapping("/rooms/{roomId}")
    public Dtos.RoomDto room(@PathVariable Long roomId,
                             @RequestHeader(value = "Authorization", required = false) String header) {
        Account a = auth.resolve(header).orElse(null);
        return catalog.room(roomId, a == null ? null : a.id);
    }
}

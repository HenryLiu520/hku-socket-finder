package hku.sf.repo;

import hku.sf.domain.Room;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface RoomRepository extends JpaRepository<Room, Long> {
    List<Room> findByFloorIdOrderByCode(Long floorId);
}

package hku.sf.repo;

import hku.sf.domain.Seat;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface SeatRepository extends JpaRepository<Seat, Long> {
    List<Seat> findByRoomIdOrderByYAscXAsc(Long roomId);
    List<Seat> findByRoomIdInOrderByYAscXAsc(List<Long> roomIds);
}

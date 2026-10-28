package hku.sf.repo;

import hku.sf.domain.SocketPoint;
import hku.sf.domain.SocketState;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;

public interface SocketRepository extends JpaRepository<SocketPoint, Long> {

    List<SocketPoint> findBySeatIdIn(List<Long> seatIds);

    List<SocketPoint> findBySeatIdInAndState(List<Long> seatIds, SocketState state);

    @Query("""
           select s from SocketPoint s
           join fetch s.seat st
           join fetch st.room r
           join fetch r.floor f
           join fetch f.building b
           where s.state in :states
           order by s.lastCheckedAt asc nulls last
           """)
    List<SocketPoint> queueByStates(@Param("states") List<SocketState> states);
}

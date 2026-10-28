package hku.sf.repo;

import hku.sf.domain.Floor;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface FloorRepository extends JpaRepository<Floor, Long> {
    List<Floor> findByBuildingIdOrderByLevel(Long buildingId);
}

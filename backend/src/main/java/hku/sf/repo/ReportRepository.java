package hku.sf.repo;

import hku.sf.domain.Report;
import hku.sf.domain.SocketState;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.time.LocalDateTime;

public interface ReportRepository extends JpaRepository<Report, Long> {

    long countBySocketIdAndAccountIdAndCreatedAtAfter(Long socketId, Long accountId, LocalDateTime since);

    long countByAccountIdAndCreatedAtAfter(Long accountId, LocalDateTime since);

    @Query("""
           select count(distinct r.account.id) from Report r
           where r.socket.id = :socketId and r.reportedState = :state and r.createdAt > :since
           """)
    long countDistinctAccounts(@Param("socketId") Long socketId,
                               @Param("state") SocketState state,
                               @Param("since") LocalDateTime since);
}

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

    /**
     * One row per account: the last thing that account said about this socket inside the
     * window. Evidence and settlement both read this, so neither counts an account twice.
     */
    @Query(value = """
           select distinct on (r.account_id) r.account_id, r.reported_state, r.created_at
             from report r
            where r.socket_id = :socketId and r.created_at > :since
            order by r.account_id, r.created_at desc
           """, nativeQuery = true)
    java.util.List<Object[]> lastReportPerAccount(@Param("socketId") Long socketId,
                                                 @Param("since") LocalDateTime since);

    @Query("""
           select r.socket.id, max(r.createdAt) from Report r
           where r.socket.id in :socketIds
           group by r.socket.id
           """)
    java.util.List<Object[]> lastReportTimes(@Param("socketIds") java.util.List<Long> socketIds);

    @Query("""
           select count(distinct r.account.id) from Report r
           where r.socket.id = :socketId and r.reportedState = :state and r.createdAt > :since
           """)
    long countDistinctAccounts(@Param("socketId") Long socketId,
                               @Param("state") SocketState state,
                               @Param("since") LocalDateTime since);
}

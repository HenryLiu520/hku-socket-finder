package hku.sf.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "report")
public class Report {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @ManyToOne @JoinColumn(name = "socket_id", nullable = false) public SocketPoint socket;
    @ManyToOne @JoinColumn(name = "account_id", nullable = false) public Account account;
    @Enumerated(EnumType.STRING) @Column(name = "reported_state", nullable = false) public SocketState reportedState;
    @Column(name = "created_at", nullable = false) public LocalDateTime createdAt = LocalDateTime.now();
}

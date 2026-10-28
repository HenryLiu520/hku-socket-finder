package hku.sf.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "repair")
public class Repair {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @ManyToOne @JoinColumn(name = "socket_id", nullable = false) public SocketPoint socket;
    @ManyToOne @JoinColumn(name = "staff_id", nullable = false) public Account staff;
    public String note;
    @Column(name = "created_at", nullable = false) public LocalDateTime createdAt = LocalDateTime.now();
}

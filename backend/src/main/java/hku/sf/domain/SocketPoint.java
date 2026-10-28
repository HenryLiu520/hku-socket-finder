package hku.sf.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/** A power socket. Named SocketPoint so it does not shadow java.net.Socket. */
@Entity
@Table(name = "socket")
public class SocketPoint {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @ManyToOne @JoinColumn(name = "seat_id", nullable = false) public Seat seat;
    /** The number printed on the desk: building-floor-room-seat-socket. */
    @Column(nullable = false) public String code;
    @Column(nullable = false) public String kind = "WALL";
    @Enumerated(EnumType.STRING) @Column(nullable = false) public SocketState state = SocketState.UNKNOWN;
    @Column(name = "last_checked_at") public LocalDateTime lastCheckedAt;
}

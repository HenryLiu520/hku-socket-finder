package hku.sf.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "seat")
public class Seat {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @ManyToOne @JoinColumn(name = "room_id", nullable = false) public Room room;
    @Column(nullable = false) public String label;
    @Column(nullable = false) public int x;
    @Column(nullable = false) public int y;
}

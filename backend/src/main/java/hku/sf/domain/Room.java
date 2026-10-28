package hku.sf.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "room")
public class Room {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @ManyToOne @JoinColumn(name = "floor_id", nullable = false) public Floor floor;
    @Column(nullable = false, unique = true) public String code;
    @Column(nullable = false) public String name;
}

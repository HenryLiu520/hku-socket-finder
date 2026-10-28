package hku.sf.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "floor")
public class Floor {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @ManyToOne @JoinColumn(name = "building_id", nullable = false) public Building building;
    @Column(nullable = false) public String level;
    @Column(name = "plan_image") public String planImage;
}

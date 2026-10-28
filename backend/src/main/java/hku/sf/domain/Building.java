package hku.sf.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "building")
public class Building {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @Column(nullable = false, unique = true) public String code;
    @Column(nullable = false) public String name;
}

package hku.sf.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "account")
public class Account {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @Column(nullable = false, unique = true) public String email;
    @Column(name = "display_name", nullable = false) public String displayName;
    @Enumerated(EnumType.STRING) @Column(nullable = false) public Role role;
    @Column(name = "password_hash", nullable = false) public String passwordHash;
    @Column(name = "created_at", nullable = false) public LocalDateTime createdAt = LocalDateTime.now();
}

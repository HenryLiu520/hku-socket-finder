package hku.sf.service;

import hku.sf.domain.Account;
import hku.sf.repo.AccountRepository;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/** Minimal token auth for the prototype: a token per sign in, kept in memory. */
@Service
public class AuthService {

    public record Session(String token, Account account, LocalDateTime expiresAt) { }

    private final AccountRepository accounts;
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
    private final Map<String, Session> sessions = new ConcurrentHashMap<>();

    public AuthService(AccountRepository accounts) {
        this.accounts = accounts;
    }

    public Optional<Session> login(String email, String password) {
        return accounts.findByEmailIgnoreCase(email == null ? "" : email.trim())
                .filter(a -> encoder.matches(password == null ? "" : password, a.passwordHash))
                .map(a -> {
                    String token = UUID.randomUUID().toString().replace("-", "");
                    Session s = new Session(token, a, LocalDateTime.now().plusHours(8));
                    sessions.put(token, s);
                    return s;
                });
    }

    public Optional<Account> resolve(String header) {
        String token = token(header);
        if (token == null) return Optional.empty();
        Session s = sessions.get(token);
        if (s == null || s.expiresAt().isBefore(LocalDateTime.now())) {
            sessions.remove(token);
            return Optional.empty();
        }
        return Optional.of(s.account());
    }

    public void logout(String header) {
        String token = token(header);
        if (token != null) sessions.remove(token);
    }

    public String encode(String raw) {
        return encoder.encode(raw);
    }

    private String token(String header) {
        if (header == null) return null;
        String v = header.trim();
        if (v.regionMatches(true, 0, "Bearer ", 0, 7)) return v.substring(7).trim();
        return v.isEmpty() ? null : v;
    }
}

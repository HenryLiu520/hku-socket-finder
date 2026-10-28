package hku.sf.web;

import hku.sf.domain.Account;
import hku.sf.service.AuthService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService auth;

    public AuthController(AuthService auth) {
        this.auth = auth;
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Dtos.LoginRequest req) {
        Optional<AuthService.Session> s = auth.login(req.email(), req.password());
        if (s.isEmpty()) {
            return ResponseEntity.status(401).body(new Dtos.ApiError("BAD_CREDENTIALS", "Wrong email or password"));
        }
        Account a = s.get().account();
        return ResponseEntity.ok(new Dtos.LoginResponse(s.get().token(), a.email, a.displayName, a.role.name()));
    }

    @GetMapping("/me")
    public ResponseEntity<?> me(@RequestHeader(value = "Authorization", required = false) String header) {
        return auth.resolve(header)
                .map(a -> ResponseEntity.ok((Object) new Dtos.MeResponse(a.id, a.email, a.displayName, a.role.name())))
                .orElseGet(() -> ResponseEntity.status(401).body(new Dtos.ApiError("UNAUTHORISED", "Sign in first")));
    }

    @GetMapping("/demo-accounts")
    public List<Dtos.DemoAccount> demoAccounts() {
        return List.of(
                new Dtos.DemoAccount("student1@connect.hku.hk", "demo1234", "Student A", "STUDENT",
                        "student, first reporter"),
                new Dtos.DemoAccount("student2@connect.hku.hk", "demo1234", "Student B", "STUDENT",
                        "student, second reporter needed to flip a socket"),
                new Dtos.DemoAccount("estates@hku.hk", "demo1234", "Estates Office", "MAINTENANCE",
                        "maintenance, sees the repair queue")
        );
    }
}

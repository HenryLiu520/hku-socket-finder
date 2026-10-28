package hku.sf.config;

import hku.sf.domain.Account;
import hku.sf.domain.Role;
import hku.sf.repo.AccountRepository;
import hku.sf.service.AuthService;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.ApplicationArguments;
import org.springframework.stereotype.Component;

/** Three demo accounts, created once, so the two-report rule can actually be shown. */
@Component
public class DemoAccounts implements ApplicationRunner {

    private final AccountRepository accounts;
    private final AuthService auth;

    public DemoAccounts(AccountRepository accounts, AuthService auth) {
        this.accounts = accounts;
        this.auth = auth;
    }

    @Override
    public void run(ApplicationArguments args) {
        seed("student1@connect.hku.hk", "Student A", Role.STUDENT);
        seed("student2@connect.hku.hk", "Student B", Role.STUDENT);
        seed("estates@hku.hk", "Estates Office", Role.MAINTENANCE);
    }

    private void seed(String email, String name, Role role) {
        if (accounts.findByEmailIgnoreCase(email).isPresent()) return;
        Account a = new Account();
        a.email = email;
        a.displayName = name;
        a.role = role;
        a.passwordHash = auth.encode("demo1234");
        accounts.save(a);
    }
}

package com.tiendatech.authservice.config;

import com.tiendatech.authservice.model.AppUser;
import com.tiendatech.authservice.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
public class DataInitializer {

    @Bean
    public CommandLineRunner seedUsers(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        return args -> {
            if (userRepository.findByUsername("admin").isEmpty()) {
                AppUser admin = new AppUser("admin", passwordEncoder.encode("P@ssw0rd"), "ROLE_USER");
                userRepository.save(admin);
            }
        };
    }
}

package com.tiendatech.authservice.service;

import com.tiendatech.authservice.model.AppUser;
import com.tiendatech.authservice.model.JwtResponse;
import com.tiendatech.authservice.model.LoginRequest;
import com.tiendatech.authservice.model.RegisterRequest;
import com.tiendatech.authservice.repository.UserRepository;
import com.tiendatech.authservice.security.JwtTokenProvider;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public AuthService(AuthenticationManager authenticationManager,
                       JwtTokenProvider jwtTokenProvider,
                       UserRepository userRepository,
                       PasswordEncoder passwordEncoder) {
        this.authenticationManager = authenticationManager;
        this.jwtTokenProvider = jwtTokenProvider;
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public AppUser register(RegisterRequest request) {
        if (userRepository.findByUsername(request.getUsername()).isPresent()) {
            throw new RuntimeException("El usuario ya existe: " + request.getUsername());
        }
        AppUser user = new AppUser(
                request.getUsername(),
                passwordEncoder.encode(request.getPassword()),
                "ROLE_USER"
        );
        return userRepository.save(user);
    }

    public JwtResponse login(LoginRequest loginRequest) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(loginRequest.getUsername(), loginRequest.getPassword())
        );
        String token = jwtTokenProvider.generateToken(authentication);
        return new JwtResponse(token, jwtTokenProvider.getExpirationMillis());
    }

    public String validateToken(String token) {
        jwtTokenProvider.validateToken(token);
        return jwtTokenProvider.getUsernameFromToken(token);
    }
}

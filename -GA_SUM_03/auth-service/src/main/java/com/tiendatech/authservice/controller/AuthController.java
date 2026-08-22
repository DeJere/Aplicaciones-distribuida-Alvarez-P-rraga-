package com.tiendatech.authservice.controller;

import com.tiendatech.authservice.model.ApiResponse;
import com.tiendatech.authservice.model.AppUser;
import com.tiendatech.authservice.model.JwtResponse;
import com.tiendatech.authservice.model.LoginRequest;
import com.tiendatech.authservice.model.RegisterRequest;
import com.tiendatech.authservice.service.AuthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.AuthenticationException;
import org.springframework.web.bind.annotation.*;

import java.util.Collections;
import java.util.Map;

@RestController
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/register")
    public ResponseEntity<ApiResponse<Map<String, Object>>> register(@RequestBody RegisterRequest request) {
        try {
            AppUser user = authService.register(request);
            Map<String, Object> data = Map.of("username", user.getUsername(), "roles", user.getRoles());
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(new ApiResponse<>(201, data, "Usuario registrado exitosamente"));
        } catch (RuntimeException ex) {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(new ApiResponse<>(409, null, ex.getMessage()));
        }
    }

    @PostMapping("/login")
    public ResponseEntity<ApiResponse<JwtResponse>> login(@RequestBody LoginRequest loginRequest) {
        try {
            JwtResponse token = authService.login(loginRequest);
            return ResponseEntity.ok(new ApiResponse<>(200, token, "Autenticación exitosa"));
        } catch (AuthenticationException ex) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(new ApiResponse<>(401, null, "Credenciales inválidas"));
        }
    }

    @GetMapping("/validate")
    public ResponseEntity<ApiResponse<Map<String, Object>>> validate(
            @RequestHeader(value = "Authorization", required = false) String authorizationHeader,
            @RequestParam(value = "token", required = false) String tokenParam) {

        String token = extractToken(authorizationHeader, tokenParam);
        if (token == null || token.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(new ApiResponse<>(401, null, "Token no proporcionado"));
        }

        try {
            String username = authService.validateToken(token);
            return ResponseEntity.ok(new ApiResponse<>(200,
                    Collections.unmodifiableMap(Map.of("username", username, "valid", true)),
                    "Token válido"));
        } catch (RuntimeException ex) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(new ApiResponse<>(401, null, ex.getMessage()));
        }
    }

    private String extractToken(String authorizationHeader, String tokenParam) {
        if (authorizationHeader != null && authorizationHeader.startsWith("Bearer ")) {
            return authorizationHeader.substring(7);
        }
        return tokenParam;
    }
}

package com.tiendatech.authservice.model;

public class JwtResponse {

    private final String token;
    private final long expiresIn;

    public JwtResponse(String token, long expiresIn) {
        this.token = token;
        this.expiresIn = expiresIn;
    }

    public String getToken() {
        return token;
    }

    public long getExpiresIn() {
        return expiresIn;
    }
}

package com.tiendatech.notificationservice.model;

import java.time.Instant;

public class ApiResponse<T> {

    private final int status;
    private final T data;
    private final String message;
    private final String timestamp;

    public ApiResponse(int status, T data, String message) {
        this.status = status;
        this.data = data;
        this.message = message;
        this.timestamp = Instant.now().toString();
    }

    public int getStatus() {
        return status;
    }

    public T getData() {
        return data;
    }

    public String getMessage() {
        return message;
    }

    public String getTimestamp() {
        return timestamp;
    }
}

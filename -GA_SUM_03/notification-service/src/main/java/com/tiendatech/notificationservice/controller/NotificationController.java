package com.tiendatech.notificationservice.controller;

import com.tiendatech.notificationservice.dto.NotificationEventRequest;
import com.tiendatech.notificationservice.model.ApiResponse;
import com.tiendatech.notificationservice.model.NotificationLog;
import com.tiendatech.notificationservice.service.NotificationService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/notifications")
public class NotificationController {

    private final NotificationService notificationService;

    public NotificationController(NotificationService notificationService) {
        this.notificationService = notificationService;
    }

    @PostMapping
    public ResponseEntity<ApiResponse<NotificationLog>> sendNotification(
            @RequestBody NotificationEventRequest request) {
        try {
            NotificationLog log = notificationService.sendNotification(request);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(new ApiResponse<>(201, log, "Notificación procesada exitosamente"));
        } catch (Exception ex) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(new ApiResponse<>(400, null, "Error al procesar notificación: " + ex.getMessage()));
        }
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<NotificationLog>>> getNotifications() {
        List<NotificationLog> history = notificationService.getNotificationHistory();
        return ResponseEntity.ok(new ApiResponse<>(200, history, "Historial de notificaciones"));
    }
}

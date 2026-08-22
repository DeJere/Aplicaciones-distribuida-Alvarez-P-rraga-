package com.tiendatech.resourceservice.client;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Component
public class NotificationClient {

    private static final Logger logger = LoggerFactory.getLogger(NotificationClient.class);

    private final RestTemplate restTemplate;

    @Value("${notification.service.url:http://notification-service:8003}")
    private String notificationServiceUrl;

    public NotificationClient() {
        this.restTemplate = new RestTemplate();
    }

    public void notify(Long resourceId, String action, String message) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            Map<String, Object> body = Map.of(
                    "resourceId", resourceId,
                    "action", action,
                    "message", message,
                    "recipientEmail", "admin@tiendatech.com"
            );

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);
            restTemplate.postForEntity(notificationServiceUrl + "/notifications", request, String.class);
            logger.info("Notificación enviada: acción={}, recurso={}", action, resourceId);
        } catch (Exception ex) {
            logger.warn("No se pudo enviar notificación al notification-service: {}", ex.getMessage());
        }
    }
}

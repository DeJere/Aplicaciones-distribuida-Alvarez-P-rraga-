package com.tiendatech.notificationservice.model;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "notification_logs")
public class NotificationLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long resourceId;
    private String action;

    @Column(length = 1000)
    private String message;

    private String recipientEmail;
    private String status;
    private String timestamp;

    public NotificationLog() {}

    public NotificationLog(Long resourceId, String action, String message, String recipientEmail) {
        this.resourceId = resourceId;
        this.action = action;
        this.message = message;
        this.recipientEmail = recipientEmail;
        this.status = "SENT";
        this.timestamp = Instant.now().toString();
    }

    public Long getId() { return id; }
    public Long getResourceId() { return resourceId; }
    public void setResourceId(Long resourceId) { this.resourceId = resourceId; }
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public String getRecipientEmail() { return recipientEmail; }
    public void setRecipientEmail(String recipientEmail) { this.recipientEmail = recipientEmail; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
}

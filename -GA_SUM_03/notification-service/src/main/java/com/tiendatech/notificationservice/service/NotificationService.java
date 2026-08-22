package com.tiendatech.notificationservice.service;

import com.tiendatech.notificationservice.dto.NotificationEventRequest;
import com.tiendatech.notificationservice.model.NotificationLog;
import com.tiendatech.notificationservice.repository.NotificationLogRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class NotificationService {

    private static final Logger logger = LoggerFactory.getLogger(NotificationService.class);

    private final NotificationLogRepository repository;

    @Value("${smtp.from:alerts@tiendatech.com}")
    private String smtpFrom;

    public NotificationService(NotificationLogRepository repository) {
        this.repository = repository;
    }

    public NotificationLog sendNotification(NotificationEventRequest request) {
        NotificationLog log = new NotificationLog(
                request.getResourceId(),
                request.getAction(),
                request.getMessage(),
                request.getRecipientEmail()
        );
        simulateSmtpEmailSend(log);
        return repository.save(log);
    }

    private void simulateSmtpEmailSend(NotificationLog log) {
        logger.info("===== SMTP EMAIL SIMULATION =====\nFrom: {}\nTo: {}\nAction: {}\nMessage: {}\nTimestamp: {}\n=================================",
                smtpFrom, log.getRecipientEmail(), log.getAction(), log.getMessage(), log.getTimestamp());
    }

    public List<NotificationLog> getNotificationHistory() {
        return repository.findAll();
    }
}

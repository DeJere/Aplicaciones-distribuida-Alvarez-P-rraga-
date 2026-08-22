package com.tiendatech.notificationservice.repository;

import com.tiendatech.notificationservice.model.NotificationLog;
import org.springframework.data.jpa.repository.JpaRepository;

public interface NotificationLogRepository extends JpaRepository<NotificationLog, Long> {}

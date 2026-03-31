package com.tongping.robot.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * 告警通知实体
 */
@Entity
@Table(name = "alarm_notifications")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AlarmNotification {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "fault_log_id", nullable = false)
    private Long faultLogId;

    @Column(length = 30, nullable = false)
    @Builder.Default
    private String channel = "系统";

    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}

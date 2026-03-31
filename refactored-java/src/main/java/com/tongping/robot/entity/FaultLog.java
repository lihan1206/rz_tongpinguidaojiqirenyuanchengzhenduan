package com.tongping.robot.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * 故障日志实体
 */
@Entity
@Table(name = "fault_logs")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FaultLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "robot_id", nullable = false)
    private Long robotId;

    @Column(name = "rule_id")
    private Long ruleId;

    @Column(name = "fault_type", length = 60, nullable = false)
    private String faultType;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String description;

    @Column(length = 20, nullable = false)
    private String level;

    @Column(length = 20, nullable = false)
    @Builder.Default
    private String status = "未处理";

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}

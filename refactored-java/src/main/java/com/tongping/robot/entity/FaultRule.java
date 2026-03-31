package com.tongping.robot.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 故障规则实体
 */
@Entity
@Table(name = "fault_rules")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FaultRule {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 100, nullable = false)
    private String name;

    @Column(name = "sensor_type", length = 50, nullable = false)
    private String sensorType;

    @Column(length = 10, nullable = false)
    private String operator;

    @Column(precision = 12, scale = 4, nullable = false)
    private BigDecimal threshold;

    @Column(length = 20, nullable = false)
    private String level;

    @Column(nullable = false)
    @Builder.Default
    private Boolean enabled = true;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}

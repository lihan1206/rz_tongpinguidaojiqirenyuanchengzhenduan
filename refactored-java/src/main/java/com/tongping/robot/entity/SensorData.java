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
 * 传感器数据实体
 */
@Entity
@Table(name = "sensor_data")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SensorData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "robot_id", nullable = false)
    private Long robotId;

    @Column(name = "sensor_type", length = 50, nullable = false)
    private String sensorType;

    @Column(precision = 12, scale = 4, nullable = false)
    private BigDecimal value;

    @CreationTimestamp
    @Column(name = "ts", nullable = false, updatable = false)
    private LocalDateTime timestamp;
}

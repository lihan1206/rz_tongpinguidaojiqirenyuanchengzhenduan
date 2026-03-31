package com.tongping.robot.repository;

import com.tongping.robot.entity.SensorData;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 传感器数据 Repository
 */
@Repository
public interface SensorDataRepository extends JpaRepository<SensorData, Long> {

    /**
     * 根据机器人ID查询传感器数据
     */
    List<SensorData> findByRobotIdOrderByIdDesc(Long robotId, Pageable pageable);

    /**
     * 根据传感器类型查询数据
     */
    List<SensorData> findBySensorTypeOrderByIdDesc(String sensorType, Pageable pageable);

    /**
     * 根据机器人ID和传感器类型查询数据
     */
    List<SensorData> findByRobotIdAndSensorTypeOrderByIdDesc(Long robotId, String sensorType, Pageable pageable);

    /**
     * 查询最新的传感器数据
     */
    @Query("SELECT s FROM SensorData s ORDER BY s.id DESC")
    List<SensorData> findLatest(Pageable pageable);

    /**
     * 查询指定机器人的最新传感器数据
     */
    @Query("SELECT s FROM SensorData s WHERE s.robotId = :robotId ORDER BY s.id DESC")
    List<SensorData> findLatestByRobotId(@Param("robotId") Long robotId, Pageable pageable);
}

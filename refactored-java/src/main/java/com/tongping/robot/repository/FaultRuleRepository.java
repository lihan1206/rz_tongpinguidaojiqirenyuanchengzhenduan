package com.tongping.robot.repository;

import com.tongping.robot.entity.FaultRule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 故障规则 Repository
 */
@Repository
public interface FaultRuleRepository extends JpaRepository<FaultRule, Long> {

    /**
     * 查询所有启用的规则
     */
    List<FaultRule> findByEnabledTrueOrderByIdDesc();

    /**
     * 根据传感器类型查询启用的规则
     */
    List<FaultRule> findBySensorTypeAndEnabledTrue(String sensorType);

    /**
     * 根据传感器类型和规则名称查询
     */
    Optional<FaultRule> findBySensorTypeAndName(String sensorType, String name);

    /**
     * 检查规则是否存在
     */
    boolean existsBySensorTypeAndName(String sensorType, String name);

    /**
     * 根据传感器类型查询启用的规则（原生SQL优化版本）
     */
    @Query("SELECT r FROM FaultRule r WHERE r.sensorType = :sensorType AND r.enabled = true")
    List<FaultRule> findActiveRulesBySensorType(@Param("sensorType") String sensorType);

    /**
     * 根据告警级别查询规则
     */
    List<FaultRule> findByLevelOrderByIdDesc(String level);
}

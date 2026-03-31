package com.tongping.robot.repository;

import com.tongping.robot.entity.FaultLog;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 故障日志 Repository
 */
@Repository
public interface FaultLogRepository extends JpaRepository<FaultLog, Long> {

    /**
     * 查询所有故障日志（按ID倒序）
     */
    List<FaultLog> findAllByOrderByIdDesc(Pageable pageable);

    /**
     * 根据机器人ID查询故障日志
     */
    List<FaultLog> findByRobotIdOrderByIdDesc(Long robotId, Pageable pageable);

    /**
     * 根据状态查询故障日志
     */
    List<FaultLog> findByStatusOrderByIdDesc(String status, Pageable pageable);

    /**
     * 根据告警级别查询故障日志
     */
    List<FaultLog> findByLevelOrderByIdDesc(String level, Pageable pageable);

    /**
     * 查询未处理的故障日志
     */
    @Query("SELECT f FROM FaultLog f WHERE f.status = '未处理' ORDER BY f.id DESC")
    List<FaultLog> findUnhandledFaults(Pageable pageable);

    /**
     * 更新故障状态
     */
    @Modifying
    @Query("UPDATE FaultLog f SET f.status = :status WHERE f.id = :id")
    int updateStatus(@Param("id") Long id, @Param("status") String status);

    /**
     * 统计指定状态的故障数量
     */
    long countByStatus(String status);

    /**
     * 统计指定机器人的故障数量
     */
    long countByRobotId(Long robotId);
}

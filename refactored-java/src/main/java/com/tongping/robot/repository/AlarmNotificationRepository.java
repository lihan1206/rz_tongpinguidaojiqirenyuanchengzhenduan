package com.tongping.robot.repository;

import com.tongping.robot.entity.AlarmNotification;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 告警通知 Repository
 */
@Repository
public interface AlarmNotificationRepository extends JpaRepository<AlarmNotification, Long> {

    /**
     * 根据故障日志ID查询通知
     */
    List<AlarmNotification> findByFaultLogIdOrderByIdDesc(Long faultLogId);

    /**
     * 根据通知渠道查询
     */
    List<AlarmNotification> findByChannelOrderByIdDesc(String channel, Pageable pageable);

    /**
     * 查询最新的通知
     */
    List<AlarmNotification> findAllByOrderByIdDesc(Pageable pageable);
}

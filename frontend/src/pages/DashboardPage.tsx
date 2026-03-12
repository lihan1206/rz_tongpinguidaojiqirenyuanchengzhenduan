import { App, Card, Col, Row, Skeleton, Statistic, Typography } from "antd";
import React, { useEffect, useState } from "react";

import { getOverview, type Overview } from "../api/reports";

export default function DashboardPage() {
  const { message } = App.useApp();
  const [data, setData] = useState<Overview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const res = await getOverview();
        setData(res);
      } catch {
        message.error("获取总览数据失败");
      } finally {
        setLoading(false);
      }
    })();
  }, [message]);

  return (
    <div>
      <Typography.Title level={4} style={{ marginTop: 0 }}>
        系统总览
      </Typography.Title>
      {loading ? (
        <Skeleton active />
      ) : (
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Card>
              <Statistic title="机器人数量" value={data?.robots ?? 0} />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Card>
              <Statistic title="故障记录" value={data?.faults ?? 0} />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Card>
              <Statistic title="维护工单" value={data?.tickets ?? 0} />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Card>
              <Statistic title="远程指令" value={data?.commands ?? 0} />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Card>
              <Statistic title="采集数据" value={data?.sensor_rows ?? 0} />
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
}

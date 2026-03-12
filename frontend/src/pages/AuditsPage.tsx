import { App, Button, Space, Table, Tag, Typography } from "antd";
import React, { useEffect, useMemo, useState } from "react";

import { listOperationLogs, type OperationLog } from "../api/audits";

export default function AuditsPage() {
  const { message } = App.useApp();
  const [rows, setRows] = useState<OperationLog[]>([]);
  const [loading, setLoading] = useState(true);

  const reload = async () => {
    try {
      setLoading(true);
      setRows(await listOperationLogs());
    } catch {
      message.error("获取审计日志失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload();
  }, []);

  const columns = useMemo(
    () => [
      { title: "时间", dataIndex: "created_at", width: 220 },
      { title: "用户ID", dataIndex: "user_id", width: 100, render: (v: any) => (v == null ? <Tag>匿名</Tag> : v) },
      { title: "方法", dataIndex: "method", width: 100 },
      { title: "路径", dataIndex: "path" },
    ],
    []
  );

  return (
    <div>
      <Space style={{ width: "100%", justifyContent: "space-between" }}>
        <Typography.Title level={4} style={{ marginTop: 0 }}>
          操作审计
        </Typography.Title>
        <Space>
          <Button onClick={reload}>刷新</Button>
        </Space>
      </Space>

      <Table rowKey="id" loading={loading} columns={columns as any} dataSource={rows} pagination={{ pageSize: 10 }} />
    </div>
  );
}

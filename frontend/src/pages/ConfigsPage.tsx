import { App, Button, Form, Input, Modal, Space, Table, Typography } from "antd";
import React, { useEffect, useMemo, useState } from "react";

import { listConfigs, upsertConfig, type SystemConfig } from "../api/configs";

export default function ConfigsPage() {
  const { message } = App.useApp();
  const [rows, setRows] = useState<SystemConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const reload = async () => {
    try {
      setLoading(true);
      setRows(await listConfigs());
    } catch {
      message.error("获取系统配置失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload();
  }, []);

  const columns = useMemo(
    () => [
      { title: "键", dataIndex: "key", width: 220 },
      { title: "值", dataIndex: "value" },
      { title: "更新时间", dataIndex: "updated_at", width: 220 },
    ],
    []
  );

  return (
    <div>
      <Space style={{ width: "100%", justifyContent: "space-between" }}>
        <Typography.Title level={4} style={{ marginTop: 0 }}>
          系统配置
        </Typography.Title>
        <Space>
          <Button onClick={reload}>刷新</Button>
          <Button
            type="primary"
            onClick={() => {
              setOpen(true);
              form.resetFields();
            }}
          >
            新增/更新
          </Button>
        </Space>
      </Space>

      <Table rowKey="id" loading={loading} columns={columns as any} dataSource={rows} pagination={{ pageSize: 10 }} />

      <Modal
        title="新增/更新配置"
        open={open}
        okText="保存"
        cancelText="取消"
        onCancel={() => setOpen(false)}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            await upsertConfig(values);
            message.success("保存成功");
            setOpen(false);
            await reload();
          } catch (e: any) {
            if (e?.errorFields) return;
            message.error(e?.response?.data?.detail ?? "保存失败");
          }
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="键" name="key" rules={[{ required: true, message: "请输入键" }]}>
            <Input placeholder="例如：采集频率" />
          </Form.Item>
          <Form.Item label="值" name="value" rules={[{ required: true, message: "请输入值" }]}>
            <Input placeholder="例如：5s" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

import { App, Button, Form, Input, Modal, Select, Space, Table, Tag, Typography } from "antd";
import React, { useEffect, useMemo, useState } from "react";

import { listRobots, type Robot } from "../api/robots";
import { createTicket, deleteTicket, listTickets, updateTicket, type Ticket } from "../api/tickets";

const statusOptions = ["待处理", "处理中", "已完成", "已关闭"];

export default function TicketsPage() {
  const { message } = App.useApp();
  const [robots, setRobots] = useState<Robot[]>([]);
  const [rows, setRows] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const reload = async () => {
    try {
      setLoading(true);
      setRows(await listTickets());
    } catch {
      message.error("获取工单失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    (async () => {
      try {
        setRobots(await listRobots());
      } catch {
        message.error("获取机器人列表失败");
      }
    })();
    reload();
  }, []);

  const columns = useMemo(
    () => [
      { title: "ID", dataIndex: "id", width: 80 },
      { title: "机器人ID", dataIndex: "robot_id", width: 110 },
      { title: "标题", dataIndex: "title", width: 220 },
      { title: "状态", dataIndex: "status", width: 110, render: (v: string) => <Tag>{v}</Tag> },
      { title: "描述", dataIndex: "description" },
      {
        title: "操作",
        width: 280,
        render: (_: any, record: Ticket) => (
          <Space>
            <Select
              size="small"
              value={record.status}
              style={{ width: 110 }}
              options={statusOptions.map((v) => ({ value: v, label: v }))}
              onChange={async (v) => {
                try {
                  await updateTicket(record.id, { status: v });
                  message.success("状态已更新");
                  await reload();
                } catch {
                  message.error("更新失败");
                }
              }}
            />
            <Button
              danger
              onClick={() => {
                Modal.confirm({
                  title: "确认删除该工单？",
                  content: `工单ID：${record.id}`,
                  okText: "删除",
                  cancelText: "取消",
                  okButtonProps: { danger: true },
                  onOk: async () => {
                    try {
                      await deleteTicket(record.id);
                      message.success("删除成功");
                      await reload();
                    } catch {
                      message.error("删除失败");
                    }
                  },
                });
              }}
            >
              删除
            </Button>
          </Space>
        ),
      },
    ],
    [message]
  );

  return (
    <div>
      <Space style={{ width: "100%", justifyContent: "space-between" }}>
        <Typography.Title level={4} style={{ marginTop: 0 }}>
          维护工单管理
        </Typography.Title>
        <Space>
          <Button onClick={reload}>刷新</Button>
          <Button
            type="primary"
            onClick={() => {
              if (!robots.length) {
                message.warning("请先创建机器人");
                return;
              }
              setOpen(true);
              form.resetFields();
              form.setFieldsValue({ robot_id: robots[0]?.id });
            }}
          >
            创建工单
          </Button>
        </Space>
      </Space>

      <Table rowKey="id" loading={loading} columns={columns as any} dataSource={rows} pagination={{ pageSize: 10 }} />

      <Modal
        title="创建维护工单"
        open={open}
        okText="创建"
        cancelText="取消"
        onCancel={() => setOpen(false)}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            await createTicket(values);
            message.success("创建成功");
            setOpen(false);
            await reload();
          } catch (e: any) {
            if (e?.errorFields) return;
            message.error(e?.response?.data?.detail ?? "创建失败");
          }
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="机器人" name="robot_id" rules={[{ required: true, message: "请选择机器人" }]}>
            <Select options={robots.map((r) => ({ value: r.id, label: `#${r.id} ${r.device_id}` }))} />
          </Form.Item>
          <Form.Item label="标题" name="title" rules={[{ required: true, message: "请输入标题" }]}>
            <Input placeholder="例如：更换电池" />
          </Form.Item>
          <Form.Item label="描述" name="description" rules={[{ required: true, message: "请输入描述" }]}>
            <Input.TextArea rows={4} placeholder="请填写故障现象、影响范围、建议操作等" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

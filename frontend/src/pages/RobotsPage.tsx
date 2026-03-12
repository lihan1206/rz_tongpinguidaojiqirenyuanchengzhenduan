import { App, Button, Form, Input, Modal, Select, Space, Table, Tag, Typography } from "antd";
import React, { useEffect, useMemo, useState } from "react";

import { createRobot, deleteRobot, listRobots, type Robot, updateRobot } from "../api/robots";

const statusOptions = ["运行中", "在线", "离线", "故障"];

export default function RobotsPage() {
  const { message } = App.useApp();
  const [rows, setRows] = useState<Robot[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Robot | null>(null);
  const [form] = Form.useForm();

  const reload = async () => {
    try {
      setLoading(true);
      const data = await listRobots();
      setRows(data);
    } catch {
      message.error("获取机器人列表失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload();
  }, []);

  const columns = useMemo(
    () => [
      { title: "ID", dataIndex: "id", width: 80 },
      { title: "设备ID", dataIndex: "device_id" },
      { title: "型号", dataIndex: "model" },
      { title: "位置", dataIndex: "location" },
      {
        title: "状态",
        dataIndex: "status",
        render: (v: string) => {
          const color = v === "运行中" ? "green" : v === "故障" ? "red" : v === "在线" ? "blue" : "default";
          return <Tag color={color}>{v}</Tag>;
        },
      },
      { title: "IP", dataIndex: "ip" },
      { title: "端口", dataIndex: "port" },
      {
        title: "操作",
        key: "actions",
        width: 200,
        render: (_: any, record: Robot) => (
          <Space>
            <Button
              onClick={() => {
                setEditing(record);
                setOpen(true);
                form.setFieldsValue(record);
              }}
            >
              编辑
            </Button>
            <Button
              danger
              onClick={() => {
                Modal.confirm({
                  title: "确认删除该机器人？",
                  content: `设备ID：${record.device_id}`,
                  okText: "删除",
                  cancelText: "取消",
                  okButtonProps: { danger: true },
                  onOk: async () => {
                    try {
                      await deleteRobot(record.id);
                      message.success("删除成功");
                      await reload();
                    } catch (e: any) {
                      message.error(e?.response?.data?.detail ?? "删除失败");
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
    [form, message]
  );

  return (
    <div>
      <Space style={{ width: "100%", justifyContent: "space-between" }}>
        <Typography.Title level={4} style={{ marginTop: 0 }}>
          机器人管理
        </Typography.Title>
        <Space>
          <Button onClick={reload}>刷新</Button>
          <Button
            type="primary"
            onClick={() => {
              setEditing(null);
              setOpen(true);
              form.resetFields();
              form.setFieldsValue({ status: "离线" });
            }}
          >
            新增机器人
          </Button>
        </Space>
      </Space>

      <Table
        rowKey="id"
        loading={loading}
        columns={columns as any}
        dataSource={rows}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={editing ? "编辑机器人" : "新增机器人"}
        open={open}
        onCancel={() => setOpen(false)}
        okText="保存"
        cancelText="取消"
        onOk={async () => {
          try {
            const values = await form.validateFields();
            if (editing) {
              await updateRobot(editing.id, values);
              message.success("更新成功");
            } else {
              await createRobot(values);
              message.success("创建成功");
            }
            setOpen(false);
            await reload();
          } catch (e: any) {
            if (e?.errorFields) return;
            message.error(e?.response?.data?.detail ?? "保存失败");
          }
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="设备ID" name="device_id" rules={[{ required: true, message: "请输入设备ID" }]}>
            <Input placeholder="例如：TC-RB-0004" disabled={Boolean(editing)} />
          </Form.Item>
          <Form.Item label="型号" name="model">
            <Input placeholder="例如：TC-Track-A1" />
          </Form.Item>
          <Form.Item label="位置" name="location">
            <Input placeholder="例如：A区-3号线" />
          </Form.Item>
          <Form.Item label="状态" name="status" rules={[{ required: true, message: "请选择状态" }]}>
            <Select options={statusOptions.map((v) => ({ value: v, label: v }))} />
          </Form.Item>
          <Form.Item label="IP" name="ip">
            <Input placeholder="例如：10.0.0.11" />
          </Form.Item>
          <Form.Item label="端口" name="port">
            <Input type="number" placeholder="例如：9001" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

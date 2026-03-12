import { App, Button, Form, Input, Modal, Select, Space, Table, Tag, Typography } from "antd";
import React, { useEffect, useMemo, useState } from "react";

import { createCommand, deleteCommand, listCommands, updateCommand, type RemoteCommand } from "../api/commands";
import { listRobots, type Robot } from "../api/robots";

const statusOptions = ["已下发", "执行中", "成功", "失败"];

export default function CommandsPage() {
  const { message } = App.useApp();
  const [robots, setRobots] = useState<Robot[]>([]);
  const [rows, setRows] = useState<RemoteCommand[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const reload = async () => {
    try {
      setLoading(true);
      setRows(await listCommands());
    } catch {
      message.error("获取指令列表失败");
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
      { title: "指令类型", dataIndex: "command_type", width: 160 },
      { title: "状态", dataIndex: "status", width: 110, render: (v: string) => <Tag>{v}</Tag> },
      { title: "结果", dataIndex: "result" },
      {
        title: "操作",
        width: 260,
        render: (_: any, record: RemoteCommand) => (
          <Space>
            <Select
              size="small"
              value={record.status}
              style={{ width: 110 }}
              options={statusOptions.map((v) => ({ value: v, label: v }))}
              onChange={async (v) => {
                try {
                  await updateCommand(record.id, { status: v, result: record.result ?? null });
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
                  title: "确认删除该指令？",
                  content: `指令ID：${record.id}`,
                  okText: "删除",
                  cancelText: "取消",
                  okButtonProps: { danger: true },
                  onOk: async () => {
                    try {
                      await deleteCommand(record.id);
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
          远程维护与操作控制
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
              form.setFieldsValue({ robot_id: robots[0]?.id, command_type: "重启", params: "{}" });
            }}
          >
            下发指令
          </Button>
        </Space>
      </Space>

      <Table rowKey="id" loading={loading} columns={columns as any} dataSource={rows} pagination={{ pageSize: 10 }} />

      <Modal
        title="下发远程指令"
        open={open}
        okText="下发"
        cancelText="取消"
        onCancel={() => setOpen(false)}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            const params = values.params ? JSON.parse(values.params) : {};
            await createCommand({ robot_id: values.robot_id, command_type: values.command_type, params });
            message.success("已下发（已写入数据库）");
            setOpen(false);
            await reload();
          } catch (e: any) {
            if (e?.errorFields) return;
            message.error("下发失败，请检查参数JSON格式");
          }
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="机器人" name="robot_id" rules={[{ required: true, message: "请选择机器人" }]}>
            <Select options={robots.map((r) => ({ value: r.id, label: `#${r.id} ${r.device_id}` }))} />
          </Form.Item>
          <Form.Item label="指令类型" name="command_type" rules={[{ required: true, message: "请输入指令类型" }]}>
            <Input placeholder="例如：重启/复位/模式切换" />
          </Form.Item>
          <Form.Item label="参数（JSON）" name="params">
            <Input.TextArea rows={4} placeholder='例如：{"mode":"巡检"}' />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

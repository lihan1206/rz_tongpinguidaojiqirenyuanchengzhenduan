import { App, Button, Card, Form, Input, InputNumber, Modal, Select, Space, Table, Tabs, Tag, Typography } from "antd";
import React, { useEffect, useMemo, useState } from "react";

import { createFaultRule, listFaultLogs, listFaultRules, type FaultLog, type FaultRule } from "../api/faults";

const operatorOptions = [">", ">=", "<", "<=", "=="];

export default function FaultsPage() {
  const { message } = App.useApp();
  const [rules, setRules] = useState<FaultRule[]>([]);
  const [logs, setLogs] = useState<FaultLog[]>([]);
  const [loadingRules, setLoadingRules] = useState(true);
  const [loadingLogs, setLoadingLogs] = useState(true);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const reload = async () => {
    try {
      setLoadingRules(true);
      setRules(await listFaultRules());
    } catch {
      message.error("获取诊断规则失败");
    } finally {
      setLoadingRules(false);
    }

    try {
      setLoadingLogs(true);
      setLogs(await listFaultLogs());
    } catch {
      message.error("获取故障记录失败");
    } finally {
      setLoadingLogs(false);
    }
  };

  useEffect(() => {
    reload();
  }, []);

  const ruleColumns = useMemo(
    () => [
      { title: "ID", dataIndex: "id", width: 80 },
      { title: "规则名称", dataIndex: "name" },
      { title: "传感器类型", dataIndex: "sensor_type", width: 130 },
      { title: "条件", render: (_: any, r: FaultRule) => `${r.operator} ${r.threshold}` },
      { title: "等级", dataIndex: "level", width: 100, render: (v: string) => <Tag color={v === "紧急" ? "red" : "orange"}>{v}</Tag> },
      { title: "启用", dataIndex: "enabled", width: 90, render: (v: boolean) => (v ? <Tag color="green">是</Tag> : <Tag>否</Tag>) },
    ],
    []
  );

  const logColumns = useMemo(
    () => [
      { title: "时间", dataIndex: "created_at", width: 220 },
      { title: "机器人ID", dataIndex: "robot_id", width: 110 },
      { title: "类型", dataIndex: "fault_type", width: 160 },
      { title: "等级", dataIndex: "level", width: 100, render: (v: string) => <Tag color={v === "紧急" ? "red" : "orange"}>{v}</Tag> },
      { title: "状态", dataIndex: "status", width: 120 },
      { title: "描述", dataIndex: "description" },
    ],
    []
  );

  return (
    <div>
      <Space style={{ width: "100%", justifyContent: "space-between" }}>
        <Typography.Title level={4} style={{ marginTop: 0 }}>
          远程诊断与故障预警
        </Typography.Title>
        <Space>
          <Button onClick={reload}>刷新</Button>
          <Button
            type="primary"
            onClick={() => {
              setOpen(true);
              form.resetFields();
              form.setFieldsValue({ sensor_type: "温度", operator: ">", threshold: 80, level: "严重", enabled: true });
            }}
          >
            新增规则
          </Button>
        </Space>
      </Space>

      <Tabs
        items={[
          {
            key: "rules",
            label: "诊断规则",
            children: (
              <Card>
                <Table rowKey="id" loading={loadingRules} columns={ruleColumns as any} dataSource={rules} pagination={{ pageSize: 10 }} />
              </Card>
            ),
          },
          {
            key: "logs",
            label: "故障记录",
            children: (
              <Card>
                <Table rowKey="id" loading={loadingLogs} columns={logColumns as any} dataSource={logs} pagination={{ pageSize: 10 }} />
              </Card>
            ),
          },
        ]}
      />

      <Modal
        title="新增诊断规则"
        open={open}
        okText="创建"
        cancelText="取消"
        onCancel={() => setOpen(false)}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            await createFaultRule(values);
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
          <Form.Item label="规则名称" name="name" rules={[{ required: true, message: "请输入规则名称" }]}>
            <Input placeholder="例如：温度过高" />
          </Form.Item>
          <Form.Item label="传感器类型" name="sensor_type" rules={[{ required: true, message: "请输入类型" }]}>
            <Input placeholder="例如：温度" />
          </Form.Item>
          <Form.Item label="运算符" name="operator" rules={[{ required: true, message: "请选择运算符" }]}>
            <Select options={operatorOptions.map((v) => ({ value: v, label: v }))} />
          </Form.Item>
          <Form.Item label="阈值" name="threshold" rules={[{ required: true, message: "请输入阈值" }]}>
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="告警等级" name="level" rules={[{ required: true, message: "请选择等级" }]}>
            <Select options={["轻微", "严重", "紧急"].map((v) => ({ value: v, label: v }))} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

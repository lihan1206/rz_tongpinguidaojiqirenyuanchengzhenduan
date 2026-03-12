import { App, Button, Card, Col, Form, InputNumber, Modal, Row, Select, Space, Table, Typography } from "antd";
import React, { useEffect, useMemo, useState } from "react";

import { listRobots, type Robot } from "../api/robots";
import { ingestSensor, listSensors, type SensorRow } from "../api/sensors";

const sensorTypes = ["温度", "电压", "电流", "速度", "位置", "电池"];

export default function SensorsPage() {
  const { message } = App.useApp();
  const [robots, setRobots] = useState<Robot[]>([]);
  const [rows, setRows] = useState<SensorRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const reload = async (robotId?: number) => {
    try {
      setLoading(true);
      const data = await listSensors(robotId);
      setRows(data);
    } catch {
      message.error("获取采集数据失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    (async () => {
      try {
        const rs = await listRobots();
        setRobots(rs);
      } catch {
        message.error("获取机器人列表失败");
      }
    })();
    reload();
  }, []);

  const columns = useMemo(
    () => [
      { title: "时间", dataIndex: "ts", width: 220 },
      { title: "机器人ID", dataIndex: "robot_id", width: 110 },
      { title: "类型", dataIndex: "sensor_type", width: 120 },
      { title: "数值", dataIndex: "value" },
    ],
    []
  );

  return (
    <div>
      <Space style={{ width: "100%", justifyContent: "space-between" }}>
        <Typography.Title level={4} style={{ marginTop: 0 }}>
          实时监控与数据采集
        </Typography.Title>
        <Space>
          <Button onClick={() => reload()}>刷新</Button>
          <Button
            type="primary"
            onClick={() => {
              if (!robots.length) {
                message.warning("请先创建机器人");
                return;
              }
              setOpen(true);
              form.resetFields();
              form.setFieldsValue({ robot_id: robots[0]?.id, sensor_type: "温度", value: 25 });
            }}
          >
            上报一条数据（写入数据库）
          </Button>
        </Space>
      </Space>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={24}>
          <Card>
            <Table rowKey="id" loading={loading} columns={columns as any} dataSource={rows} pagination={{ pageSize: 10 }} />
          </Card>
        </Col>
      </Row>

      <Modal
        title="上报传感器数据"
        open={open}
        okText="提交"
        cancelText="取消"
        onCancel={() => setOpen(false)}
        onOk={async () => {
          try {
            const values = await form.validateFields();
            await ingestSensor(values);
            message.success("上报成功（已写入数据库）");
            setOpen(false);
            await reload();
          } catch (e: any) {
            if (e?.errorFields) return;
            message.error(e?.response?.data?.detail ?? "上报失败");
          }
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="机器人" name="robot_id" rules={[{ required: true, message: "请选择机器人" }]}>
            <Select
              options={robots.map((r) => ({ value: r.id, label: `#${r.id} ${r.device_id}（${r.status}）` }))}
            />
          </Form.Item>
          <Form.Item label="传感器类型" name="sensor_type" rules={[{ required: true, message: "请选择类型" }]}>
            <Select options={sensorTypes.map((v) => ({ value: v, label: v }))} />
          </Form.Item>
          <Form.Item label="数值" name="value" rules={[{ required: true, message: "请输入数值" }]}>
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

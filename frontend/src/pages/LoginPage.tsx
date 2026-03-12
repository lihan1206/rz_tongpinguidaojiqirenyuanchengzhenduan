import { Alert, App, Button, Card, Form, Input, Typography } from "antd";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login } from "../api/auth";

export default function LoginPage() {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 16,
        background: "linear-gradient(135deg, #f6f9ff, #ffffff)",
      }}
    >
      <Card style={{ width: 420, borderRadius: 12 }}>
        <Typography.Title level={3} style={{ marginTop: 0 }}>
          登录
        </Typography.Title>
        <Typography.Paragraph type="secondary" style={{ marginTop: -8 }}>
          瞳骋轨道机器人远程诊断与维护管理系统
        </Typography.Paragraph>
        {error ? <Alert style={{ marginBottom: 12 }} type="error" message={error} /> : null}
        <Form
          layout="vertical"
          initialValues={{ account: "admin", password: "123456" }}
          onFinish={async (values) => {
            setError(null);
            setLoading(true);
            try {
              const res = await login(values.account, values.password);
              localStorage.setItem("access_token", res.access_token);
              message.success("登录成功");
              navigate("/", { replace: true });
            } catch (e: any) {
              setError(e?.response?.data?.detail ?? "登录失败，请检查账号密码");
            } finally {
              setLoading(false);
            }
          }}
        >
          <Form.Item label="账号/手机号/工号" name="account" rules={[{ required: true, message: "请输入账号" }]}>
            <Input placeholder="请输入账号/手机号/工号" autoComplete="username" />
          </Form.Item>
          <Form.Item label="密码" name="password" rules={[{ required: true, message: "请输入密码" }]}>
            <Input.Password placeholder="请输入密码" autoComplete="current-password" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            登录
          </Button>
        </Form>
      </Card>
    </div>
  );
}

import { App, Button, Dropdown, Layout, Menu, Space, Typography } from "antd";
import {
  AlertOutlined,
  AppstoreOutlined,
  AuditOutlined,
  ControlOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  LogoutOutlined,
  RobotOutlined,
  SettingOutlined,
  TeamOutlined,
  ToolOutlined,
} from "@ant-design/icons";
import React, { useEffect, useMemo, useState } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";

import { me, type MeOut } from "../api/auth";

const { Header, Sider, Content } = Layout;

export default function MainLayout() {
  const { message } = App.useApp();
  const location = useLocation();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [currentUser, setCurrentUser] = useState<MeOut | null>(null);

  const isAdmin = Boolean(currentUser?.roles?.includes("系统管理员"));

  const selectedKey = useMemo(() => {
    const path = location.pathname.replace(/^\//, "");
    if (!path) return "dashboard";
    const first = path.split("/")[0];
    if (first === "robots") return "robots";
    if (first === "sensors") return "sensors";
    if (first === "faults") return "faults";
    if (first === "commands") return "commands";
    if (first === "tickets") return "tickets";
    if (first === "configs") return "configs";
    if (first === "audits") return "audits";
    if (first === "admin") return "admin";
    return "dashboard";
  }, [location.pathname]);

  useEffect(() => {
    (async () => {
      try {
        const data = await me();
        setCurrentUser(data);
      } catch {
        localStorage.removeItem("access_token");
        message.error("登录已失效，请重新登录");
        navigate("/login", { replace: true });
      }
    })();
  }, [message, navigate]);

  const userMenu = (
    <Menu
      items={[
        {
          key: "logout",
          icon: <LogoutOutlined />,
          label: "退出登录",
          onClick: () => {
            localStorage.removeItem("access_token");
            navigate("/login", { replace: true });
          },
        },
      ]}
    />
  );

  const menuItems = [
    {
      key: "dashboard",
      icon: <DashboardOutlined />,
      label: <Link to="/">总览</Link>,
    },
    {
      key: "robots",
      icon: <RobotOutlined />,
      label: <Link to="/robots">机器人管理</Link>,
    },
    {
      key: "sensors",
      icon: <DatabaseOutlined />,
      label: <Link to="/sensors">数据采集</Link>,
    },
    {
      key: "faults",
      icon: <AlertOutlined />,
      label: <Link to="/faults">故障与告警</Link>,
    },
    {
      key: "commands",
      icon: <ControlOutlined />,
      label: <Link to="/commands">远程指令</Link>,
    },
    {
      key: "tickets",
      icon: <ToolOutlined />,
      label: <Link to="/tickets">维护工单</Link>,
    },
    ...(isAdmin
      ? [
          {
            key: "admin",
            icon: <TeamOutlined />,
            label: <Link to="/admin">用户与权限</Link>,
          },
          {
            key: "configs",
            icon: <SettingOutlined />,
            label: <Link to="/configs">系统配置</Link>,
          },
          {
            key: "audits",
            icon: <AuditOutlined />,
            label: <Link to="/audits">审计日志</Link>,
          },
        ]
      : []),
    {
      key: "apps",
      icon: <AppstoreOutlined />,
      label: "",
      disabled: true,
    },
  ];

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} theme="light">
        <div style={{ padding: 16, display: "flex", alignItems: "center", gap: 8 }}>
          <RobotOutlined />
          {!collapsed && <Typography.Text strong>瞳骋轨道机器人远程诊断与维护管理系统</Typography.Text>}
        </div>
        <Menu mode="inline" selectedKeys={[selectedKey]} items={menuItems as any} />
      </Sider>
      <Layout>
        <Header
          style={{
            background: "#fff",
            borderBottom: "1px solid #f0f0f0",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            paddingInline: 16,
          }}
        >
          <Space>
            <Typography.Text>{currentUser?.full_name ?? currentUser?.username ?? ""}</Typography.Text>
            {currentUser?.roles?.length ? (
              <Typography.Text type="secondary">（{currentUser.roles.join("、")}）</Typography.Text>
            ) : null}
          </Space>
          <Dropdown overlay={userMenu} trigger={["click"]}>
            <Button>账号</Button>
          </Dropdown>
        </Header>
        <Content style={{ padding: 16 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}

import { App, Button, Form, Input, Modal, Select, Space, Table, Tabs, Tag, Typography } from "antd";
import React, { useEffect, useMemo, useState } from "react";

import {
  createPermission,
  createRole,
  listPermissions,
  listRoles,
  listUserLogs,
  listUsers,
  setUserRoles,
  type AdminUser,
  type Permission,
  type Role,
  type UserLog,
} from "../api/admin";

export default function AdminPage() {
  const { message } = App.useApp();

  const [roles, setRoles] = useState<Role[]>([]);
  const [perms, setPerms] = useState<Permission[]>([]);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [userLogs, setUserLogs] = useState<UserLog[]>([]);

  const [loading, setLoading] = useState(false);

  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [permModalOpen, setPermModalOpen] = useState(false);
  const [userRoleModalOpen, setUserRoleModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null);

  const [roleForm] = Form.useForm();
  const [permForm] = Form.useForm();
  const [userRoleForm] = Form.useForm();

  const reloadAll = async () => {
    try {
      setLoading(true);
      const [r, p, u, l] = await Promise.all([listRoles(), listPermissions(), listUsers(), listUserLogs()]);
      setRoles(r);
      setPerms(p);
      setUsers(u);
      setUserLogs(l);
    } catch {
      message.error("加载用户与权限数据失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reloadAll();
  }, []);

  const roleColumns = useMemo(
    () => [
      { title: "ID", dataIndex: "id", width: 80 },
      { title: "编码", dataIndex: "code", width: 140 },
      { title: "名称", dataIndex: "name" },
    ],
    []
  );

  const permColumns = useMemo(
    () => [
      { title: "ID", dataIndex: "id", width: 80 },
      { title: "编码", dataIndex: "code", width: 160 },
      { title: "名称", dataIndex: "name" },
    ],
    []
  );

  const userColumns = useMemo(
    () => [
      { title: "ID", dataIndex: "id", width: 80 },
      { title: "账号", dataIndex: "username", width: 140 },
      { title: "姓名", dataIndex: "full_name", width: 140 },
      { title: "手机号", dataIndex: "phone", width: 140 },
      { title: "工号", dataIndex: "employee_no", width: 140 },
      {
        title: "角色",
        dataIndex: "roles",
        render: (v: string[]) => (v?.length ? v.map((c) => <Tag key={c}>{c}</Tag>) : <Tag>未分配</Tag>),
      },
      {
        title: "操作",
        width: 140,
        render: (_: any, record: AdminUser) => (
          <Button
            onClick={() => {
              setEditingUser(record);
              setUserRoleModalOpen(true);
              userRoleForm.setFieldsValue({ role_codes: record.roles });
            }}
          >
            分配角色
          </Button>
        ),
      },
    ],
    [userRoleForm]
  );

  const logColumns = useMemo(
    () => [
      { title: "时间", dataIndex: "created_at", width: 220 },
      { title: "用户ID", dataIndex: "user_id", width: 110, render: (v: any) => (v == null ? <Tag>匿名</Tag> : v) },
      { title: "动作", dataIndex: "action", width: 120 },
      { title: "IP", dataIndex: "ip", width: 160 },
      { title: "User-Agent", dataIndex: "user_agent" },
    ],
    []
  );

  return (
    <div>
      <Space style={{ width: "100%", justifyContent: "space-between" }}>
        <Typography.Title level={4} style={{ marginTop: 0 }}>
          用户与权限管理
        </Typography.Title>
        <Space>
          <Button onClick={reloadAll} loading={loading}>
            刷新
          </Button>
          <Button
            type="primary"
            onClick={() => {
              setRoleModalOpen(true);
              roleForm.resetFields();
            }}
          >
            新增角色
          </Button>
          <Button
            onClick={() => {
              setPermModalOpen(true);
              permForm.resetFields();
            }}
          >
            新增权限
          </Button>
        </Space>
      </Space>

      <Tabs
        items={[
          {
            key: "users",
            label: "用户",
            children: (
              <Table rowKey="id" loading={loading} columns={userColumns as any} dataSource={users} pagination={{ pageSize: 10 }} />
            ),
          },
          {
            key: "roles",
            label: "角色",
            children: (
              <Table rowKey="id" loading={loading} columns={roleColumns as any} dataSource={roles} pagination={{ pageSize: 10 }} />
            ),
          },
          {
            key: "perms",
            label: "权限",
            children: (
              <Table rowKey="id" loading={loading} columns={permColumns as any} dataSource={perms} pagination={{ pageSize: 10 }} />
            ),
          },
          {
            key: "userLogs",
            label: "登录日志",
            children: (
              <Table rowKey="id" loading={loading} columns={logColumns as any} dataSource={userLogs} pagination={{ pageSize: 10 }} />
            ),
          },
        ]}
      />

      <Modal
        title="新增角色"
        open={roleModalOpen}
        okText="创建"
        cancelText="取消"
        onCancel={() => setRoleModalOpen(false)}
        onOk={async () => {
          try {
            const values = await roleForm.validateFields();
            await createRole(values);
            message.success("创建成功");
            setRoleModalOpen(false);
            await reloadAll();
          } catch (e: any) {
            if (e?.errorFields) return;
            message.error(e?.response?.data?.detail ?? "创建失败");
          }
        }}
      >
        <Form form={roleForm} layout="vertical">
          <Form.Item label="编码" name="code" rules={[{ required: true, message: "请输入编码" }]}>
            <Input placeholder="例如：viewer" />
          </Form.Item>
          <Form.Item label="名称" name="name" rules={[{ required: true, message: "请输入名称" }]}>
            <Input placeholder="例如：只读用户" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="新增权限"
        open={permModalOpen}
        okText="创建"
        cancelText="取消"
        onCancel={() => setPermModalOpen(false)}
        onOk={async () => {
          try {
            const values = await permForm.validateFields();
            await createPermission(values);
            message.success("创建成功");
            setPermModalOpen(false);
            await reloadAll();
          } catch (e: any) {
            if (e?.errorFields) return;
            message.error(e?.response?.data?.detail ?? "创建失败");
          }
        }}
      >
        <Form form={permForm} layout="vertical">
          <Form.Item label="编码" name="code" rules={[{ required: true, message: "请输入编码" }]}>
            <Input placeholder="例如：export" />
          </Form.Item>
          <Form.Item label="名称" name="name" rules={[{ required: true, message: "请输入名称" }]}>
            <Input placeholder="例如：数据导出" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={editingUser ? `分配角色：${editingUser.username}` : "分配角色"}
        open={userRoleModalOpen}
        okText="保存"
        cancelText="取消"
        onCancel={() => setUserRoleModalOpen(false)}
        onOk={async () => {
          try {
            const values = await userRoleForm.validateFields();
            if (!editingUser) return;
            await setUserRoles(editingUser.id, values.role_codes ?? []);
            message.success("已更新");
            setUserRoleModalOpen(false);
            await reloadAll();
          } catch (e: any) {
            if (e?.errorFields) return;
            message.error(e?.response?.data?.detail ?? "更新失败");
          }
        }}
      >
        <Form form={userRoleForm} layout="vertical">
          <Form.Item label="角色" name="role_codes">
            <Select
              mode="multiple"
              placeholder="请选择角色"
              options={roles.map((r) => ({ value: r.code, label: `${r.name}（${r.code}）` }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

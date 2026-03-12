import React from "react";
import { Button, Result } from "antd";

type Props = { children: React.ReactNode };
type State = { hasError: boolean };

export default class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch() {
    // 生产环境避免输出敏感信息，这里不做 console.log
  }

  render() {
    if (this.state.hasError) {
      return (
        <Result
          status="error"
          title="页面发生错误"
          subTitle="请刷新页面重试。如果问题持续出现，请联系管理员。"
          extra={[
            <Button key="reload" type="primary" onClick={() => window.location.reload()}>
              刷新页面
            </Button>,
          ]}
        />
      );
    }

    return this.props.children;
  }
}

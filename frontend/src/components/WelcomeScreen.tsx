import { InputForm } from "./InputForm";
import { Button } from "./ui/button";
import { useState } from "react";

interface WelcomeScreenProps {
  handleSubmit: (
    submittedInputValue: string,
    effort: string,
    model: string
  ) => void;
  onCancel: () => void;
  isLoading: boolean;
}

const BACKEND_API_URL = import.meta.env.VITE_BACKEND_API_URL;

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  handleSubmit,
  onCancel,
  isLoading,
}) => {
  const [healthStatus, setHealthStatus] = useState<string>("");
  const [isTestingHealth, setIsTestingHealth] = useState(false);

  /**
   * 测试健康检查接口
   */
  const testHealthCheck = async () => {
    setIsTestingHealth(true);
    setHealthStatus("");

    try {
      const response = await fetch(`${BACKEND_API_URL}/health`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setHealthStatus(`✅ 后端服务正常 - ${JSON.stringify(data)}`);
      } else {
        setHealthStatus(`❌ 后端服务异常 - 状态码: ${response.status}`);
      }
    } catch (error) {
      setHealthStatus(
        `❌ 连接失败 - ${error instanceof Error ? error.message : "未知错误"}`
      );
    } finally {
      setIsTestingHealth(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center text-center px-4 flex-1 w-full max-w-3xl mx-auto gap-4">
      <div>
        <h1 className="text-5xl md:text-6xl font-semibold text-neutral-100 mb-3">
          xDAN 智能分析
        </h1>
        <p className="text-xl md:text-2xl text-neutral-400">
          我是您的专业金融数据分析助手，今天想查询什么？
        </p>
      </div>

      <div className="w-full mt-2">
        <InputForm
          onSubmit={handleSubmit}
          isLoading={isLoading}
          onCancel={onCancel}
          hasHistory={false}
        />
      </div>
      <p className="text-xs text-neutral-500">
        基于 xDAN 智能工具选择器 | 支持股票、港股、财务等30+专业工具
      </p>

      {/* 健康检查测试区域 */}
      <div className="w-full my-2 p-4 bg-neutral-900 rounded-lg">
        <div className="flex flex-col items-center gap-3">
          <Button
            onClick={testHealthCheck}
            disabled={isTestingHealth}
            variant="outline"
            size="sm"
            className="w-48 text-color-black bg-color-primary"
          >
            {isTestingHealth ? "测试中..." : "🔍 测试后端连接"}
          </Button>

          {healthStatus && (
            <div className="text-sm text-neutral-300 bg-neutral-800 px-3 py-1 rounded-md w-full max-w-md break-words">
              {healthStatus}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

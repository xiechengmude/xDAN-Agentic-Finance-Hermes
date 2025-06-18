import { useState, useEffect, useRef, useCallback } from "react";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";

// 消息类型定义
interface Message {
  id: string;
  type: "human" | "ai";
  content: string;
}

// 流式处理的自定义Hook
function useCustomStream() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * 提交新消息并开始流式处理
   */
  const submit = useCallback(
    async (data: {
      messages: Message[];
      initial_search_query_count?: number;
      max_research_loops?: number;
      reasoning_model?: string;
    }) => {
      if (isLoading) return;

      setIsLoading(true);
      abortControllerRef.current = new AbortController();

      try {
        // 1. 创建新线程
        const threadResponse = await fetch(
          "http://localhost:8000/assistants/xdan-agent/threads",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            signal: abortControllerRef.current.signal,
          }
        );

        if (!threadResponse.ok) {
          throw new Error(`创建线程失败: ${threadResponse.status}`);
        }

        const { thread_id } = await threadResponse.json();

        // 2. 发送流式请求
        const streamResponse = await fetch(
          `http://localhost:8000/assistants/xdan-agent/threads/${thread_id}/runs/stream`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              messages: data.messages.map((msg) => ({
                type: msg.type,
                content: msg.content,
                id: msg.id,
              })),
              initial_search_query_count: data.initial_search_query_count || 3,
              max_research_loops: data.max_research_loops || 5,
              reasoning_model: data.reasoning_model,
            }),
            signal: abortControllerRef.current.signal,
          }
        );

        if (!streamResponse.ok) {
          throw new Error(`流式请求失败: ${streamResponse.status}`);
        }

        // 3. 处理SSE流
        const reader = streamResponse.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let aiMessage = "";
        let currentMessageId = Date.now().toString();

        // 立即添加用户消息
        setMessages((prev) => [...prev, ...data.messages]);

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                try {
                  const eventData = JSON.parse(line.slice(6));

                  if (eventData.type === "update" && eventData.data) {
                    // 处理不同类型的事件
                    if (eventData.data.finalize_answer) {
                      aiMessage =
                        eventData.data.finalize_answer.response || "分析完成";
                    } else if (eventData.data.web_research) {
                      // 可以在这里处理中间状态更新
                    }
                  }
                } catch (e) {
                  console.warn("Failed to parse SSE data:", line);
                }
              }
            }
          }

          // 添加AI响应消息
          if (aiMessage) {
            setMessages((prev) => [
              ...prev,
              {
                id: currentMessageId,
                type: "ai" as const,
                content: aiMessage,
              },
            ]);
          }
        }
      } catch (error: any) {
        if (error.name !== "AbortError") {
          console.error("Stream error:", error);
          // 添加错误消息
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now().toString(),
              type: "ai" as const,
              content: `抱歉，处理您的请求时出现错误：${error.message}`,
            },
          ]);
        }
      } finally {
        setIsLoading(false);
        abortControllerRef.current = null;
      }
    },
    [isLoading]
  );

  /**
   * 停止当前的流式处理
   */
  const stop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  }, []);

  return {
    messages,
    isLoading,
    submit,
    stop,
  };
}

export default function App() {
  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<
    ProcessedEvent[]
  >([]);
  const [historicalActivities, setHistoricalActivities] = useState<
    Record<string, ProcessedEvent[]>
  >({});
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // 使用自定义的流式处理Hook
  const thread = useCustomStream();

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [thread.messages]);

  const handleSubmit = useCallback(
    (submittedInputValue: string, effort: string, model: string) => {
      if (!submittedInputValue.trim()) return;
      setProcessedEventsTimeline([]);

      // 转换effort参数
      let initial_search_query_count = 0;
      let max_research_loops = 0;
      switch (effort) {
        case "low":
          initial_search_query_count = 1;
          max_research_loops = 1;
          break;
        case "medium":
          initial_search_query_count = 3;
          max_research_loops = 3;
          break;
        case "high":
          initial_search_query_count = 5;
          max_research_loops = 10;
          break;
      }

      const newMessage: Message = {
        type: "human",
        content: submittedInputValue,
        id: Date.now().toString(),
      };

      thread.submit({
        messages: [newMessage],
        initial_search_query_count,
        max_research_loops,
        reasoning_model: model,
      });
    },
    [thread]
  );

  const handleCancel = useCallback(() => {
    thread.stop();
    window.location.reload();
  }, [thread]);

  return (
    <div className="flex h-screen bg-neutral-800 text-neutral-100 font-sans antialiased">
      <main className="flex-1 flex flex-col overflow-hidden max-w-4xl mx-auto w-full">
        <div
          className={`flex-1 overflow-y-auto ${
            thread.messages.length === 0 ? "flex" : ""
          }`}
        >
          {thread.messages.length === 0 ? (
            <WelcomeScreen
              handleSubmit={handleSubmit}
              isLoading={thread.isLoading}
              onCancel={handleCancel}
            />
          ) : (
            <ChatMessagesView
              messages={thread.messages}
              isLoading={thread.isLoading}
              scrollAreaRef={scrollAreaRef}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              liveActivityEvents={processedEventsTimeline}
              historicalActivities={historicalActivities}
            />
          )}
        </div>
      </main>
    </div>
  );
}

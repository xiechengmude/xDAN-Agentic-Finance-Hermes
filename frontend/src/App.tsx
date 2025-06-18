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

const BACKEND_API_URL = import.meta.env.VITE_BACKEND_API_URL;

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
          `${BACKEND_API_URL}/assistants/xdan-agent/threads`,
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
          `${BACKEND_API_URL}/assistants/xdan-agent/threads/${thread_id}/runs/stream`,
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
        let hasReceivedData = false;
        const currentMessageId = Date.now().toString();

        // 立即添加用户消息
        setMessages((prev) => [...prev, ...data.messages]);

        // 添加占位的AI消息
        const addInitialAIMessage = () => {
          setMessages((prev) => [
            ...prev,
            {
              id: currentMessageId,
              type: "ai" as const,
              content: "正在分析您的问题...",
            },
          ]);
        };

        addInitialAIMessage();

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
                  hasReceivedData = true;

                  console.log("📨 收到SSE事件:", eventData);

                  // 处理 messages/partial 事件（实际的流式输出）
                  if (
                    eventData.event === "messages/partial" &&
                    eventData.data?.ai_response
                  ) {
                    const aiResponse = eventData.data.ai_response;

                    // 获取当前的增量内容
                    const partialContent = aiResponse.partial_content || "";
                    const fullContentSoFar =
                      aiResponse.full_content_so_far || "";

                    // 累积内容到aiMessage
                    if (partialContent) {
                      // 使用完整内容作为当前消息内容
                      aiMessage = fullContentSoFar;
                    }
                  }
                  // 处理其他事件类型（保持原有逻辑）
                  else if (eventData.type === "update" && eventData.data) {
                    // 后端格式：{"type": "update", "data": {"finalize_answer": {...}}}
                    const data = eventData.data;

                    if (data.generate_query) {
                      const queries = data.generate_query.query_list || [];
                      aiMessage = `正在分析: ${queries.join(", ")}`;
                    } else if (data.web_research) {
                      const sources = data.web_research.sources_gathered || [];
                      if (sources.length > 0) {
                        aiMessage = `已收集数据源: ${sources
                          .map((s: { label: string }) => s.label)
                          .join(", ")}`;
                      }
                    } else if (data.reflection) {
                      const sufficient = data.reflection.is_sufficient;
                      aiMessage = sufficient
                        ? "数据分析中..."
                        : "需要更多数据，继续搜索...";
                    } else if (data.finalize_answer) {
                      // 处理最终回答，支持 partial_content、response 等字段
                      const finalAnswer = data.finalize_answer;
                      const content =
                        finalAnswer.partial_content ||
                        finalAnswer.response ||
                        finalAnswer.result ||
                        "分析完成";
                      aiMessage = content;
                    }
                  } else if (eventData.generate_query) {
                    // 直接事件格式：{"generate_query": {...}}
                    const queries = eventData.generate_query.query_list || [];
                    aiMessage = `正在分析: ${queries.join(", ")}`;
                  } else if (eventData.web_research) {
                    const sources =
                      eventData.web_research.sources_gathered || [];
                    if (sources.length > 0) {
                      aiMessage = `已收集数据源: ${sources
                        .map((s: { label: string }) => s.label)
                        .join(", ")}`;
                    }
                  } else if (eventData.reflection) {
                    const sufficient = eventData.reflection.is_sufficient;
                    aiMessage = sufficient
                      ? "数据分析中..."
                      : "需要更多数据，继续搜索...";
                  } else if (eventData.finalize_answer) {
                    // 处理直接的 finalize_answer 事件
                    const finalAnswer = eventData.finalize_answer;
                    const content =
                      finalAnswer.partial_content ||
                      finalAnswer.response ||
                      finalAnswer.result ||
                      "分析完成";
                    aiMessage = content;
                  } else if (eventData.type === "start") {
                    aiMessage = "开始处理您的请求...";
                  } else if (eventData.type === "end") {
                    if (!aiMessage) {
                      aiMessage = "处理完成";
                    }
                  } else if (eventData.type === "error") {
                    aiMessage = `处理出错: ${eventData.error}`;
                  }

                  // 实时更新AI消息
                  if (aiMessage) {
                    setMessages((prev) => {
                      const newMessages = [...prev];
                      const lastMessage = newMessages[newMessages.length - 1];
                      if (lastMessage && lastMessage.id === currentMessageId) {
                        lastMessage.content = aiMessage;
                      }
                      return newMessages;
                    });
                  }
                } catch (error) {
                  console.warn("Failed to parse SSE data:", line, error);
                }
              }
            }
          }

          // 处理完成后，如果没有收到任何数据，显示错误信息
          if (!hasReceivedData) {
            setMessages((prev) => {
              const newMessages = [...prev];
              const lastMessage = newMessages[newMessages.length - 1];
              if (lastMessage && lastMessage.id === currentMessageId) {
                lastMessage.content = "未收到服务器响应，请稍后重试";
              }
              return newMessages;
            });
          }
        }
      } catch (error: unknown) {
        if (error instanceof Error && error.name !== "AbortError") {
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
  const [historicalActivities] = useState<Record<string, ProcessedEvent[]>>({});
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

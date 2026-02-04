"use client";

import { useTasks } from '@/features/tasks/hooks';
import { getSessionToken } from '@/lib/auth/client';
import { env } from '@/utils/env';
import { ChatKit, useChatKit, UseChatKitOptions } from '@openai/chatkit-react';
import { useTheme } from 'next-themes';
import { useEffect, useMemo, useState } from 'react';

export function ChatInterface() {

  const { refetch: refetchTasks } = useTasks();
  const [isExpanded, setIsExpanded] = useState(false);
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  // Memoize the configuration to prevent recreating the control on every render
  const chatKitConfig: UseChatKitOptions = useMemo(() => ({
    api: {
      url: env.NEXT_PUBLIC_API_BASE_URL + "/chat",
      domainKey: env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY,
      fetch: async (url, options) => {
        const token = await getSessionToken();
        const customOptions = {
          ...options,
          headers: {
            ...options?.headers,
            'Authorization': `Bearer ${token}`,
            'X-Context-Source': 'chat-widget',
          }
        };
        return fetch(url, customOptions);
      }
    },
    theme: {
      color: {
        accent: {
          primary: "hsl(35, 85%, 55%)", // amber accent
          level: 2
        },
        grayscale: {
          hue: 25, // warm brown hue
          tint: isDark ? 1 : 3, // darker tint for dark mode
          shade: isDark ? 3 : 1 // more shade for dark mode
        },
        surface: isDark ? {
          background: "hsl(26, 25%, 11%)", // dark espresso background
          foreground: "hsl(25, 15%, 20%)" // espresso text
        } : {
          background: "hsl(40, 27%, 98%)", // warm cream background
          foreground: "hsl(30, 20%, 85%)" // cream text
        },
      },
      density: "normal",
      typography: {
        fontFamily: "'DM Sans', sans-serif",
      },
      radius: "round",
    },
    history: { enabled: true },

    composer: {
      attachments: { enabled: false },
      placeholder: "Ask me anything about your tasks...",
    },
    startScreen: {
      greeting: "Hello! I'm your AI task assistant. You can tell me things like:",
      prompts: [
        { label: "Add a task to review the quarterly report by Friday", prompt: "Add a task to review the quarterly report by Friday" },
        { label: "Show high priority tasks", prompt: "Show me my high priority tasks" },
        { label: "What's on my schedule?", prompt: "What's on my schedule for today?" },
      ]
    },
    onError: ({ error }) => {
      console.error(error);
    },
    onResponseEnd: async () => {
      await refetchTasks()
    }

  }), [isExpanded, isDark]); // Only recreate when these values change

  const { control } = useChatKit(chatKitConfig);

  // Update header dynamically after initialization
  useEffect(() => {
    if (control) {
      control.options.header = {
        title: { text: isExpanded ? "AI Task Assistant - Expanded" : "AI Task Assistant" },
        leftAction: {
          icon: isExpanded ? 'collapse-large' : 'expand-large',
          onClick: toggleExpand,
        },
        rightAction: isExpanded ? {
          icon: 'close',
          onClick: toggleExpand,
        } : undefined,
      };
    }
  }, [isExpanded, control]);


  if (isExpanded) {
    return (
      <div className="fixed inset-0 z-50 bg-background flex flex-col">
        <div className="flex-1 overflow-hidden">
          <ChatKit control={control} className="h-full w-full" />
        </div>
      </div>
    );
  }

  return (
    <ChatKit control={control} className="h-full w-full bg-transparent!" />
  );
}

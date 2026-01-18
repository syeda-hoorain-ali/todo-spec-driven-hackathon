"use client";

import { useState } from "react";
import { TaskList } from "@/components/tasks/task-list";
import { TaskFilters } from "@/components/tasks/task-filters";
import { CreateTaskDialog } from "@/components/tasks/create-task-dialog";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  PlusIcon,
  CheckCircle2Icon,
  ClockIcon,
  AlertTriangleIcon,
  ListTodoIcon,
  BotMessageSquareIcon,
  XIcon
} from "lucide-react";
import { ChatInterface } from "@/components/chat/chat-interface";
import { ProtectedRoute } from "@/components/protected/protected-route";
import { useUser } from "@/features/auth/hooks";
import { useTasks } from "@/features/tasks/hooks";
import Loading from "@/app/loading";
import { cn } from "@/utils/shadcn";

export default function Dashboard() {

  const { stats } = useTasks();
  const { user, isLoading: userLoading } = useUser();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);

  if (userLoading) return <Loading />;
  if (!user) return null;

  const handleAddTask = () => {
    setDialogOpen(true);
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen gradient-warm flex flex-col">
        <main className="container mx-auto px-4 py-6 flex-1">
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Left Column - Stats & Chat */}
            <div className="lg:col-span-1 space-y-6">
              {/* Stats Cards */}
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: "Total", value: stats.total, icon: ListTodoIcon, color: "text-foreground" },
                  { label: "Active", value: stats.active, icon: ClockIcon, color: "text-accent" },
                  { label: "Completed", value: stats.completed, icon: CheckCircle2Icon, color: "text-priority-low" },
                  { label: "Overdue", value: stats.overdue, icon: AlertTriangleIcon, color: "text-priority-high" },
                ].map((stat) => (
                  <Card key={stat.label} className="p-4">
                    <div className="flex items-center gap-2">
                      <stat.icon className={`w-4 h-4 ${stat.color}`} />
                      <span className="text-xs text-muted-foreground font-body">{stat.label}</span>
                    </div>
                    <p className={`text-2xl font-bold font-display mt-1 ${stat.color}`}>{stat.value}</p>
                  </Card>
                ))}
              </div>

              {/* AI Chat - Desktop */}
              <Card className="hidden lg:flex flex-col h-125 overflow-hidden pt-0">
                <ChatInterface />
              </Card>
            </div>

            {/* Right Column - Tasks */}
            <div className="lg:col-span-2 space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold font-display text-foreground">My Tasks</h1>
                <div className="flex items-center gap-2">
                  <Button
                    onClick={() => setChatOpen(true)}
                    variant="outline"
                    className="lg:hidden"
                  >
                    <BotMessageSquareIcon className="w-4 h-4 mr-2" />
                    AI Chat
                  </Button>
                  <Button onClick={handleAddTask} variant="accent">
                    <PlusIcon className="w-4 h-4 mr-2" />
                    Add Task
                  </Button>
                </div>
              </div>

              {/* Filters */}
              <Card className="p-4">
                <TaskFilters />
              </Card>

              {/* Task List */}
              <TaskList />
            </div>
          </div>
        </main>

        {/* Mobile Chat Overlay */}
        <div
          className={cn(
            "fixed inset-0 z-50 lg:hidden transition-transform duration-300",
            chatOpen ? "translate-y-0" : "translate-y-full"
          )}
        >
          <div className="absolute inset-0 bg-background flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="font-semibold">AI Task Assistant</h2>
              <Button variant="ghost" size="icon" onClick={() => setChatOpen(false)}>
                <XIcon className="w-5 h-5" />
              </Button>
            </div>
            <div className="flex-1 overflow-hidden">
              <ChatInterface />
            </div>
          </div>
        </div>

        {/* Create Task Dialog */}
        <CreateTaskDialog
          open={dialogOpen}
          onOpenChange={setDialogOpen}
        />
      </div>
    </ProtectedRoute>
  );
}

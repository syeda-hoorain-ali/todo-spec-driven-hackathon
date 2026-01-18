import { TaskItem } from "./task-item";
import { CheckCircle2, ListTodo } from "lucide-react";
import { useTasks } from "@/features/tasks/hooks";

export function TaskList() {
  const { tasks, isLoading: loading } = useTasks();

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="h-24 rounded-xl bg-muted/50 animate-pulse"
            style={{ animationDelay: `${i * 100}ms` }}
          />
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
        <div className="w-16 h-16 rounded-2xl bg-muted/50 flex items-center justify-center mb-4">
          <ListTodo className="w-8 h-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold font-display text-foreground mb-2">
          No tasks found
        </h3>
        <p className="text-sm text-muted-foreground max-w-sm font-body">
          Try adjusting your filters or add a new task.
          Start a conversation with your AI assistant or add a task to get started on your productivity journey.
        </p>
      </div>
    );
  }

  const activeTasks = tasks.filter(t => !t.completed);
  const completedTasks = tasks.filter(t => t.completed);

  return (
    <div className="space-y-6">
      {/* Active Tasks */}
      {activeTasks.length > 0 && (
        <div className="space-y-3">
          {activeTasks.map((task, index) => (
            <div
              key={task.id}
              className="animate-slide-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <TaskItem task={task} />
            </div>
          ))}
        </div>
      )}

      {/* Completed Tasks */}
      {completedTasks.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 px-1">
            <CheckCircle2 className="w-4 h-4 text-accent" />
            <span className="text-sm font-medium text-muted-foreground font-body">
              Completed ({completedTasks.length})
            </span>
          </div>
          {completedTasks.map((task) => (
            <TaskItem key={task.id} task={task} />
          ))}
        </div>
      )}
    </div>
  );
}

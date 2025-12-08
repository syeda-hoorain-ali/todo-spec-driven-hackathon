"""
Tests for User Story 6 - Set Priorities and Tags

As a user, I want to assign priorities and tags to my tasks so that I can better
organize and prioritize my work.

Test Criteria:
- Can add priority when creating a task
- Can add tags when creating a task
- Can update priority of existing task
- Can add/remove tags from existing task
- Tasks display priority and tags correctly
"""
import pytest
from todo_app.models.task import Task
from todo_app.managers.task_manager import TaskManager


class TestUserStory6:
    """Test cases for User Story 6 - Set Priorities and Tags"""

    def test_add_priority_when_creating_task(self):
        """T073, T078: Test adding priority when creating a task"""
        tm = TaskManager()

        # Create tasks with different priorities
        high_task = tm.create_task("High priority task", priority="high")
        medium_task = tm.create_task("Medium priority task", priority="medium")
        low_task = tm.create_task("Low priority task", priority="low")

        # Verify priorities are set correctly
        assert high_task.priority == "high"
        assert medium_task.priority == "medium"
        assert low_task.priority == "low"

    def test_add_tags_when_creating_task(self):
        """T074, T078: Test adding tags when creating a task"""
        tm = TaskManager()

        # Create a task with tags
        tags = ["work", "important", "today"]
        task = tm.create_task("Task with tags", tags=tags)

        # Verify tags are set correctly
        assert task.tags == tags

        # Create a task without tags (should default to empty list)
        task2 = tm.create_task("Task without tags")
        assert task2.tags == []

    def test_update_priority_of_existing_task(self):
        """T077, T078: Test updating priority of existing task"""
        tm = TaskManager()

        # Create a task with default priority
        task = tm.create_task("Test task")

        # Verify initial priority
        assert task.priority == "medium"

        # Update priority
        updated_task = tm.update_task(task.id, priority="high")
        assert updated_task.priority == "high"

        # Verify the change is persistent
        retrieved_task = tm.get_task(task.id)
        assert retrieved_task.priority == "high"

    def test_add_remove_tags_from_existing_task(self):
        """T077, T078: Test adding/removing tags from existing task"""
        tm = TaskManager()

        # Create a task without tags
        task = tm.create_task("Test task")

        # Verify initial tags are empty
        assert task.tags == []

        # Add tags
        new_tags = ["work", "important"]
        updated_task = tm.update_task(task.id, tags=new_tags)
        assert updated_task.tags == new_tags

        # Update with different tags (replace existing)
        different_tags = ["personal", "low-priority"]
        updated_task2 = tm.update_task(task.id, tags=different_tags)
        assert updated_task2.tags == different_tags

        # Update with empty tags
        updated_task3 = tm.update_task(task.id, tags=[])
        assert updated_task3.tags == []

    def test_tag_validation_constraints(self):
        """T079: Validate tag constraints (max 10 tags, max 50 chars each)"""
        tm = TaskManager()

        # Test max tags constraint (10 tags should work)
        max_valid_tags = [f"tag{i}" for i in range(10)]
        task = tm.create_task("Task with max valid tags", tags=max_valid_tags)
        assert task.tags == max_valid_tags

        # Test exceeding max tags constraint (11 tags should fail)
        too_many_tags = [f"tag{i}" for i in range(11)]
        with pytest.raises(ValueError, match="A task cannot have more than 10 tags"):
            tm.create_task("Task with too many tags", tags=too_many_tags)

        # Test max character constraint (50 chars should work)
        max_char_tag = "x" * 50
        task2 = tm.create_task("Task with max char tag", tags=[max_char_tag])
        assert task2.tags == [max_char_tag]

        # Test exceeding max character constraint (51 chars should fail)
        too_long_tag = "x" * 51
        with pytest.raises(ValueError, match="Each tag cannot exceed 50 characters"):
            tm.create_task("Task with too long tag", tags=[too_long_tag])

        # Test empty tag validation
        with pytest.raises(ValueError, match="Tags cannot be empty"):
            tm.create_task("Task with empty tag", tags=[""])

        # Test whitespace-only tag validation
        with pytest.raises(ValueError, match="Tags cannot be empty"):
            tm.create_task("Task with whitespace tag", tags=["   "])

    def test_priority_validation(self):
        """Test priority validation constraints"""
        tm = TaskManager()

        # Test invalid priority
        with pytest.raises(ValueError, match="Priority must be one of: low, medium, high"):
            tm.create_task("Task with invalid priority", priority="invalid")

        # Valid priorities should work
        valid_priorities = ["low", "medium", "high"]
        for priority in valid_priorities:
            task = tm.create_task(f"Task with {priority} priority", priority=priority)
            assert task.priority == priority

    def test_multiple_tasks_with_different_priorities_and_tags(self):
        """Test multiple tasks with various priority and tag combinations"""
        tm = TaskManager()

        # Create tasks with different combinations
        task1 = tm.create_task("Work task", priority="high", tags=["work", "urgent"])
        task2 = tm.create_task("Personal task", priority="medium", tags=["personal"])
        task3 = tm.create_task("Low priority task", priority="low", tags=["later", "maybe", "optional"])
        task4 = tm.create_task("Tagless high priority", priority="high", tags=[])

        # Verify all properties are correctly set
        assert task1.priority == "high"
        assert task1.tags == ["work", "urgent"]

        assert task2.priority == "medium"
        assert task2.tags == ["personal"]

        assert task3.priority == "low"
        assert task3.tags == ["later", "maybe", "optional"]

        assert task4.priority == "high"
        assert task4.tags == []

    def test_update_task_with_tags_and_priority_simultaneously(self):
        """Test updating both tags and priority at the same time"""
        tm = TaskManager()

        # Create a task with initial values
        task = tm.create_task("Initial task", priority="low", tags=["old"])

        # Update both priority and tags
        updated_task = tm.update_task(
            task.id,
            priority="high",
            tags=["new", "tags", "here"]
        )

        assert updated_task.priority == "high"
        assert updated_task.tags == ["new", "tags", "here"]

    def test_filter_tasks_by_tags(self):
        """Test filtering tasks by tags"""
        tm = TaskManager()

        # Create tasks with different tags
        task1 = tm.create_task("Work task", tags=["work", "important"])
        task2 = tm.create_task("Personal task", tags=["personal", "family"])
        task3 = tm.create_task("Shopping task", tags=["shopping", "errand"])
        task4 = tm.create_task("Task without tags", tags=[])

        # Get all tasks and manually filter for those with "work" tag
        all_tasks = tm.get_all_tasks()
        work_tasks = [t for t in all_tasks if "work" in t.tags]

        assert len(work_tasks) == 1
        assert work_tasks[0].id == task1.id

        # Filter for tasks with "personal" tag
        personal_tasks = [t for t in all_tasks if "personal" in t.tags]
        assert len(personal_tasks) == 1
        assert personal_tasks[0].id == task2.id

    def test_task_with_maximum_valid_tags(self):
        """Test creating a task with the maximum number of valid tags"""
        tm = TaskManager()

        # Create 10 tags, each with 50 characters
        max_tags = [f"tag{i:02d}" + "x" * 45 for i in range(10)]  # tag00xxxxx... to tag09xxxxx...

        task = tm.create_task("Task with max tags", tags=max_tags)

        assert len(task.tags) == 10
        assert task.tags == max_tags
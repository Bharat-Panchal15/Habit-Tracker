import pytest
from django.utils import timezone
from users.models import User
from habits.models import Habit
from tasks.models import Task

@pytest.mark.django_db
def test_create_task_with_habit():
    user = User.objects.create_user(username="test123", password="password123")
    habit = Habit.objects.create(user=user, title="Exercise")

    task = Task.objects.create(
        user=user,
        habit=habit,
        description="30 minutes daily workout",
        status="done"
    )

    assert task.user == user
    assert task.habit == habit
    assert task.status == "done"
    assert task.description == "30 minutes daily workout"

@pytest.mark.django_db
def test_create_task_without_habit():
    user = User.objects.create_user(username="test123", password="password123")

    task = Task.objects.create(user=user,description="Buy groceries")

    assert task.user == user
    assert task.habit is None
    assert task.description == "Buy groceries"
    assert task.status == "pending"
    assert task.date == timezone.now().date()

@pytest.mark.django_db
def test_str_returns_description_and_date():
    user = User.objects.create_user(username="test123",password="password123")
    task = Task.objects.create(user=user,description="A 1km walk")

    assert str(task) == f"A 1km walk - {task.date}"

@pytest.mark.django_db
def test_user_related_name_tasks_manager():
    user = User.objects.create_user(username="test123",password="password123")

    Task.objects.create(user=user,description="Task One")
    Task.objects.create(user=user,description="Task Two")

    queryset = user.tasks.all()
    descriptions = {task.description for task in queryset}

    assert descriptions == {"Task One", "Task Two"}

@pytest.mark.django_db
def test_habit_related_name_tasks_manager():
    user = User.objects.create_user(username="test123",password="password123")
    habit = Habit.objects.create(user=user,title="Meditation")

    Task.objects.create(user=user,habit=habit,description="Do meditation for 10 min")
    Task.objects.create(user=user,habit=habit,description="Evening meditation")

    queryset = habit.tasks.all()
    descriptions = {task.description for task in queryset}

    assert queryset.count() == 2
    assert descriptions == {"Do meditation for 10 min", "Evening meditation"}
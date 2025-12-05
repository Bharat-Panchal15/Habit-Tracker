import pytest
from django.utils import timezone
from users.models import User
from habits.models import Habit
from datetime import date, time, timedelta

@pytest.mark.django_db
def test_create_habit_with_all_fields():
    user = User.objects.create_user(username="test123", password="password123")
    end = date.today() + timedelta(days=10)
    reminder = time(hour=8, minute=30)

    habit = Habit.objects.create(
        user=user,
        title="Read a book",
        description="Read 20 pages every day",
        end_date=end,
        reminder_enabled=True,
        reminder_time=reminder,
    )

    assert habit.user == user
    assert habit.title == "Read a book"
    assert habit.description == "Read 20 pages every day"
    assert habit.end_date == end
    assert habit.reminder_enabled is True
    assert habit.reminder_time == reminder
    assert habit.is_active is True
    assert habit.created_on is not None

@pytest.mark.django_db
def test_habit_defaults_when_not_provided():
    user = User.objects.create_user(username="test123", password="password123")
    habit = Habit.objects.create(user=user,title="Read a book")

    assert habit.description is None
    assert habit.end_date is None
    assert habit.reminder_enabled is False
    assert habit.reminder_time is None
    assert habit.is_active is True

@pytest.mark.django_db
def test_str_returns_title_and_username():
    user = User.objects.create_user(username="test123",password="password123")
    habit = Habit.objects.create(user=user,title="Exercise")

    assert str(habit) == "Exercise (test123)"

@pytest.mark.django_db
def test_user_related_name_habits_manager():
    user = User.objects.create_user(username="test123", password="password123")
    Habit.objects.create(user=user, title="Habit One")
    Habit.objects.create(user=user, title="Habit Two")

    queryset = user.habits.all()
    titles = {habit.title for habit in queryset}
    
    assert queryset.count() == 2
    assert titles == {"Habit One", "Habit Two"}
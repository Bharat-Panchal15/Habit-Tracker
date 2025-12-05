import pytest
from django.utils import timezone
from django.db import IntegrityError
from users.models import User
from habits.models import Habit
from streaks.models import StreakRecord

@pytest.mark.django_db
def test_create_streak_record_defaults():
    user = User.objects.create_user(username="test123",password="password123")
    habit = Habit.objects.create(user=user,title="Read a book")
    
    streak = StreakRecord.objects.create(habit=habit)

    assert streak.habit == habit
    assert streak.current_streak == 0
    assert streak.longest_streak == 0
    assert streak.last_completed_date is None

@pytest.mark.django_db
def test_create_streak_record_with_custom_values():
    user = User.objects.create_user(username="test123",password="password123")
    habit = Habit.objects.create(user=user,title="Journal")

    today = timezone.now().date()

    streak = StreakRecord(
        habit=habit,
        current_streak=3,
        longest_streak=5,
        last_completed_date=today
    )

    assert streak.habit == habit
    assert streak.current_streak == 3
    assert streak.longest_streak == 5
    assert streak.last_completed_date == today

@pytest.mark.django_db
def test_one_to_one_relationship_enforced():
    user = User.objects.create_user(username="test123",password="password123")
    habit = Habit.objects.create(user=user,title="Read a book")

    StreakRecord.objects.create(habit=habit)

    with pytest.raises(IntegrityError):
        StreakRecord.objects.create(habit=habit)

@pytest.mark.django_db
def test_related_name_streak_record():
    user = User.objects.create_user(username="test123", password="password123")
    habit = Habit.objects.create(user=user, title="Yoga")

    streak = StreakRecord.objects.create(habit=habit)

    assert habit.streak_record == streak

@pytest.mark.django_db
def test_updating_streak_fields_persists():
    user = User.objects.create_user(username="test123",password="password123")
    habit = Habit.objects.create(user=user, title="Exercise")
    
    streak = StreakRecord.objects.create(habit=habit)
    today = timezone.now().date()

    streak.current_streak = 7
    streak.longest_streak = 24
    streak.last_completed_date = today
    streak.save()

    refreshed = StreakRecord.objects.get(pk=streak.pk)
    
    assert refreshed.habit == habit
    assert refreshed.current_streak == 7
    assert refreshed.longest_streak == 24
    assert refreshed.last_completed_date == today

@pytest.mark.django_db
def test_str_representation():
    user = User.objects.create_user(username="test123", password="password123")
    habit = Habit.objects.create(user=user, title="Programming")

    streak = StreakRecord.objects.create(habit=habit, current_streak=4)

    assert str(streak) == "Streak for Programming: 4 days"
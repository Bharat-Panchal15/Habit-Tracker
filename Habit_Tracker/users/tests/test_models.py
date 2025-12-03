import pytest
from django.utils import timezone
from users.models import User
from datetime import timedelta

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        username="test123",
        password="password123",
        email="example1@gmail.com",
        is_guest=False
    )

    assert user.username == "test123"
    assert user.password != "password123"
    assert user.email == "example1@gmail.com"
    assert user.is_guest is False
    assert user.created_on is not None

@pytest.mark.django_db
def test_guest_expiry_false_for_normal_users():
    user = User.objects.create_user(
        username="test123",
        password="password123",
        email="example123@gmail.com",
        is_guest=False
    )

    assert user.is_guest_expired is False

@pytest.mark.django_db
def test_guest_expiry_true_after_7_days():
    user = User.objects.create_user(
        username="test123",
        password="password123",
        email="example123@gmail.com",
        is_guest=True
    )
    user.created_on = timezone.now().date() - timedelta(days=8)
    user.save()

    assert user.is_guest_expired is True

@pytest.mark.django_db
def test_guest_expiry_false_before_7_days():
    user = User.objects.create_user(
        username="test123",
        password="password123",
        email="example123@gmail.com",
        is_guest=True
    )

    assert user.is_guest_expired is False

@pytest.mark.django_db
def test_guest_days_left():
    user = User.objects.create_user(
        username="test123",
        password="password123",
        email="example123@gmail.com",
        is_guest=True
    )
    user.created_on = timezone.now().date() - timedelta(days=3)
    user.save()

    assert user.guest_days_left == 4
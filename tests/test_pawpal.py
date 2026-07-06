"""Quick tests for the PawPal+ logic layer.

Run from the repo root with:  python -m pytest
"""

from datetime import date, timedelta

import pytest

from pawpal_system import (
    Frequency,
    Owner,
    Pet,
    Priority,
    Scheduler,
    Task,
    TaskStatus,
)


def test_mark_completed_changes_status():
    """Task Completion: mark_completed() moves status to COMPLETED."""
    task = Task("Morning walk", duration_minutes=30)
    assert task.status == TaskStatus.NOT_STARTED  # sanity check

    task.mark_completed()

    assert task.status == TaskStatus.COMPLETED


def test_add_task_increases_pet_task_count():
    """Task Addition: adding a task to a Pet grows its task list."""
    pet = Pet(name="Rex", pet_type="dog")
    assert len(pet.tasks) == 0  # sanity check

    pet.add_task(Task("Give heartworm meds", duration_minutes=5))

    assert len(pet.tasks) == 1


def test_cancelled_task_cannot_be_completed():
    """Status guard: a finished task rejects further changes."""
    task = Task("Brush coat", duration_minutes=20)
    task.cancel()

    with pytest.raises(ValueError):
        task.mark_completed()


def test_pets_do_not_share_task_lists():
    """Each Pet gets its own list (default_factory, not a shared default)."""
    rex = Pet(name="Rex", pet_type="dog")
    whiskers = Pet(name="Whiskers", pet_type="cat")

    rex.add_task(Task("Morning walk", duration_minutes=30))

    assert len(rex.tasks) == 1
    assert len(whiskers.tasks) == 0


def test_completing_daily_task_spawns_tomorrows_copy():
    """Recurrence: complete_task on a DAILY task adds a new instance."""
    pet = Pet(name="Whiskers", pet_type="cat")
    dinner = Task("Feed dinner", 10, frequency=Frequency.DAILY)
    pet.add_task(dinner)

    follow_up = pet.complete_task(dinner)

    assert dinner.status == TaskStatus.COMPLETED       # history kept
    assert len(pet.tasks) == 2                         # new copy added
    assert follow_up.status == TaskStatus.NOT_STARTED
    assert follow_up.due_date == date.today() + timedelta(days=1)


def test_completing_once_task_does_not_recur():
    """Recurrence: ONCE tasks produce no follow-up."""
    pet = Pet(name="Rex", pet_type="dog")
    meds = Task("Give heartworm meds", 5, frequency=Frequency.ONCE)
    pet.add_task(meds)

    follow_up = pet.complete_task(meds)

    assert follow_up is None
    assert len(pet.tasks) == 1


def test_future_task_is_not_pending_today():
    """A spawned task due tomorrow must not appear in today's pending."""
    pet = Pet(name="Rex", pet_type="dog")
    walk = Task("Walk", 30, frequency=Frequency.DAILY)
    pet.add_task(walk)
    pet.complete_task(walk)

    assert len(pet.get_pending_tasks()) == 0


def _owner_with(*tasks: Task) -> Owner:
    """Helper: one owner, one pet, the given tasks."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", pet_type="dog")
    owner.add_pet(pet)
    for task in tasks:
        pet.add_task(task)
    return owner


def test_overlapping_tasks_produce_warning():
    """Conflicts: a task starting inside another's window is flagged."""
    owner = _owner_with(
        Task("Vet visit", 60, scheduled_time="18:00"),
        Task("Walk", 30, scheduled_time="18:30"),
    )
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Vet visit" in warnings[0]


def test_back_to_back_tasks_do_not_conflict():
    """Conflicts: a task starting exactly when another ends is fine."""
    owner = _owner_with(
        Task("Vet visit", 60, scheduled_time="18:00"),
        Task("Walk", 30, scheduled_time="19:00"),
    )
    assert Scheduler(owner).detect_conflicts() == []
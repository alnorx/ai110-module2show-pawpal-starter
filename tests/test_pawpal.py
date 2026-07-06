"""Quick tests for the PawPal+ logic layer.

Run from the repo root with:  python -m pytest
"""

import pytest

from pawpal_system import Pet, Priority, Task, TaskStatus


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
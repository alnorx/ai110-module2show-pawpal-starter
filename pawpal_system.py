"""PawPal+ logic layer.

Backend classes for the PawPal+ pet care scheduling app.
Phase 2: full core implementation (translated from diagrams/uml_draft.mmd).
"""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from enum import Enum


class TaskStatus(Enum):
    """Lifecycle states for a care task."""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Priority(Enum):
    """Priority levels used by the Scheduler to order tasks."""
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class Frequency(Enum):
    """How often a task repeats."""
    ONCE = "Once"
    DAILY = "Daily"
    WEEKLY = "Weekly"


@dataclass
class Task:
    """A single care task for a pet (e.g., walk, feeding, meds)."""
    description: str
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    frequency: Frequency = Frequency.ONCE
    status: TaskStatus = TaskStatus.NOT_STARTED
    scheduled_time: str | None = None  # "HH:MM" 24-hour, or None = flexible
    due_date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        """Validate scheduled_time is a real 'HH:MM' clock time (or None)."""
        t = self.scheduled_time
        if t is None:
            return
        parts = t.split(":")
        valid = (
            len(parts) == 2
            and len(parts[0]) == 2 and len(parts[1]) == 2
            and parts[0].isdigit() and parts[1].isdigit()
            and 0 <= int(parts[0]) <= 23
            and 0 <= int(parts[1]) <= 59
        )
        if not valid:
            raise ValueError(
                f"scheduled_time must be 'HH:MM' (24-hour), got {t!r}"
            )

    # Statuses from which a task may still change.
    _ACTIVE = (TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS)

    def mark_in_progress(self) -> None:
        """Move this task to In Progress.

        Raises ValueError if the task is already finished (Completed
        or Cancelled) — finished tasks are immutable.
        """
        if self.status not in self._ACTIVE:
            raise ValueError(
                f"Cannot start a task that is {self.status.value}."
            )
        self.status = TaskStatus.IN_PROGRESS

    def mark_completed(self) -> None:
        """Move this task to Completed.

        Raises ValueError if the task was cancelled or is already done.
        """
        if self.status not in self._ACTIVE:
            raise ValueError(
                f"Cannot complete a task that is {self.status.value}."
            )
        self.status = TaskStatus.COMPLETED

    def cancel(self) -> None:
        """Cancel this task.

        Raises ValueError if the task is already finished.
        """
        if self.status not in self._ACTIVE:
            raise ValueError(
                f"Cannot cancel a task that is {self.status.value}."
            )
        self.status = TaskStatus.CANCELLED

    def is_pending(self) -> bool:
        """A task is pending if it's active and due by today."""
        return self.status in self._ACTIVE and self.due_date <= date.today()

    def next_occurrence(self) -> "Task | None":
        """Return a fresh Task for the next occurrence, or None if ONCE.

        DAILY tasks recur tomorrow (+1 day), WEEKLY in 7 days.
        dataclasses.replace() copies every field except the ones we
        override: status resets to NOT_STARTED and due_date advances.
        """
        deltas = {
            Frequency.DAILY: timedelta(days=1),
            Frequency.WEEKLY: timedelta(days=7),
        }
        delta = deltas.get(self.frequency)
        if delta is None:  # Frequency.ONCE
            return None
        return replace(
            self,
            status=TaskStatus.NOT_STARTED,
            due_date=self.due_date + delta,
        )


@dataclass
class Pet:
    """A pet belonging to an owner, with its list of care tasks."""
    name: str
    pet_type: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def complete_task(self, task: Task) -> "Task | None":
        """Mark a task completed and auto-add its next occurrence.

        The completed task stays in the list as history. If the task
        recurs (Daily/Weekly), the new instance is appended and
        returned; for one-off tasks, returns None.
        """
        task.mark_completed()
        follow_up = task.next_occurrence()
        if follow_up is not None:
            self.add_task(follow_up)
        return follow_up

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list.

        Uses identity (is) rather than equality so that two tasks with
        identical fields don't get confused for one another.
        """
        for i, existing in enumerate(self.tasks):
            if existing is task:
                del self.tasks[i]
                return
        raise ValueError(f"Task {task.description!r} not found for {self.name}.")

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet completed or cancelled."""
        return [t for t in self.tasks if t.is_pending()]


@dataclass
class Owner:
    """The app user: holds their pets and scheduling constraints."""
    name: str
    available_time_minutes: int = 0
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet for this owner."""
        self.pets.append(pet)

    def set_available_time(self, minutes: int) -> None:
        """Update how much time the owner has available today."""
        if minutes < 0:
            raise ValueError("Available time cannot be negative.")
        self.available_time_minutes = minutes

    def get_all_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every pending task across all pets, as (pet, task) pairs.

        This is the single access point the Scheduler uses — the
        Scheduler never reaches into pet internals directly.
        """
        return [
            (pet, task)
            for pet in self.pets
            for task in pet.get_pending_tasks()
        ]

    def filter_tasks(
        self,
        pet_name: str | None = None,
        status: TaskStatus | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs matching the given filters.

        Each filter is optional: None means "don't filter on this",
        so the criteria compose freely (pet only, status only, both,
        or neither — which returns every task).
        """
        return [
            (pet, task)
            for pet in self.pets
            if pet_name is None or pet.name == pet_name
            for task in pet.tasks
            if status is None or task.status == status
        ]


class Scheduler:
    """Coordination logic: builds and explains the daily plan.

    Not a dataclass — it holds behavior, not data. It reads pets and
    tasks through the Owner rather than storing its own copies.
    """

    def __init__(self, owner: Owner) -> None:
        """Attach this scheduler to the owner whose tasks it will plan."""
        self.owner = owner

    def generate_daily_plan(self) -> list[tuple[Pet, Task]]:
        """Return today's ordered plan as (pet, task) pairs.

        Order of operations matters:
        1. Gather pending tasks from all of the owner's pets.
        2. Sort by priority (highest first).
        3. Greedily keep tasks that fit in the owner's available time.
        Sorting BEFORE filtering ensures a high-priority task is never
        dropped in favor of lower-priority ones that happen to fit.
        """
        items = self.owner.get_all_pending_tasks()
        items = self.sort_tasks_by_priority(items)
        return self.filter_by_available_time(items)

    def sort_by_time(
        self, items: list[tuple[Pet, Task]]
    ) -> list[tuple[Pet, Task]]:
        """Order (pet, task) pairs chronologically by scheduled_time.

        Zero-padded 24-hour "HH:MM" strings sort chronologically as
        plain strings, so no time parsing is needed. Tasks with no
        scheduled_time (flexible) sort after all timed tasks: the key
        is a tuple whose first element is False for timed tasks and
        True for untimed ones, and False < True.
        """
        return sorted(
            items,
            key=lambda pair: (
                pair[1].scheduled_time is None,
                pair[1].scheduled_time or "",
            ),
        )

    def sort_tasks_by_priority(
        self, items: list[tuple[Pet, Task]]
    ) -> list[tuple[Pet, Task]]:
        """Order (pet, task) pairs from highest to lowest task priority.

        Ties are broken by shorter duration first, so quick tasks
        aren't starved by long ones of equal priority. Python's sort
        is stable, so insertion order breaks any remaining ties.
        """
        return sorted(
            items,
            key=lambda pair: (-pair[1].priority.value, pair[1].duration_minutes),
        )

    def filter_by_available_time(
        self, items: list[tuple[Pet, Task]]
    ) -> list[tuple[Pet, Task]]:
        """Greedily keep pairs whose total duration fits the owner's time.

        Walks the (already sorted) list and skips any task that would
        push the running total past available_time_minutes. Later,
        shorter tasks may still fit — the whole budget gets used.
        """
        budget = self.owner.available_time_minutes
        plan: list[tuple[Pet, Task]] = []
        used = 0
        for pet, task in items:
            if used + task.duration_minutes <= budget:
                plan.append((pet, task))
                used += task.duration_minutes
        return plan

    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        """Convert 'HH:MM' to minutes since midnight (e.g. '08:30' -> 510)."""
        hours, minutes = hhmm.split(":")
        return int(hours) * 60 + int(minutes)

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for overlapping timed tasks (never raises).

        Lightweight sweep: consider today's pending tasks that have a
        scheduled_time, sort them chronologically, and walk the list
        once while remembering the latest end time seen so far. Any
        task that starts before that point overlaps — including tasks
        for different pets, since one owner can't be in two places.
        An empty list means no conflicts.
        """
        timed = [
            (pet, task)
            for pet, task in self.owner.get_all_pending_tasks()
            if task.scheduled_time is not None
        ]
        timed.sort(key=lambda pair: pair[1].scheduled_time)

        warnings: list[str] = []
        latest_end = -1  # minutes since midnight
        blocker: tuple[Pet, Task] | None = None  # task holding latest_end

        for pet, task in timed:
            start = self._to_minutes(task.scheduled_time)
            if start < latest_end and blocker is not None:
                b_pet, b_task = blocker
                warnings.append(
                    f"Warning: '{task.description}' ({pet.name}) at "
                    f"{task.scheduled_time} overlaps "
                    f"'{b_task.description}' ({b_pet.name}), which runs "
                    f"{b_task.scheduled_time}-"
                    f"{latest_end // 60:02d}:{latest_end % 60:02d}."
                )
            end = start + task.duration_minutes
            if end > latest_end:
                latest_end = end
                blocker = (pet, task)
        return warnings

    def explain_plan(self, plan: list[tuple[Pet, Task]]) -> str:
        """Return a human-readable explanation of the plan's ordering."""
        if not plan:
            return (
                "No tasks scheduled. Either there are no pending tasks, "
                "or none fit in the available time "
                f"({self.owner.available_time_minutes} min)."
            )
        lines = []
        total = 0
        for i, (pet, task) in enumerate(plan, start=1):
            total += task.duration_minutes
            lines.append(
                f"{i}. {task.description} — {pet.name} the {pet.pet_type} "
                f"({task.priority.name.title()} priority, "
                f"{task.duration_minutes} min)"
            )
        lines.append(
            f"Tasks are ordered by priority, then by shorter duration. "
            f"Total: {total} of {self.owner.available_time_minutes} "
            f"available minutes."
        )
        skipped = len(self.owner.get_all_pending_tasks()) - len(plan)
        if skipped:
            lines.append(
                f"{skipped} pending task(s) did not fit today's time budget."
            )
        return "\n".join(lines)
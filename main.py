"""PawPal+ demo script.

Temporary testing ground: builds a sample household in code and prints
today's schedule to the terminal. Run with:  python main.py
"""

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task, TaskStatus


def build_sample_data() -> Owner:
    """Create an owner with two pets and a mix of tasks."""
    owner = Owner(name="Sam", available_time_minutes=60)

    rex = Pet(name="Rex", pet_type="dog")
    whiskers = Pet(name="Whiskers", pet_type="cat")
    owner.add_pet(rex)
    owner.add_pet(whiskers)

    # Deliberately added OUT of chronological order to prove sorting works.
    rex.add_task(Task("Evening walk", 30, Priority.HIGH, Frequency.DAILY,
                      scheduled_time="18:30"))
    rex.add_task(Task("Give heartworm meds", 5, Priority.HIGH, Frequency.ONCE,
                      scheduled_time="08:00"))
    rex.add_task(Task("Brush coat", 20, Priority.LOW, Frequency.WEEKLY))

    whiskers.add_task(Task("Feed dinner", 10, Priority.HIGH, Frequency.DAILY,
                           scheduled_time="17:00"))
    whiskers.add_task(Task("Clean litter box", 10, Priority.MEDIUM,
                           Frequency.DAILY))
    whiskers.complete_task(whiskers.tasks[0])  # spawns tomorrow's dinner

    # Deliberate conflict: vet visit overlaps Rex's 18:30 evening walk
    # AND Whiskers' grooming starts at the exact same time.
    rex.add_task(Task("Vet visit", 60, Priority.HIGH, Frequency.ONCE,
                      scheduled_time="18:00"))
    whiskers.add_task(Task("Grooming", 20, Priority.MEDIUM, Frequency.ONCE,
                           scheduled_time="18:00"))

    return owner


def print_schedule(owner: Owner, scheduler: Scheduler) -> None:
    """Print a formatted 'Today's Schedule' to the terminal."""
    plan = scheduler.generate_daily_plan()

    width = 58
    print("=" * width)
    print(f"  PawPal+ | Today's Schedule for {owner.name}".ljust(width))
    print(f"  Time available: {owner.available_time_minutes} min".ljust(width))
    print("=" * width)

    if not plan:
        print("  Nothing scheduled today!")
    else:
        for i, (pet, task) in enumerate(plan, start=1):
            who = f"{pet.name} ({pet.pet_type})"
            print(
                f"  {i}. [{task.priority.name:<6}] {task.description:<22} "
                f"{who:<16} {task.duration_minutes:>3} min"
            )

    print("-" * width)
    print("Scheduler's reasoning:")
    print(scheduler.explain_plan(plan))
    print("=" * width)


def main() -> None:
    owner = build_sample_data()
    scheduler = Scheduler(owner)
    print_schedule(owner, scheduler)

    # --- Phase 4: sorting by time ---
    print("\nAll tasks sorted by time (untimed tasks last):")
    everything = owner.filter_tasks()  # no filters = all tasks
    for pet, task in scheduler.sort_by_time(everything):
        when = task.scheduled_time or "anytime"
        print(f"  {when:>7}  {task.description} ({pet.name})")

    # --- Phase 4: filtering ---
    print("\nOnly Rex's tasks:")
    for pet, task in owner.filter_tasks(pet_name="Rex"):
        print(f"  - {task.description} [{task.status.value}]")

    print("\nOnly COMPLETED tasks (any pet):")
    for pet, task in owner.filter_tasks(status=TaskStatus.COMPLETED):
        print(f"  - {task.description} ({pet.name})")

    print("\nRex's NOT STARTED tasks (both filters combined):")
    for pet, task in owner.filter_tasks(
        pet_name="Rex", status=TaskStatus.NOT_STARTED
    ):
        print(f"  - {task.description}")

    # --- Phase 4: recurring tasks ---
    print("\nWhiskers' full task history (recurrence in action):")
    for task in owner.pets[1].tasks:
        print(
            f"  - {task.description:<18} due {task.due_date}  "
            f"[{task.status.value}]"
        )
    print("Completing daily 'Feed dinner' auto-created tomorrow's copy;")
    print("note it is NOT in today's plan above — it isn't due yet.")

    # --- Phase 4: conflict detection ---
    print("\nConflict check:")
    conflicts = scheduler.detect_conflicts()
    if not conflicts:
        print("  No scheduling conflicts found.")
    for warning in conflicts:
        print(f"  {warning}")


if __name__ == "__main__":
    main()
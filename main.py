"""PawPal+ demo script.

Temporary testing ground: builds a sample household in code and prints
today's schedule to the terminal. Run with:  python main.py
"""

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def build_sample_data() -> Owner:
    """Create an owner with two pets and a mix of tasks."""
    owner = Owner(name="Sam", available_time_minutes=60)

    rex = Pet(name="Rex", pet_type="dog")
    whiskers = Pet(name="Whiskers", pet_type="cat")
    owner.add_pet(rex)
    owner.add_pet(whiskers)

    rex.add_task(Task("Morning walk", 30, Priority.HIGH, Frequency.DAILY))
    rex.add_task(Task("Give heartworm meds", 5, Priority.HIGH, Frequency.ONCE))
    rex.add_task(Task("Brush coat", 20, Priority.LOW, Frequency.WEEKLY))

    whiskers.add_task(Task("Feed dinner", 10, Priority.HIGH, Frequency.DAILY))
    whiskers.add_task(Task("Clean litter box", 10, Priority.MEDIUM, Frequency.DAILY))

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


if __name__ == "__main__":
    main()
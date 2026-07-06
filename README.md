# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

==========================================================
  PawPal+ | Today's Schedule for Sam                      
  Time available: 60 min                                  
==========================================================
  1. [HIGH  ] Give heartworm meds    Rex (dog)          5 min
  2. [HIGH  ] Evening walk           Rex (dog)         30 min
  3. [MEDIUM] Clean litter box       Whiskers (cat)    10 min
----------------------------------------------------------
Scheduler's reasoning:
1. Give heartworm meds — Rex the dog (High priority, 5 min)
2. Evening walk — Rex the dog (High priority, 30 min)
3. Clean litter box — Whiskers the cat (Medium priority, 10 min)
Tasks are ordered by priority, then by shorter duration. Total: 45 of 60 available minutes.
3 pending task(s) did not fit today's time budget.
==========================================================

All tasks sorted by time (untimed tasks last):
    08:00  Give heartworm meds (Rex)
    17:00  Feed dinner (Whiskers)
    17:00  Feed dinner (Whiskers)
    18:00  Vet visit (Rex)
    18:00  Grooming (Whiskers)
    18:30  Evening walk (Rex)
  anytime  Brush coat (Rex)
  anytime  Clean litter box (Whiskers)

Only Rex's tasks:
  - Evening walk [Not Started]
  - Give heartworm meds [Not Started]
  - Brush coat [Not Started]
  - Vet visit [Not Started]

Only COMPLETED tasks (any pet):
  - Feed dinner (Whiskers)

Rex's NOT STARTED tasks (both filters combined):
  - Evening walk
  - Give heartworm meds
  - Brush coat
  - Vet visit

Whiskers' full task history (recurrence in action):
  - Feed dinner        due 2026-07-06  [Completed]
  - Clean litter box   due 2026-07-06  [Not Started]
  - Feed dinner        due 2026-07-07  [Not Started]
  - Grooming           due 2026-07-06  [Not Started]
Completing daily 'Feed dinner' auto-created tomorrow's copy;
note it is NOT in today's plan above — it isn't due yet.

Conflict check:
  Warning: 'Grooming' (Whiskers) at 18:00 overlaps 'Vet visit' (Rex), which runs 18:00-19:00.
  Warning: 'Evening walk' (Rex) at 18:30 overlaps 'Vet visit' (Rex), which runs 18:00-19:00.

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

=========================================== test session starts ============================================
platform linux -- Python 3.12.1, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspaces/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 9 items                                                                                          

tests/test_pawpal.py .........                                                                       [100%]

============================================ 9 passed in 0.07s =============================================

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks_by_priority()` | Chronological sort by optional `"HH:MM"` time (zero-padded strings sort correctly with no parsing; untimed tasks go last via a tuple key). The daily plan sorts by priority, breaking ties with shorter duration. |
| Filtering | `Owner.filter_tasks(pet_name, status)`, `Scheduler.filter_by_available_time()` | One composable method filters by pet, status, both, or neither (`None` = don't filter) in a single O(n) pass. The plan builder greedily keeps tasks that fit the owner's time budget — sorting *before* filtering so high-priority tasks are never dropped for smaller low-priority ones. |
| Conflict handling | `Scheduler.detect_conflicts()` | O(n log n) sweep: sort timed tasks by start, track the latest end time, flag any task starting before it. Catches non-adjacent overlaps, works across pets, and returns warning strings instead of raising — so the UI warns without crashing. Back-to-back tasks (one ends exactly as the next starts) are not conflicts. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a Daily/Weekly task auto-spawns a fresh copy due +1/+7 days (`datetime.timedelta` handles month rollovers). The completed task is kept as history, and the spawned copy stays out of today's plan because `is_pending()` requires `due_date <= today`. |



## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:
The UI

The Streamlit app (streamlit run app.py) has three areas:


1. Owner — set your name and how many minutes you have available today. The time budget directly constrains the generated plan.
2. Pets & Tasks — add pets (name + species), then add tasks for a chosen pet: title, duration, priority, frequency (Once/Daily/Weekly), and an optional scheduled time in 24-hour HH:MM. The task table can be filtered by pet and status, and always displays in chronological order with "anytime" tasks last. A dropdown lets you mark tasks complete — completing a Daily task instantly spawns tomorrow's copy in the table.
3. Build Schedule — conflict warnings (or a green all-clear) appear before you generate. The button produces today's ordered plan, with a "Why this order?" expander explaining the Scheduler's reasoning.


Example workflow

Add pet Rex (dog) → schedule "Evening walk" (30 min, high, daily, 18:30) and "Vet visit" (60 min, high, once, 18:00) → a ⚠️ warning appears: the walk overlaps the vet visit, which runs until 19:00 → change the walk to 19:00 → ✅ no conflicts → Generate schedule → both tasks appear, ordered, with reasoning → mark the walk complete → tomorrow's walk appears automatically, but stays out of today's plan.

Scheduler behaviors demonstrated


Sorting: the task table is time-ordered; the plan is priority-ordered.
Constraint filtering: lower the available minutes and regenerate — low-priority tasks drop out first, and the explanation reports how many didn't fit.
Conflict warnings: overlapping timed tasks produce specific warnings before planning, without blocking.
Recurrence: completed Daily/Weekly tasks self-schedule their next occurrence.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

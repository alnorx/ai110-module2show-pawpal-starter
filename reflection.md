# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

My initial design has four classes, each with one responsibility. Owner represents the app user and holds the scheduling constraints (available time, preferences) plus their list of pets. Pet stores pet-specific information (name, type) and maintains that pet's list of care tasks. Task represents a single care activity with a description, duration, and priority, and manages its own lifecycle through statuses (Not Started, In Progress, Completed, Cancelled). Scheduler contains the coordination logic: it reads pets and tasks through the Owner, sorts pending tasks by priority, filters them to fit the owner's available time, and produces a daily plan with an explanation of its ordering. Relationships are one-directional: an Owner has many Pets, a Pet has many Tasks, and the Scheduler plans for one Owner.

- What classes did you include, and what responsibilities did you assign to each?
Pet — Responsible for storing pet-specific data: the pet's name, its type (e.g., dog, cat, snake, spider), and the owner's name. It also maintains the list of activities scheduled for that pet.
Activity — Responsible for representing a single scheduled activity. It holds the description and scheduled time, and it manages the activity's status as it moves through its lifecycle: Not Started, In Progress, Completed, or Cancelled.
Scheduler — Responsible for the coordination logic: adding new pets and activities, organizing activities based on constraints like time, priority, and owner preferences, and determining which activity a pet should do next.

**b. Design changes**

After asking my AI assistant to review the skeleton, I made two changes. First, the AI noticed that generate_daily_plan() returned plain Task objects, which lost the pet–task relationship at the Scheduler boundary — the plan couldn't say which pet each task was for, making explain_plan() impossible to write well. I changed the plan to return (Pet, Task) pairs so the relationship survives. Second, the review flagged that the order of sorting vs. time-filtering was unspecified: filtering first could drop a high-priority task in favor of smaller low-priority ones. I documented in the docstring that the Scheduler must sort by priority before greedily filling available time. I also noted two issues to handle during implementation rather than now: status transitions need validation (a Cancelled task shouldn't become Completed), and the preferences attribute isn't consumed by any Scheduler logic yet, so I'll either wire it into scheduling or remove it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- Available time is the hard constraint: the owner sets a daily minute budget, and generate_daily_plan() will not schedule past it. Priority (High/Medium/Low) is the ranking constraint that decides which tasks win when time is scarce, with ties broken by shorter duration so quick tasks aren't starved by long ones of equal importance. Scheduled time is a soft constraint: fixed-time tasks are checked for overlaps by detect_conflicts(), which warns rather than blocks.  
- I decided priority and available time mattered most by thinking about the actual failure modes for a pet owner: skipping a low-priority task (brushing) is an inconvenience, but skipping a high-priority one (medication) can harm the pet

**b. Tradeoffs**

Use your AI coding assistant to add docstrings to your new algorithmic methods.Update your README.md with a dedicated Smarter Scheduling section that documents each feature you implemented and names the method that implements it:
 Sorting behavior (e.g., Scheduler.sort_by_time())Filtering behavior (e.g., by pet or completion status)Conflict detection logicRecurring task logicVerified docstring completeness and drafted documentation updatesVerified docstring completeness and drafted documentation updatesDocstring coverage is already complete — every Phase 4 method was documented as we wrote it (writing the docstring with the method beats retrofitting; the design reasoning is fresh). The AST check above confirms no gaps, and each first line is a proper one-line summary.
For your README.md, here's the Smarter Scheduling section — paste it after your Sample Output section:
markdown## Smarter Scheduling

Phase 4 added four algorithmic features to the logic layer. All logic
lives in `pawpal_system.py`; the UI and CLI only call these methods.

### Sorting by time — `Scheduler.sort_by_time()`
Orders tasks chronologically by their optional `scheduled_time`
("HH:MM", 24-hour). Zero-padded time strings sort correctly as plain
strings, so no parsing is needed; a tuple sort key pushes untimed
("anytime") tasks after all timed ones. The daily plan itself still
orders by priority via `Scheduler.sort_tasks_by_priority()`, which
sorts highest priority first and breaks ties with shorter duration.

### Filtering — `Owner.filter_tasks(pet_name=..., status=...)`
One method covers all filter combinations: by pet, by status
(`TaskStatus` enum), both, or neither. Each criterion defaults to
`None`, meaning "don't filter on this," so the criteria compose
freely in a single O(n) pass.

### Recurring tasks — `Task.next_occurrence()` + `Pet.complete_task()`
Completing a Daily or Weekly task through `Pet.complete_task()`
automatically appends a fresh copy due `+1` or `+7` days later
(computed with `datetime.timedelta`, so month/year rollovers are
handled). The completed task stays in the list as history. A spawned
task due tomorrow does not appear in today's plan: `Task.is_pending()`
requires `due_date <= today`.

### Conflict detection — `Scheduler.detect_conflicts()`
A lightweight sweep over today's timed tasks: sort by start time,
then walk once while tracking the latest end time seen so far; any
task starting before that point overlaps. This is O(n log n), catches
non-adjacent overlaps (a long task blocking several later ones), and
works across pets. It returns a list of warning strings — never an
exception — so the CLI prints them and the Streamlit UI shows them
as warnings without ever crashing. Tasks that start exactly when
another ends are back-to-back, not conflicts.

All features are covered by the test suite (`python -m pytest`,
9 tests).
Every claim in it is verifiable by a grader against your code and tests — feature, method name, and the one design fact worth knowing per feature, matching the assignment's requested structure.
That wraps Phase 4 completely: four algorithms implemented and tested, one evaluated against an alternative, everything documented. Commit with something like Document Phase 4 algorithms in README; verify docstring coverage and push. Phase 5 whenever you're ready.## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |Prepared to populate scheduling feature table systematicallyPrepared to populate scheduling feature table systematicallyThe starter wants it as a table — here's the same content in their format:
markdown## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks_by_priority()` | Chronological sort by optional `"HH:MM"` time (zero-padded strings sort correctly with no parsing; untimed tasks go last via a tuple key). The daily plan sorts by priority, breaking ties with shorter duration. |
| Filtering | `Owner.filter_tasks(pet_name, status)`, `Scheduler.filter_by_available_time()` | One composable method filters by pet, status, both, or neither (`None` = don't filter) in a single O(n) pass. The plan builder greedily keeps tasks that fit the owner's time budget — sorting *before* filtering so high-priority tasks are never dropped for smaller low-priority ones. |
| Conflict handling | `Scheduler.detect_conflicts()` | O(n log n) sweep: sort timed tasks by start, track the latest end time, flag any task starting before it. Catches non-adjacent overlaps, works across pets, and returns warning strings instead of raising — so the UI warns without crashing. Back-to-back tasks (one ends exactly as the next starts) are not conflicts. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a Daily/Weekly task auto-spawns a fresh copy due +1/+7 days (`datetime.timedelta` handles month rollovers). The completed task is kept as history, and the spawned copy stays out of today's plan because `is_pending()` requires `due_date <= today`. |
Two things I adjusted while converting: I deleted the > Fill in once you've implemented... blockquote (it's an instruction to you, not content — leftover placeholders in a submitted README look unfinished), and I noticed the starter's Filtering row hints at something different from what I documented before: "skip tasks if time runs out" is your Phase 2 filter_by_available_time(), not the Phase 4 filter_tasks(). So that row now credits both methods — the table reads as the complete filtering story, and it matches the starter's example hint.
If you'd rather keep the table lean (some graders prefer scannable), you can trim each Notes cell to its first sentence and the rest is still in your docstrings. Table's the contract; docstrings are the detail.Step 1: Reflect the Algorithmic Layer in the UI
Your backend is now "smart," but your UI might still be basic. Ensure the user can actually see and use the features you built in Phase 3.Update your display logic in app.py to use the methods from your Scheduler class (like sorting or conflict warnings).Use Streamlit components like st.success, st.warning, or st.table to make the sorted and filtered data look professional.
If your Scheduler flags a task conflict, how should that warning be presented in the Streamlit UI to be most helpful to a pet owner?
Step 2: Finalize Your System Architecture (UML)Revisit the Mermaid.js UML diagram you drafted in Phase 1. Does it still match your final code in pawpal_system.py?Attach pawpal_system.py and ask your AI coding assistant: "Based on my final implementation, what updates should I make to my initial UML diagram to accurately show how my classes interact?".Adjust your Mermaid code to reflect any new methods or relationships you added during the build.Save the updated Mermaid source as diagrams/uml_final.mmd in your project folder. Export a PNG for the README if you'd like, but the .mmd source file is required.
Step 3: Polish Your READMEOpen README.md. Your README should act as a professional manual for your app.Reference or attach the relevant files and ask your AI coding assistant to help draft a "Features" list that accurately describes the algorithms you implemented (e.g., "Sorting by time," "Conflict warnings," "Daily recurrence").Replace the "📸 Demo" section with a Demo Walkthrough that describes, in text:
 The main UI features and what actions a user can performAn example workflow (e.g., add a pet → schedule a task → view today's schedule)Key Scheduler behaviors shown (sorting, conflict warnings, etc.)A fenced code block of sample CLI output from running main.pyShow moreOrchestrated UI refinements, UML architecture updates, and README documentation enhancementsOrchestrated UI refinements, UML architecture updates, and README documentation enhancementsBig step — three deliverables. Taking them in order.
Step 1: Surface the algorithms in the UI. Auditing app.py against the Phase 4 features: conflict warnings are wired (on Generate), but there are three gaps — no way to set a task's time (so conflict detection is untriggerable from the UI!), no filter controls, and the table isn't time-sorted. Fixing all three:Identified discrepancies between draft UML and implemented code architectureIdentified discrepancies between draft UML and implemented code architectureStep 3: README sections. Grabbing fresh CLI output for the walkthrough:Ran a command, read a fileRan a command, read a fileAll three deliverables are above. What to do with each:
app.py — replace yours and run streamlit run app.py. The additions: an optional Scheduled time field on the task form (with a friendly error if you type 8:00 instead of 08:00 — the logic layer's validation surfaces via try/except rather than crashing the app), filter dropdowns above the task table calling Owner.filter_tasks(), the table now time-sorted via Scheduler.sort_by_time() with a Time column, and conflicts shown proactively — before you click Generate, not after.
That last one is my answer to the assignment's embedded question about presenting conflict warnings helpfully. Three principles: (1) Before, not after — a warning that appears only once the plan is built arrives too late to act on; showing it above the Generate button lets the owner fix times first. (2) Specific and actionable — each warning names both tasks, both pets, and when the blocking task ends ("...overlaps 'Vet visit' (Rex), which runs 18:00–19:00"), which is enough to know what to change. (3) Advisory, not blocking — st.warning (yellow), never st.error or an exception, because the overlap might be intentional (two family members, two dogs). And the green "No conflicts today ✅" when clear matters too — silence is ambiguous; confirmation builds trust that the check actually ran.
uml_final.mmd — save to diagrams/uml_final.mmd alongside the draft. Keeping both files is the point: the diff between them is the honest record of how the design evolved, and the divergences are exactly the ones we logged as they happened (enums in the skeleton, frequency in Phase 2, scheduled_time/due_date in Phase 4). The one structurally new relationship — Task ..> Task : next_occurrence() creates — uses a dashed dependency arrow rather than a solid association, since a Task creates its successor but doesn't hold a reference to it.
README_sections.md — copy the two sections into your README (Features near the top, Demo Walkthrough replacing the 📸 Demo section). One caveat: the sample CLI output embeds due dates from my run — regenerate that block with your own python main.py output before committing, so the README matches what a grader reproduces.
Commit checklist for this step: app.py, diagrams/uml_final.mmd, README.md — plus a quick python -m pytest (9 passing) before pushing. What's left in the phase?AppPY Uml finalDiagram · MMD Readme sectionsDocument · MD ## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?Show moreWeighed constraint priorities and scheduling tradeoffs thoughtfullyWeighed constraint priorities and scheduling tradeoffs thoughtfullyHere are drafts grounded in what your scheduler actually does — adapt the wording to your voice:
2a. Constraints and priorities

My scheduler considers four constraints. Available time is the hard constraint: the owner sets a daily minute budget, and generate_daily_plan() will not schedule past it. Priority (High/Medium/Low) is the ranking constraint that decides which tasks win when time is scarce, with ties broken by shorter duration so quick tasks aren't starved by long ones of equal importance. Scheduled time is a soft constraint: fixed-time tasks are checked for overlaps by detect_conflicts(), which warns rather than blocks. Due date constrains recurrence — a task spawned for tomorrow is excluded from today's plan because is_pending() requires due_date <= today.
I decided priority and available time mattered most by thinking about the actual failure modes for a pet owner: skipping a low-priority task (brushing) is an inconvenience, but skipping a high-priority one (medication) can harm the pet. That reasoning also dictated the order of operations inside the scheduler — sort by priority before filtering by time — because filtering first could keep several small low-priority tasks while dropping the one high-priority task that didn't fit. One honest limitation: Owner.preferences exists in the data model but no algorithm consumes it yet; I kept it as a documented extension point rather than pretending it's a real constraint.

2b. Tradeoffs

My scheduler fills the time budget greedily — it walks the priority-sorted list and takes each task that still fits — rather than solving for the optimal combination.
Greedy-by-priority guarantees the highest-priority tasks are considered first, and for pet care "the important things happen" beats "the most minutes get used.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project 
I used the AI to build the skeleton for the code with TODO instead of code and wrote test code see if if had any suggestions.


**b. Judgment and verification**

- The AI wanted to make all task to be completed in one day, when I asked to set a daily task.

---

## 4. Testing and Verification

**a. What you tested**

adding a task to a Pet
a finished task rejects further changes.
Each Pet gets its own list
- Why were these tests important?
These test ensure that each pet gets a task and that there are no conflicts

**b. Confidence**

- How confident are you that your scheduler works correctly?
- I 50% confidence that the shceduler works correctly.
-- What is the task limit for each pet or owner


---

## 5. Reflection

**a. What went well**

- Using the AI to guide me creatung a somewhat workable app.

**b. What you would improve**

- I would add:
notification for when tasks are 30 minutes from start date.
a reminder to do a task
    

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
-The AI reduce the struggle of setting of the logic algorithm and made the project less stressful.
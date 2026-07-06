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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

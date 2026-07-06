import streamlit as st

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

with st.expander("Scenario"):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

# ---------------------------------------------------------------
# Application "memory": create the Owner and Scheduler exactly once
# per browser session. Streamlit reruns this script on every click,
# so anything not stored in st.session_state would be reset.
# ---------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time_minutes=60)
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.divider()

# ---------------------------------------------------------------
# Owner settings
# ---------------------------------------------------------------
st.subheader("Owner")
col_a, col_b = st.columns(2)
with col_a:
    owner.name = st.text_input("Owner name", value=owner.name)
with col_b:
    minutes = st.number_input(
        "Time available today (minutes)",
        min_value=0,
        max_value=1440,
        value=owner.available_time_minutes,
        step=5,
    )
    owner.set_available_time(int(minutes))

# ---------------------------------------------------------------
# Pets: form data is handled by Owner.add_pet()
# ---------------------------------------------------------------
st.subheader("Pets")
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    st.write("")  # spacer to align the button with the inputs
    if st.button("Add pet"):
        name = pet_name.strip()
        if not name:
            st.error("Pet name can't be empty.")
        elif any(p.name == name for p in owner.pets):
            st.error(f"You already have a pet named {name}.")
        else:
            owner.add_pet(Pet(name=name, pet_type=species))

if owner.pets:
    st.write("Your pets: " + ", ".join(f"{p.name} ({p.pet_type})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above — tasks belong to a pet.")

# ---------------------------------------------------------------
# Tasks: form data is handled by Pet.add_task()
# ---------------------------------------------------------------
st.markdown("### Tasks")

if owner.pets:
    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        task_pet = st.selectbox("For pet", [p.name for p in owner.pets])
    with col3:
        duration = st.number_input(
            "Duration (min)", min_value=1, max_value=240, value=20
        )
    with col4:
        priority = st.selectbox(
            "Priority",
            list(Priority),
            format_func=lambda p: p.name.lower(),
            index=0,  # list(Priority) is [HIGH, MEDIUM, LOW]
        )
    with col5:
        frequency = st.selectbox(
            "Frequency", list(Frequency), format_func=lambda f: f.value
        )

    if st.button("Add task"):
        if not task_title.strip():
            st.error("Task title can't be empty.")
        else:
            pet = next(p for p in owner.pets if p.name == task_pet)
            pet.add_task(
                Task(task_title.strip(), int(duration), priority, frequency)
            )

# The table is rendered FROM the real objects — the objects are the
# single source of truth, the table is just a view of them.
all_tasks = [(pet, task) for pet in owner.pets for task in pet.tasks]
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "Pet": pet.name,
                "Task": task.description,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority.name.lower(),
                "Frequency": task.frequency.value,
                "Status": task.status.value,
            }
            for pet, task in all_tasks
        ]
    )
elif owner.pets:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------
# Build Schedule: the button calls the Scheduler ("the brain")
# ---------------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule", type="primary"):
    plan = scheduler.generate_daily_plan()
    if not plan:
        st.info(scheduler.explain_plan(plan))
    else:
        st.success(f"Planned {len(plan)} task(s) for {owner.name}'s day:")
        for i, (pet, task) in enumerate(plan, start=1):
            st.markdown(
                f"**{i}. {task.description}** — {pet.name} the {pet.pet_type} "
                f"({task.priority.name.lower()} priority, "
                f"{task.duration_minutes} min)"
            )
        with st.expander("Why this order?"):
            st.text(scheduler.explain_plan(plan))
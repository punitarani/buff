"""
Streamlit App

python -m streamlit run main.py
"""

import asyncio

import streamlit as st

from buff.llm.agents.research import breakdown_objective, research_planner


def format_steps(idea_steps: list[str]) -> str:
    """Format the objective steps."""
    formatted_steps = []
    for idx, step in enumerate(idea_steps):
        formatted_step = f"**{idx + 1}**: {step}"
        formatted_steps.append(formatted_step)
    return "\n\n".join(formatted_steps)


def format_plan(plan: list[dict]) -> str:
    """Format the strp plan."""
    formatted_plan = []
    for idx, task in enumerate(plan):
        formatted_task = f"`{task['agent']}` {task['task']}"
        formatted_plan.append(formatted_task)
    return "\n\n".join(formatted_plan)


st.set_page_config(page_title="buff", page_icon=":microscope:", layout="wide")

st.title("buff")

research_objective = st.text_input(
    "Research Objective",
    "Can protein misfolding be used to treat neurodegenerative diseases?"
)
start_button = st.button(
    "Start Research",
    help="Start the research process.",
    use_container_width=True,
    disabled=("steps" in st.session_state),
)

st.divider()
idea_1_col, idea_2_col, idea_3_col = st.columns(3)

if start_button or "steps" in st.session_state:
    with st.spinner("Analyzing the objective..."):
        if "steps" not in st.session_state:
            steps = asyncio.run(breakdown_objective(research_objective))
            st.session_state["steps"] = steps
        else:
            steps = st.session_state["steps"]

    if steps:
        st.subheader("Research Steps")
        st.write(format_steps(steps))
        run_button = st.button("Run Plan", help="Run the research plan.", use_container_width=True)
        # TODO: allow user to to edit steps

        if run_button:
            for s_id, step in enumerate(steps):
                with st.status(f"Step {s_id + 1}: {step}"):
                    section_content = st.empty()
                    section_content.write(f"Running Step {s_id + 1} ...")
                    research_plan = asyncio.run(research_planner(step))
                    section_content.write(format_plan(research_plan))
                    st.divider()

                    st.error("Not Implemented")
                st.stop()

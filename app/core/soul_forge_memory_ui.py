
"""
⚔️ SOUL FORGE MEMORY UI
"""

import streamlit as st

from app.core.soul_forge_memory import (
    add_memory,
    delete_conversation,
    list_conversations,
    load_conversation,
    rename_conversation,
    search_memory,
)


def render_soul_forge_memory_sidebar(project: str = ""):

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🧠 SOUL FORGE MEMORY")

    conversations = list_conversations()

    if not conversations:

        st.sidebar.caption("No saved conversations yet.")

    else:

        st.sidebar.caption(
            f"{len(conversations)} saved conversation(s)"
        )

        for item in conversations[:20]:

            title = item.get("title") or "New Chat"
            conversation_id = item.get("conversation_id")

            if st.sidebar.button(
                f"💬 {title[:32]}",
                key=f"sf_memory_chat_{conversation_id}",
                use_container_width=True,
            ):

                conversation = load_conversation(
                    conversation_id
                )

                if conversation:

                    st.session_state[
                        "sf_active_conversation_id"
                    ] = conversation_id

                    st.session_state[
                        "sf_loaded_conversation"
                    ] = conversation

                    st.rerun()

    with st.sidebar.expander(
        "🧠 Important Memories",
        expanded=False,
    ):

        query = st.text_input(
            "Search memory",
            key="sf_memory_search",
        )

        if query:

            results = search_memory(
                query,
                project=project,
                limit=10,
            )

            if not results:

                st.caption("No matching memories.")

            for memory in results:

                importance = memory.get(
                    "importance",
                    5,
                )

                memory_type = memory.get(
                    "memory_type",
                    "fact",
                )

                st.markdown(
                    f"**{memory_type.upper()} · "
                    f"{importance}/10**"
                )

                st.caption(
                    memory.get("content", "")
                )


def render_soul_forge_memory_panel(project: str = ""):

    with st.expander(
        "🧠 SOUL FORGE MEMORY",
        expanded=False,
    ):

        st.caption(
            "Long-term memory that helps SOUL FORGE "
            "retain important project information."
        )

        results = search_memory(
            "",
            project=project,
        )

        if not results:

            st.info(
                "No long-term memories have been stored yet."
            )

        else:

            for memory in results[:30]:

                importance = memory.get(
                    "importance",
                    5,
                )

                memory_type = memory.get(
                    "memory_type",
                    "fact",
                )

                st.markdown(
                    f"**{memory_type.upper()}** "
                    f"· importance {importance}/10"
                )

                st.write(
                    memory.get("content", "")
                )

                st.divider()


def create_new_soul_forge_chat(
    project: str = "",
):

    from app.core.soul_forge_memory import (
        create_conversation,
    )

    conversation = create_conversation(
        title="New Chat",
        project=project,
    )

    st.session_state[
        "sf_active_conversation_id"
    ] = conversation["conversation_id"]

    st.session_state[
        "sf_loaded_conversation"
    ] = conversation

    return conversation

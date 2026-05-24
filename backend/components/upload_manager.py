import streamlit as st

from components.ui import (
    esc,
    render_section_header,
    render_system_notice
)
from utils.file_utils import read_uploaded_file


def render_upload_manager():

    render_section_header(
        "Sources",
        "Add TXT, PY, or MD context."
    )

    st.markdown(
        """
        <div class="helios-upload-shell helios-motion-card">
            <div class="helios-upload-icon">IN</div>
            <div>
                <h3>Source Intake</h3>
                <p>Drop a file or browse.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    scope = st.selectbox(
        "Knowledge scope",
        [
            "This chat",
            "Project",
            "Global memory"
        ],
        key="helios_source_scope",
        label_visibility="collapsed"
    )

    uploaded_file = st.file_uploader(
        label="Upload Files",
        type=[
            "txt",
            "py",
            "md"
        ],
        label_visibility="collapsed",
    )

    file_content = read_uploaded_file(
        uploaded_file
    )

    if uploaded_file:

        file_size = round(
            uploaded_file.size / 1024,
            2
        )

        extension = uploaded_file.name.split(".")[-1].upper()

        st.markdown(
            f"""
            <div class="helios-source-chip helios-motion-card source-ready">
                <span>{esc(extension)}</span>
                <div>
                    <strong>{esc(uploaded_file.name)}</strong>
                    <small>{file_size} KB • {esc(scope)}</small>
                </div>
                <em>READY</em>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.progress(
            100,
            text="Indexing complete"
        )

        action_cols = st.columns(
            2,
            gap="small"
        )

        with action_cols[0]:

            if st.button(
                "Re-index source",
                key="helios_reindex_source",
                use_container_width=True
            ):

                render_system_notice(
                    "success",
                    "Source re-index queued",
                    uploaded_file.name
                )

        with action_cols[1]:

            if st.button(
                "Remove from scope",
                key="helios_remove_source",
                use_container_width=True
            ):

                render_system_notice(
                    "warning",
                    "Source removal staged",
                    uploaded_file.name
                )

        st.markdown(
            f"""
            <section class="helios-source-library helios-motion-card">
                <div class="helios-source-library-head">
                    <strong>Source Library</strong>
                    <span>{esc(scope)}</span>
                </div>
                <div class="helios-source-row">
                    <span>{esc(extension)}</span>
                    <strong>{esc(uploaded_file.name)}</strong>
                    <em>Indexed</em>
                </div>
            </section>
            """,
            unsafe_allow_html=True
        )

    return uploaded_file, file_content

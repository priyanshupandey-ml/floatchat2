
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from langchain_chroma import Chroma
from retrive import ask_rag
from pathlib import Path
import tempfile
from Data_pipeline import process_argo_data
from profile_summary import get_new_profile_documents
from vector_store import create_vector_store

from embeddings import get_embeddings

if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

if "processing_log" not in st.session_state:
    st.session_state.processing_log = []

# ---------------- CONFIG ----------------
DB_USER = "postgres"
DB_PASSWORD = "8860"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ocean_db"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

st.set_page_config(
    page_title="FloatChat",
    layout="wide"
)

# ---------------- DATA ----------------
@st.cache_data
def load_data():
    query = """
    SELECT *
    FROM ocean_measurements
    """
    return pd.read_sql(query, engine)

@st.cache_data
def load_profile_summary():
    query = """
    SELECT *
    FROM profile_summaries
    """
    try:
        return pd.read_sql(query, engine)
    except:
        return pd.DataFrame()

# ---------------- RAG ----------------
@st.cache_resource
def load_vectorstore():
    embeddings = get_embeddings()

    return Chroma(
        collection_name="ocean_measurements",
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )


def rag_search(question):
    try:
        vectorstore = load_vectorstore()

        answer = ask_rag(
            vectorstore=vectorstore,
            question=question
        )

        return answer

    except Exception as e:
        return f"RAG error: {str(e)}"
# ---------------- SIDEBAR ----------------

#------------UPLOAD SECTION ---------------

st.sidebar.header("Data Upload")

uploaded_files = st.sidebar.file_uploader(
    "Upload ARGO NetCDF files",
    type=["nc"],
    accept_multiple_files=True
)

#------------PROCESSING SECTION ---------------

if st.sidebar.button("Process Data"):

    if not uploaded_files:
        st.warning("Please upload files.")

    else:
        
        # Create temporary folder
        temp_dir = Path(tempfile.mkdtemp())

        # Save uploaded files
        for file in uploaded_files:

            save_path = temp_dir / file.name

            with open(save_path, "wb") as f:
                f.write(file.getbuffer())
        
        status = st.empty()
        progress = st.progress(0)

        try:

            st.session_state.processing_log = []

            st.session_state.processing_log.append(
                "Uploading files..."
            )

            # save files
           
           
            # process data
            status.info("Processing ARGO measurements...")

            st.session_state.processing_log.append(
                "Processing ARGO measurements..."
            )

            process_argo_data(temp_dir)
            status.info("Generating profile summaries...")

            st.session_state.processing_log.append(
                "Generating profile summaries..."
            )
            status.info("Checking for new profiles...")

            docs = get_new_profile_documents(engine)

            st.session_state.processing_log.append(
                f"{len(docs)} new profiles found."
            )
            status.info(f"found {len(docs)} new profiles.")

            status.info("Creating embeddings...")

            if docs:

                st.session_state.processing_log.append(
                    "Creating embeddings..."
                )

                create_vector_store(
                    get_embeddings(),
                    docs
                )

                st.session_state.processing_log.append(
                    f"{len(docs)} profiles added to ChromaDB."
                )
                status.info(f"Added {len(docs)} new profiles to ChromaDB.")

            else:

                st.session_state.processing_log.append(
                    "No new profiles found."
                )
                status.info("No new profiles found.")

            st.session_state.processing_log.append(
                "System ready."
            )
            status.success("Data processing complete!")
            

            st.session_state.data_loaded = True

        except Exception as e:

            st.error(str(e))
            
if not st.session_state.data_loaded:

    st.title("FloatChat")

    st.subheader("Data Processing")

    for msg in st.session_state.processing_log:
        st.write(msg)

    st.info(
        "Upload ARGO files to begin exploration."
    )

    st.stop()
                
st.sidebar.title("FloatChat")
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Geospatial View",
        "Profile Explorer",
        "Chat Assistant",
        "ASCII Summary"
    ]
)

# ---------------- LOAD DATA ----------------
df = load_data()



# ---------------- DASHBOARD ----------------
if page == "Dashboard":

    st.title("Ocean Intelligence Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Records", len(df))

    c2.metric(
        "Floats",
        df["platform_id"].nunique()
        if len(df) else 0
    )

    c3.metric(
        "Max Depth",
        round(df["depth"].max(), 2)
        if len(df) else 0
    )

    c4.metric(
        "Avg Temp",
        round(df["temperature"].mean(), 2)
        if len(df) else 0
    )

    st.subheader("Temperature Distribution")

    fig = px.histogram(
        df,
        x="temperature",
        nbins=50
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Depth vs Temperature")

    fig2 = px.scatter(
        df.sample(min(5000, len(df))),
        x="depth",
        y="temperature"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ---------------- MAP ----------------
elif page == "Geospatial View":

    st.title("ARGO Float Locations")

    map_df = (
        df.groupby(
            ["platform_id"]
        )
        .agg(
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean")
        )
        .reset_index()
    )

    fig = px.scatter_map(
        map_df,
        lat="latitude",
        lon="longitude",
        hover_name="platform_id",
        zoom=2,
        height=700
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------- PROFILE EXPLORER ----------------
elif page == "Profile Explorer":

    st.title("NetCDF Profile Explorer")

    profiles = load_profile_summary()

    st.dataframe(
        profiles,
        use_container_width=True
    )

    if not profiles.empty:

        selected = st.selectbox(
            "Select Profile",
            profiles["profile_id"]
        )

        row = profiles[
            profiles["profile_id"] == selected
        ].iloc[0]

        st.json(row.to_dict())

# ---------------- CHAT ----------------
elif page == "Chat Assistant":

    st.title("Ocean Data Chat")

    st.markdown(
        """
        Example Questions:

        - Maximum depth observed?
        - Which float reached deepest?
        - Temperature range?
        - Show profile near latitude 10
        """
    )

    q = st.text_input(
        "Ask about your ARGO data"
    )

    if st.button("Search"):

        with st.spinner("Searching knowledge base..."):
            answer = rag_search(q)

        st.markdown("### Retrieved Context")
        st.write(answer)

# ---------------- ASCII ----------------
elif page == "ASCII Summary":

    st.title("ASCII Ocean Summary")

    summary = df.describe(
        include="all"
    )

    st.code(
        summary.to_string(),
        language="text"
    )

    st.download_button(
        "Download ASCII Report",
        summary.to_string(),
        file_name="argo_ascii_report.txt"
    )

import streamlit as st
import time
import os
import sys
import pandas as pd
import csv
import altair as alt
import base64

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from src.search_engine import SearchEngine
    from src.evaluator import Evaluator
except ImportError:
    from search_engine import SearchEngine
    from evaluator import Evaluator

# --- CONFIGURATION ---
# Custom CSS for Google-like look
st.markdown(f"""
<style>
    .stApp {{
        background-color: #fee7f0; /* Cuisse de nymphe */
    }}
    .main-header {{
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        color: #424242; /* Dark Grey for 'start your' */
        text-align: center;
        margin-bottom: 20px;
    }}
    .stTextInput > div > div > input {{
        border-radius: 24px;
        padding: 10px 20px;
        border: 1px solid #dfe1e5;
        box-shadow: 0 1px 6px rgba(32,33,36,0.28);
    }}
    .stTextInput > div > div > input:focus {{
        border-color: transparent;
        box-shadow: 0 1px 6px rgba(32,33,36,0.28);
    }}
    .result-card {{
        padding: 10px;
        border-radius: 8px;
        transition: background-color 0.2s;
    }}
    .result-card:hover {{
        background-color: rgba(255, 255, 255, 0.5); /* Lighter hover on pink */
    }}
    /* Force charts to align left */
    div[data-testid="stAltairChart"] > div {{
        width: 100% !important;
    }}
    div[data-testid="stHorizontalBlock"] > div {{
        /* Ensure columns don't force center alignment if not needed */
    }}
    /* Reduce side padding of the main block to use more screen width */
    .block-container {{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- LOADERS ---
@st.cache_resource
def load_engine():
    return SearchEngine()

@st.cache_resource
def load_evaluator():
    return Evaluator()

engine = load_engine()

# --- STATE MANAGEMENT ---
if "page" not in st.session_state:
    st.session_state.page = 1
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "results" not in st.session_state:
    st.session_state.results = []
if "relevant_docs" not in st.session_state:
    st.session_state.relevant_docs = set()
if "last_query_run" not in st.session_state:
    st.session_state.last_query_run = ""


RESULTS_PER_PAGE = 10

# --- MAIN INTERFACE ---
tab_search, tab_eval, tab_stats = st.tabs(["Recherche", "Évaluation", "Statistiques"])

with tab_search:
    # LOGO & SEARCH BAR
    # Rosewood hex: #65000B
    st.markdown('<div class="main-header">start your <span style="color: #65000B;">search</span></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        # Model Selection
        st.caption("Choisir le modèle de pertinence :")
        model_choice = st.radio(
            "Modèle", 
            ["Probabiliste (BM25)", "Vectoriel (TF-IDF)"], 
            horizontal=True, 
            label_visibility="collapsed"
        )
        model_code = 'tfidf' if 'Vectoriel' in model_choice else 'bm25'
        
        query_input = st.text_input("", placeholder="Rechercher sur le web...", label_visibility="collapsed")
        
        # Search Button (Centered)
        # Using columns to center button
        b1, b2, b3 = st.columns([2, 1, 2])
        with b2:
            search_clicked = st.button("Recherche", use_container_width=True)

    # SEARCH LOGIC
    # Trigger if button clicked OR enter pressed (query changed)
    # Also trigger if model changed? Maybe not, usually user types query then clicks.
    # But if they change model, they might expect refresh. Let's keep it simple: need to click or enter.
    if (search_clicked or query_input) and (query_input != st.session_state.last_query_run or search_clicked):
        # Allow re-run if button clicked even if query same (to apply new model)
        if query_input:
            st.session_state.search_query = query_input
            st.session_state.last_query_run = query_input
            st.session_state.page = 1
            st.session_state.results = [] # Clear previous results
            
            with st.spinner(f"Recherche en cours ({model_choice})..."):
                start_time = time.time()
                # Get more results for pagination (e.g. 50)
                st.session_state.results = engine.search(query_input, k=50, model=model_code)
                st.session_state.duration = time.time() - start_time
    
    # DISPLAY RESULTS
    if st.session_state.results:
        results = st.session_state.results
        total_results = len(results)
        
        st.markdown(f"About {total_results} results ({st.session_state.duration:.2f} seconds)")
        st.divider()

        # PAGINATION CALCULATION
        total_pages = (total_results // RESULTS_PER_PAGE) + (1 if total_results % RESULTS_PER_PAGE > 0 else 0)
        
        # Ensure page range is valid
        if st.session_state.page > total_pages: st.session_state.page = total_pages
        if st.session_state.page < 1: st.session_state.page = 1
        
        start_idx = (st.session_state.page - 1) * RESULTS_PER_PAGE
        end_idx = start_idx + RESULTS_PER_PAGE
        current_results = results[start_idx:end_idx]

        # RENDER RESULTS
        st.write(f"**Page {st.session_state.page} sur {total_pages}**")
        
        for res in current_results:
            with st.container():
                st.markdown(f"### {res['title']}")
                st.caption(f"Score: {res['score']} | {res['path']}")
                st.markdown(f"{res['snippet']}")
                
                # + Button / Expander for Full Content
                with st.expander("Voir tout l'article"):
                    # Retrieve content using doc map
                    doc_info = engine.doc_map.get(res['id'])
                    if doc_info:
                        path = os.path.join("data", "documents", doc_info["path"])
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                data = pd.read_json(f, typ='series')
                                st.write(data['content'])
                        except Exception as e:
                            st.error(f"Erreur lecture fichier: {e}")
                
                st.divider()
        
        # PAGINATION CONTROLS
        col_prev, col_pages, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.session_state.page > 1:
                if st.button("Précédent"):
                    st.session_state.page -= 1
                    st.rerun()
        
        with col_next:
            if st.session_state.page < total_pages:
                if st.button("Suivant"):
                    st.session_state.page += 1
                    st.rerun()

    # Empty State
    elif st.session_state.search_query:
        st.warning("Aucun résultat trouvé.")

with tab_eval:
    # Removed top header as requested
    
    eval_file = os.path.join("data", "evaluation_results.csv")
    curve_file = os.path.join("data", "evaluation_curve.csv")
    
    if os.path.exists(eval_file) and os.path.exists(curve_file):
        try:
            df = pd.read_csv(eval_file)
            curve_df = pd.read_csv(curve_file)
            
            # --- Global Performance Section ---
            st.markdown("<h3 style='text-align: center'>Performance Globale </h3>", unsafe_allow_html=True)
            
            # Helper to get scalar metric (if exists)
            def get_metric(m_df, metric):
                if not m_df.empty:
                    return m_df[metric].mean()
                return 0.0

            # Split data by model
            bm25_df = df[df['model'] == 'bm25']
            tfidf_df = df[df['model'] == 'tfidf']
            
            # Create comparison columns
            col_bm25, col_tfidf = st.columns(2)
            
            with col_bm25:
                st.markdown("<h4 style='text-align: center'>Probabiliste (BM25)</h4>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.metric("MAP", f"{get_metric(bm25_df, 'ap'):.4f}")
                c2.metric("MRR", f"{get_metric(bm25_df, 'rr'):.4f}")
                
            with col_tfidf:
                st.markdown("<h4 style='text-align: center'>Vectoriel (TF-IDF)</h4>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                # Show delta if possible? Streamlit metric allows delta.
                map_bm25 = get_metric(bm25_df, 'ap')
                map_tfidf = get_metric(tfidf_df, 'ap')
                mrr_bm25 = get_metric(bm25_df, 'rr')
                mrr_tfidf = get_metric(tfidf_df, 'rr')
                
                c1.metric("MAP", f"{map_tfidf:.4f}", delta=f"{map_tfidf - map_bm25:.4f}")
                c2.metric("MRR", f"{mrr_tfidf:.4f}", delta=f"{mrr_tfidf - mrr_bm25:.4f}")

            st.divider()
            
            # Global P-R Curve (Scatter + Line sorted by recall)
            st.markdown("<h3 style='text-align: center'>Courbe Précision-Rappel Globale </h3>", unsafe_allow_html=True)
            st.caption("Comparaison des modèles : BM25 (Bleu) vs TF-IDF (Rouge).")
            
            color_scale = alt.Scale(domain=['bm25', 'tfidf'], range=['#4285F4', 'red'])
            
            # Altair Chart using 'df' (summary results), not 'curve_df'
            base = alt.Chart(df).encode(
                x=alt.X('recall', title='Rappel (Recall)', scale=alt.Scale(domain=[0, 1])),
                y=alt.Y('precision', title='Précision (Precision)', scale=alt.Scale(domain=[0, 1])),
                color=alt.Color('model', title='Modèle', scale=color_scale),
                tooltip=['query', 'model', 'precision', 'recall', 'f_measure']
            )
            
            # Points for each query
            points = base.mark_circle(size=100, opacity=0.6)
            
            # Connecting line (ordered by recall to form a shape for each model)
            line = base.mark_line().encode(order='recall')
            
            st.altair_chart(points + line, use_container_width=True)
            
            st.divider()
            
            # --- Per-Query Section (Horizontal Scroll / HConcat) ---
            st.markdown("<h3 style='text-align: center'>Détails par Requête </h3>", unsafe_allow_html=True)
            
            unique_queries = df['query'].unique()
            charts = []
            
            for query_text in unique_queries:
                q_curve = curve_df[curve_df['query'] == query_text]
                if not q_curve.empty:
                    # Individual Chart
                    c = alt.Chart(q_curve, title=query_text).mark_line(point=True).encode(
                        x=alt.X('recall', title='Rappel'),
                        y=alt.Y('precision', title='Précision'),
                        color=alt.Color('model', scale=color_scale, legend=None), # No legend per chart to save space
                        tooltip=['model', 'precision', 'recall', 'rank']
                    ).properties(
                        width=300, # Fixed width to force scrolling if many
                        height=300
                    )
                    charts.append(c)
            
            if charts:
                # Horizontal Concatenation
                hchart = alt.hconcat(*charts).resolve_scale(color='shared')
                # use_container_width=False allows it to extend beyond container and trigger scroll
                st.altair_chart(hchart, use_container_width=False) 
            else:
                st.warning("Aucune donnée pour les graphiques détaillés.")

            st.divider()

            # Raw Data Expander
            with st.expander("Voir les données brutes"):
                st.write("Résultats Principaux")
                st.dataframe(df)
                st.write("Données de Courbe")
                st.dataframe(curve_df)
            
        except Exception as e:
            st.error(f"Erreur lors de la lecture des fichiers de résultats: {e}")
    else:
        st.warning("Fichiers de résultats introuvables. Veuillez exécuter 'src/evaluator.py'.")

with tab_stats:
    st.header("Statistiques du Moteur")
    if engine and hasattr(engine, 'stats') and engine.stats:
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.metric("Documents Indexés", engine.stats.get("total_docs", 0))
        with c2: 
            st.metric("Taille Index", f"{len(engine.inverted_index)} termes")
        with c3: 
            st.metric("Mots / Doc (Moy.)", f"{engine.stats.get('avg_doc_length', 0):.1f}")
    else:
        st.info("Statistiques non disponibles (Index vide ou non chargé).")

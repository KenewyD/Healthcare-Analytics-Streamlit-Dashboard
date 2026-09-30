# ============================================================
# utils.py
# DIM Insight — Hospital Data Intelligence Platform
# ============================================================

import base64
from datetime import timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# CONSTANTES
# ============================================================

DATA_PATH = Path("data/Healthcare Analysis Dataset.csv")
CLUSTER_PATH = Path("data/clustered_patients.csv")
CSS_PATH = Path("assets/styles.css")
LOGO_PATH = Path("assets/images/logo.png")


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data(show_spinner=False)
def load_data():
    """
    Charge le jeu de données principal.

    Les données sont mises en cache afin d'éviter de relire
    et retraiter le CSV à chaque interaction Streamlit.
    """

    df = pd.read_csv(
        DATA_PATH,
        parse_dates=[
            "Date of Admission",
            "Discharge Date"
        ]
    )

    # Durée du séjour
    df["Length of Stay"] = (
        df["Discharge Date"] - df["Date of Admission"]
    ).dt.days

    # Variables temporelles
    df["Year"] = (
        df["Date of Admission"]
        .dt.year
        .astype("int16")
    )

    df["Month"] = (
        df["Date of Admission"]
        .dt.month
        .astype("int8")
    )

    df["Quarter"] = (
        df["Date of Admission"]
        .dt.quarter
        .astype("int8")
    )

    # Réduction de l'utilisation mémoire
    categorical_columns = [
        "Hospital",
        "Gender",
        "Admission Type",
        "Insurance Provider",
        "Test Results",
        "Blood Type",
        "Medical Condition",
        "Medication"
    ]

    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df


@st.cache_data(show_spinner=False)
def load_clusters():
    """
    Charge les données utilisées pour les analyses de clustering.
    """

    df = pd.read_csv(
        CLUSTER_PATH,
        parse_dates=[
            "Date of Admission",
            "Discharge Date"
        ]
    )

    df["Length of Stay"] = (
        df["Discharge Date"] - df["Date of Admission"]
    ).dt.days

    df["Year"] = (
        df["Date of Admission"]
        .dt.year
        .astype("int16")
    )

    if "Cluster" in df.columns:

        # Clusters 0-5 -> 1-6
        df["Cluster"] = df["Cluster"] + 1

        df["Cluster"] = (
            "Cluster "
            + df["Cluster"].astype(str)
        )

    return df


# ============================================================
# RESSOURCES / ASSETS
# ============================================================

@st.cache_data(show_spinner=False)
def img_to_base64(img_path):
    """
    Convertit une image en Base64.
    Le résultat est mis en cache.
    """

    path = Path(img_path)

    if not path.exists():
        return ""

    with open(path, "rb") as img_file:
        return base64.b64encode(
            img_file.read()
        ).decode()


@st.cache_data(show_spinner=False)
def load_css():
    """
    Charge le fichier CSS de l'application.
    """

    if not CSS_PATH.exists():
        return ""

    with open(
        CSS_PATH,
        "r",
        encoding="utf-8"
    ) as css_file:

        return css_file.read()


# ============================================================
# INITIALISATION DE L'APPLICATION
# ============================================================

def initialize_page():
    """
    Initialise la configuration Streamlit et charge le CSS.
    """

    st.set_page_config(
        page_title="DIM Insight | Hospital Data Intelligence",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    css = load_css()

    if css:
        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )


# ============================================================
# AIDE
# ============================================================

def toggle_help_state():
    """
    Ferme la section d'aide.
    """

    st.session_state["show_help"] = False


# ============================================================
# NAVIGATION
# ============================================================

def create_page_navigation():
    """
    Navigation horizontale de l'application.

    Les URLs originales sont conservées afin de rester
    compatibles avec les fichiers présents dans pages/.
    """

    current_page = st.session_state.get(
        "current_page",
        "Executive Summary"
    )

    st.markdown(
        f"""
        <div class="stTabs">
            <div data-baseweb="tab-list">

                <a
                    target="_self"
                    href="/"
                    class="nav-link"
                    data-active="{
                        'true'
                        if current_page == 'Executive Summary'
                        else 'false'
                    }"
                >
                    Synthèse DIM
                </a>

                <a
                    target="_self"
                    href="/Patient_Demographics"
                    class="nav-link"
                    data-active="{
                        'true'
                        if current_page == 'Patient Demographics'
                        else 'false'
                    }"
                >
                    Population patients
                </a>

                <a
                    target="_self"
                    href="/Hospital_Performance"
                    class="nav-link"
                    data-active="{
                        'true'
                        if current_page == 'Hospital Performance'
                        else 'false'
                    }"
                >
                    Performance hospitalière
                </a>

                <a
                    target="_self"
                    href="/Insurance_&_Billing"
                    class="nav-link"
                    data-active="{
                        'true'
                        if current_page == 'Insurance & Billing'
                        else 'false'
                    }"
                >
                    Analyse médico-économique
                </a>

                <a
                    target="_self"
                    href="/Trends_&_Forecasting"
                    class="nav-link"
                    data-active="{
                        'true'
                        if current_page == 'Trends & Forecasting'
                        else 'false'
                    }"
                >
                    Tendances & prévisions
                </a>

            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # AIDE UTILISATEUR
    # ========================================================

    if st.session_state.get(
        "show_help",
        False
    ):

        with st.container(
            key="help-container"
        ):

            help_header = st.container(
                key="help_head"
            )

            help_cols = help_header.columns(
                [10, 1]
            )

            help_cols[0].markdown(
                """
                <h3 class="help-title">
                    Aide & informations
                </h3>
                """,
                unsafe_allow_html=True
            )

            help_cols[1].button(
                "",
                key="close_help",
                icon=":material/close:",
                help="Fermer",
                use_container_width=True,
                on_click=toggle_help_state
            )

            st.markdown(
                """
                <div class="help-container">

                    <div
                        class="help-section"
                        style="margin-top:20px;"
                    >

                        <h3>
                            Utilisation de DIM Insight
                        </h3>

                        <p>
                            Cette plateforme démonstratrice
                            permet d'explorer des données
                            hospitalières synthétiques.
                        </p>

                        <ul>
                            <li>
                                Utilisez les filtres de la
                                barre latérale.
                            </li>

                            <li>
                                Naviguez entre les différents
                                modules avec les onglets.
                            </li>

                            <li>
                                Survolez les graphiques pour
                                afficher davantage d'informations.
                            </li>

                            <li>
                                Comparez différentes périodes
                                d'activité hospitalière.
                            </li>
                        </ul>

                    </div>


                    <div class="help-section">

                        <h3>
                            Périodes disponibles
                        </h3>

                        <ul>

                            <li>
                                <strong>Dernier mois :</strong>
                                comparaison avec le mois précédent.
                            </li>

                            <li>
                                <strong>Dernier trimestre :</strong>
                                comparaison avec le trimestre précédent.
                            </li>

                            <li>
                                <strong>Dernière année :</strong>
                                comparaison avec l'année précédente.
                            </li>

                            <li>
                                <strong>Personnalisée :</strong>
                                choix libre des dates.
                            </li>

                        </ul>

                    </div>


                    <div class="help-section">

                        <h3>
                            Filtre établissement
                        </h3>

                        <p>
                            Sélectionnez un ou plusieurs
                            établissements afin de limiter
                            l'analyse.
                        </p>

                        <p>
                            Si aucun établissement n'est
                            sélectionné, toutes les données
                            sont utilisées.
                        </p>

                    </div>


                    <div class="help-section">

                        <h3>
                            Modules
                        </h3>

                        <div class="page-specific">

                            <p>
                                <b>Synthèse DIM :</b>
                                principaux indicateurs
                                d'activité hospitalière.
                            </p>

                            <p>
                                <b>Population patients :</b>
                                analyses démographiques
                                et cliniques.
                            </p>

                            <p>
                                <b>Performance hospitalière :</b>
                                analyse des durées de séjour,
                                volumes et performances.
                            </p>

                            <p>
                                <b>Analyse médico-économique :</b>
                                coûts simulés, organismes
                                payeurs et segmentation.
                            </p>

                            <p>
                                <b>Tendances & prévisions :</b>
                                évolution temporelle et
                                projections d'activité.
                            </p>

                        </div>

                    </div>


                    <div class="attribution">

                        <p>
                            <strong>
                                DIM Insight —
                                Hospital Data Intelligence Platform
                            </strong>
                            <br>

                            Projet démonstrateur utilisant
                            uniquement des données synthétiques.

                            <br><br>

                            Application adaptée à partir d'un
                            projet open-source créé initialement
                            pour le Data DNA April 2025 Challenge.
                            Les crédits et la licence du projet
                            source sont conservés conformément
                            aux conditions du dépôt d'origine.

                        </p>

                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# GESTION DES PÉRIODES
# ============================================================

def process_date_ranges(
    scenario,
    max_date
):
    """
    Calcule les périodes d'analyse et de comparaison.
    """

    max_date = pd.Timestamp(max_date)

    prev_custom_start = None
    prev_start = None
    prev_end = None

    # ========================================================
    # DERNIER MOIS
    # ========================================================

    if scenario == "Last Month":

        current_start = max_date.replace(
            day=1
        )

        current_end = max_date

        # Premier jour du mois précédent
        prev_start = (
            current_start
            - pd.DateOffset(months=1)
        )

        # Même progression dans le mois précédent
        day_number = current_end.day

        previous_month_last_day = (
            current_start
            - pd.Timedelta(days=1)
        )

        previous_day = min(
            day_number,
            previous_month_last_day.day
        )

        prev_end = prev_start.replace(
            day=previous_day
        )

        comparison_label = "vs mois précédent"

    # ========================================================
    # DERNIER TRIMESTRE
    # ========================================================

    elif scenario == "Last Quarter":

        current_quarter = (
            (max_date.month - 1) // 3
        ) + 1

        quarter_start_month = (
            (current_quarter - 1) * 3
        ) + 1

        current_start = pd.Timestamp(
            year=max_date.year,
            month=quarter_start_month,
            day=1
        )

        current_end = max_date

        days_into_quarter = (
            current_end - current_start
        ).days

        prev_start = (
            current_start
            - pd.DateOffset(months=3)
        )

        prev_end = (
            prev_start
            + pd.Timedelta(
                days=days_into_quarter
            )
        )

        comparison_label = "vs trimestre précédent"

    # ========================================================
    # DERNIÈRE ANNÉE
    # ========================================================

    elif scenario == "Last Year":

        current_start = pd.Timestamp(
            year=max_date.year,
            month=1,
            day=1
        )

        current_end = max_date

        prev_start = pd.Timestamp(
            year=max_date.year - 1,
            month=1,
            day=1
        )

        # Même date approximative année précédente.
        # Gestion automatique du 29 février.
        try:

            prev_end = max_date.replace(
                year=max_date.year - 1
            )

        except ValueError:

            # Cas du 29 février
            prev_end = pd.Timestamp(
                year=max_date.year - 1,
                month=2,
                day=28
            )

        comparison_label = "vs année précédente"

    # ========================================================
    # PERSONNALISÉ
    # ========================================================

    else:

        min_data_date = (
            max_date
            - pd.DateOffset(years=5)
        ).date()

        default_start = (
            max_date
            - timedelta(days=180)
        ).date()

        date_range = st.sidebar.date_input(
            "Sélectionner une période",
            value=(
                default_start,
                max_date.date()
            ),
            min_value=min_data_date,
            max_value=max_date.date(),
            key="custom_date_range"
        )

        if isinstance(
            date_range,
            (list, tuple)
        ) and len(date_range) == 2:

            current_start = pd.Timestamp(
                date_range[0]
            )

            current_end = pd.Timestamp(
                date_range[1]
            )

            prev_custom_start = (
                current_start
            )

            comparison_label = ""

        else:

            st.sidebar.warning(
                "Sélectionnez une date de début "
                "et une date de fin."
            )

            current_start = (
                max_date
                - timedelta(days=30)
            )

            current_end = max_date

            comparison_label = ""

    # ========================================================
    # AFFICHAGE DES DATES
    # ========================================================

    st.sidebar.markdown(
        f"""
        <div class="simpleTextFirst">

            <p>
                Période analysée :
            </p>

            <p class="textBlak">
                {current_start.strftime('%d/%m/%Y')}
                -
                {current_end.strftime('%d/%m/%Y')}
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    if (
        prev_start is not None
        and prev_end is not None
    ):

        st.sidebar.markdown(
            f"""
            <div class="simpleText">

                <p>
                    Comparaison :
                </p>

                <p class="textBlak">
                    {prev_start.strftime('%d/%m/%Y')}
                    -
                    {prev_end.strftime('%d/%m/%Y')}
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.sidebar.markdown(
        """
        <hr
            style="
                margin-top:35px;
                margin-bottom:35px;
            "
        >
        """,
        unsafe_allow_html=True
    )

    return (
        current_start,
        current_end,
        prev_start,
        prev_end,
        comparison_label,
        prev_custom_start
    )


# ============================================================
# SIDEBAR
# ============================================================

def create_sidebar(df):
    """
    Construit les filtres principaux de la sidebar.
    """

    # ========================================================
    # LOGO
    # ========================================================

    logo_base64 = img_to_base64(
        LOGO_PATH
    )

    if logo_base64:

        st.sidebar.markdown(
            f"""
            <div
                style="
                    display:flex;
                    justify-content:center;
                    margin-bottom:10px;
                "
            >

                <img
                    src="data:image/png;base64,{logo_base64}"
                    width="42"
                >

            </div>
            """,
            unsafe_allow_html=True
        )

    # ========================================================
    # TITRE
    # ========================================================

    st.sidebar.markdown(
        """
        <div class="sidebar-header">
            DIM Insight
        </div>

        <div
            style="
                text-align:center;
                font-size:12px;
                opacity:0.70;
                margin-top:-8px;
                margin-bottom:18px;
            "
        >
            Hospital Data Intelligence
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        "<hr>",
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <div class="sidebar-section-title">
            Filtres
        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # PÉRIODE
    # ========================================================

    scenario_translation = {
        "Last Month": "Dernier mois",
        "Last Quarter": "Dernier trimestre",
        "Last Year": "Dernière année",
        "Custom": "Période personnalisée"
    }

    scenario = st.sidebar.selectbox(
        "Période :",
        options=[
            "Last Month",
            "Last Quarter",
            "Last Year",
            "Custom"
        ],
        index=0,
        format_func=lambda x: scenario_translation[x],
        key="time_period_selector"
    )

    # ========================================================
    # ÉTABLISSEMENTS
    # ========================================================

    if "Hospital" in df.columns:

        hospitals = sorted(
            df["Hospital"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_hospitals = (
            st.sidebar.multiselect(
                "Établissement(s) :",
                options=hospitals,
                default=[],
                placeholder="Tous les établissements",
                key="hospital_selector"
            )
        )

    else:

        selected_hospitals = []

    # ========================================================
    # FILTRAGE ÉTABLISSEMENT
    # ========================================================

    if selected_hospitals:

        filtered_df = df[
            df["Hospital"]
            .astype(str)
            .isin(selected_hospitals)
        ]

    else:

        filtered_df = df

    # ========================================================
    # PAGE COURANTE
    # ========================================================

    current_page = (
        st.session_state.get(
            "current_page",
            "Executive Summary"
        )
    )

    # ========================================================
    # DATE MAXIMUM
    # ========================================================

    max_date = (
        filtered_df[
            "Date of Admission"
        ].max()
    )

    if pd.isna(max_date):

        max_date = (
            df["Date of Admission"]
            .max()
        )

    # Pour la page des prévisions,
    # éviter d'utiliser un mois trop incomplet.
    if current_page == "Trends & Forecasting":

        if max_date.day < 25:

            first_day_current_month = (
                max_date.replace(day=1)
            )

            max_date = (
                first_day_current_month
                - pd.Timedelta(days=1)
            )

    # ========================================================
    # TRAITEMENT DES PÉRIODES
    # ========================================================

    (
        current_start,
        current_end,
        prev_start,
        prev_end,
        comparison_label,
        prev_custom_start
    ) = process_date_ranges(
        scenario,
        max_date
    )

    # ========================================================
    # BLOC AIDE
    # ========================================================

    help_container = st.sidebar.container(
        key="helpBlock"
    )

    help_cols = help_container.columns(
        [3, 1]
    )

    help_cols[0].markdown(
        """
        <p
            style="
                margin-top:7px;
                margin-bottom:0;
            "
        >
            Informations :
        </p>
        """,
        unsafe_allow_html=True
    )

    if help_cols[1].button(
        "",
        key="help_button",
        icon=":material/help:",
        help="Afficher l'aide",
        use_container_width=False
    ):

        st.session_state["show_help"] = (
            not st.session_state.get(
                "show_help",
                False
            )
        )

    # ========================================================
    # RETOUR
    # ========================================================

    return (
        current_start,
        current_end,
        prev_start,
        prev_end,
        comparison_label,
        prev_custom_start,
        filtered_df
    )

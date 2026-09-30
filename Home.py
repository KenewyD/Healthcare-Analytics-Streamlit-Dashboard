import streamlit as st
from utils import (
    initialize_page,
    load_data,
    create_sidebar,
    create_page_navigation
)

# ============================================================
# INITIALISATION
# ============================================================

initialize_page()

try:
    # ========================================================
    # CHARGEMENT DES DONNÉES
    # ========================================================

    df = load_data()

    if df is None or df.empty:
        st.warning("Aucune donnée disponible.")
        st.stop()

    # ========================================================
    # SIDEBAR + NAVIGATION
    # ========================================================

    (
        current_start,
        current_end,
        prev_start,
        prev_end,
        comparison_label,
        prev_custom_start,
        filtered_df
    ) = create_sidebar(df)

    create_page_navigation()

    if filtered_df is None or filtered_df.empty:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
        st.stop()

    # ========================================================
    # FILTRAGE DES PÉRIODES
    # ========================================================

    current_mask = (
        (filtered_df["Date of Admission"] >= current_start)
        & (filtered_df["Date of Admission"] <= current_end)
    )

    df_current = filtered_df.loc[current_mask]

    if prev_start is not None and prev_end is not None:
        previous_mask = (
            (filtered_df["Date of Admission"] >= prev_start)
            & (filtered_df["Date of Admission"] <= prev_end)
        )

        df_prev = filtered_df.loc[previous_mask]

        if df_prev.empty:
            df_prev = None
    else:
        df_prev = None

    # ========================================================
    # SESSION STATE
    # ========================================================

    st.session_state["current_page"] = "Synthèse DIM"
    st.session_state["df_current"] = df_current
    st.session_state["df_prev"] = df_prev
    st.session_state["comparison_label"] = comparison_label

    # ========================================================
    # EN-TÊTE
    # ========================================================

    st.markdown(
        """
        <div style="
            padding: 18px 22px;
            border-radius: 14px;
            margin-bottom: 20px;
            background: rgba(120,120,120,0.08);
        ">
            <h1 style="margin-bottom:5px;">
                DIM Insight
            </h1>

            <h4 style="margin-top:0;">
                Hospital Data Intelligence Platform
            </h4>

            <p>
                Plateforme démonstratrice de pilotage hospitalier,
                d'analyse des séjours et de contrôle de la qualité
                des données médicales.
            </p>

            <p style="font-size:13px; opacity:0.75;">
                Projet démonstrateur – données entièrement synthétiques.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df_current.empty:
        st.warning(
            "Aucun séjour n'est disponible pour la période sélectionnée."
        )
        st.stop()

    # ========================================================
    # CALCUL DES INDICATEURS
    # ========================================================

    total_patients = len(df_current)

    avg_length_of_stay = (
        df_current["Length of Stay"].mean()
        if "Length of Stay" in df_current.columns
        else 0
    )

    avg_treatment_cost = (
        df_current["Billing Amount"].mean()
        if "Billing Amount" in df_current.columns
        else 0
    )

    elective_admission_pct = (
        df_current["Admission Type"]
        .eq("Elective")
        .mean()
        * 100
        if "Admission Type" in df_current.columns
        else 0
    )

    inconclusive_pct = (
        df_current["Test Results"]
        .eq("Inconclusive")
        .mean()
        * 100
        if "Test Results" in df_current.columns
        else 0
    )

    # ========================================================
    # COMPARAISON AVEC LA PÉRIODE PRÉCÉDENTE
    # ========================================================

    prev_avg_los = None
    prev_avg_cost = None
    prev_elective_pct = None
    prev_inconclusive_pct = None

    los_change = 0
    cost_change = 0
    elective_change = 0
    inconclusive_change = 0

    if df_prev is not None and not df_prev.empty:

        prev_avg_los = df_prev["Length of Stay"].mean()

        prev_avg_cost = df_prev["Billing Amount"].mean()

        prev_elective_pct = (
            df_prev["Admission Type"]
            .eq("Elective")
            .mean()
            * 100
        )

        prev_inconclusive_pct = (
            df_prev["Test Results"]
            .eq("Inconclusive")
            .mean()
            * 100
        )

        if prev_avg_los and prev_avg_los > 0:
            los_change = (
                (avg_length_of_stay / prev_avg_los) - 1
            ) * 100

        if prev_avg_cost and prev_avg_cost > 0:
            cost_change = (
                (avg_treatment_cost / prev_avg_cost) - 1
            ) * 100

        elective_change = (
            elective_admission_pct
            - prev_elective_pct
        )

        inconclusive_change = (
            inconclusive_pct
            - prev_inconclusive_pct
        )

    # ========================================================
    # KPIs
    # ========================================================

    st.markdown(
        '<h3 class="sub">Indicateurs principaux</h3>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Durée moyenne de séjour",
            value=f"{avg_length_of_stay:.1f} jours",
            delta=(
                f"{los_change:+.1f}%"
                if prev_avg_los is not None
                else None
            )
        )

    with col2:
        st.metric(
            label="Admissions programmées",
            value=f"{elective_admission_pct:.1f}%",
            delta=(
                f"{elective_change:+.1f} pts"
                if prev_elective_pct is not None
                else None
            )
        )

    with col3:
        st.metric(
            label="Coût moyen simulé",
            value=f"{avg_treatment_cost:,.0f} €",
            delta=(
                f"{cost_change:+.1f}%"
                if prev_avg_cost is not None
                else None
            ),
            delta_color="inverse"
        )

    with col4:
        st.metric(
            label="Résultats non conclusifs",
            value=f"{inconclusive_pct:.1f}%",
            delta=(
                f"{inconclusive_change:+.1f} pts"
                if prev_inconclusive_pct is not None
                else None
            ),
            delta_color="inverse"
        )

    # ========================================================
    # VOLUME D'ACTIVITÉ
    # ========================================================

    st.markdown("---")

    st.markdown(
        f"""
        ### Activité hospitalière

        **{total_patients:,} séjours / dossiers analysés**
        """
    )

    # ========================================================
    # RÉPARTITION PAR ORGANISME / ASSURANCE
    # ========================================================

    if "Insurance Provider" in df_current.columns:

        st.markdown(
            "#### Répartition par organisme payeur"
        )

        insurance_counts = (
            df_current["Insurance Provider"]
            .value_counts()
            .head(5)
        )

        prev_insurance_counts = (
            df_prev["Insurance Provider"].value_counts()
            if df_prev is not None
            and "Insurance Provider" in df_prev.columns
            else None
        )

        number_of_columns = min(
            len(insurance_counts),
            5
        )

        if number_of_columns > 0:

            ins_cols = st.columns(number_of_columns)

            for idx, (provider, count) in enumerate(
                insurance_counts.items()
            ):

                previous_value = None
                change_pct = None

                if (
                    prev_insurance_counts is not None
                    and provider in prev_insurance_counts.index
                ):
                    previous_value = (
                        prev_insurance_counts[provider]
                    )

                    if previous_value > 0:
                        change_pct = (
                            (count / previous_value) - 1
                        ) * 100

                with ins_cols[idx]:

                    st.metric(
                        label=str(provider),
                        value=f"{count:,}",
                        delta=(
                            f"{change_pct:+.1f}%"
                            if change_pct is not None
                            else None
                        )
                    )

    # ========================================================
    # NOTE SUR LES DONNÉES
    # ========================================================

    st.caption(
        "Les informations affichées dans cette application "
        "sont issues de données synthétiques et servent "
        "uniquement à démontrer des méthodes d'analyse "
        "et de pilotage hospitalier."
    )

except Exception as e:
    st.error(
        f"Une erreur est survenue lors du chargement "
        f"de l'application : {e}"
    )
    st.stop()

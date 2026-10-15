import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from auth import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    authenticate_user,
    register_user,
)


st.set_page_config(
    page_title="DataClean Mobile",
    layout="centered"
)


st.markdown(
    """
    <style>

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(
            135deg,
            #f5f7fa,
            #c3cfe2
        );
        color: #333333;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
    }

    .stButton > button {
        background-color: #4a90e2;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #357ABD;
        color: white;
    }

    [data-testid="stFormSubmitButton"] > button {
        width: 100%;
        background: linear-gradient(
            135deg,
            #4a90e2,
            #357ABD
        );
        border-radius: 10px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


if "df" not in st.session_state:
    st.session_state.df = None

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = None



if not st.session_state.authenticated:

    st.title("DataClean Mobile")

    st.subheader("Sign in or create an account")

    login_tab, register_tab = st.tabs(
        ["Login", "Register"]
    )

    # ==================================================
    # LOGIN
    # ==================================================

    with login_tab:

        with st.form("login_form"):

            username = st.text_input(
                "Username",
                placeholder="Enter your username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            submitted = st.form_submit_button(
                "Login"
            )

            if submitted:

                username = username.strip()

                if not username or not password:

                    st.error(
                        "Please enter username and password."
                    )

                else:

                    try:

                        login_success = authenticate_user(
                            username,
                            password
                        )

                        if login_success:

                            st.session_state.authenticated = True

                            st.session_state.username = (
                                username.lower()
                            )

                            st.session_state.df = None

                            st.success(
                                "Login successful!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Invalid username or password."
                            )

                    except Exception as error:

                        st.error(
                            f"Database error: {error}"
                        )


    # ==================================================
    # REGISTER
    # ==================================================

    with register_tab:

        st.caption(
            "Username must contain 3-32 letters, "
            "numbers, or underscores. "
            f"Password must be "
            f"{PASSWORD_MIN_LENGTH}-"
            f"{PASSWORD_MAX_LENGTH} characters."
        )

        with st.form("register_form"):

            new_username = st.text_input(
                "Username",
                placeholder="Choose a username"
            )

            new_password = st.text_input(
                "Password",
                type="password",
                placeholder="Choose a password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                placeholder="Enter your password again"
            )

            submitted = st.form_submit_button(
                "Create account"
            )

            if submitted:

                new_username = new_username.strip()

                if not new_username:

                    st.error(
                        "Please enter a username."
                    )

                elif not new_password:

                    st.error(
                        "Please enter a password."
                    )

                elif new_password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    try:

                        created = register_user(
                            new_username,
                            new_password
                        )

                        if created:

                            st.session_state.authenticated = True

                            st.session_state.username = (
                                new_username.lower()
                            )

                            st.session_state.df = None

                            st.success(
                                "Account created successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "That username is already registered."
                            )

                    except ValueError as error:

                        st.error(str(error))

                    except Exception as error:

                        st.error(
                            f"Database error: {error}"
                        )

    st.stop()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Navigation")

st.sidebar.caption(
    f"Signed in as {st.session_state.username}"
)


if st.sidebar.button("Logout"):

    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.df = None

    st.rerun()


page = st.sidebar.radio(
    "Go to:",
    [
        "1. Home",
        "2. Upload Data",
        "3. Clean Data",
        "4. Statistics",
        "5. Visualize"
    ]
)


# --------------------------------------------------
# PAGE 1: HOME
# --------------------------------------------------

if page == "1. Home":

    st.title("DataClean Mobile")

    st.subheader(
        "Your Mobile Data Assistant"
    )

    st.write(
        "Upload messy datasets, clean automatically, "
        "view statistics, and create interactive charts."
    )

    st.info(
        "Use sidebar navigation to start."
    )


# --------------------------------------------------
# PAGE 2: UPLOAD DATA
# --------------------------------------------------

elif page == "2. Upload Data":

    st.header("Upload CSV")

    file = st.file_uploader(
        "Choose CSV file",
        type="csv"
    )

    if file:

        with st.spinner("Loading..."):

            st.session_state.df = pd.read_csv(
                file
            )

        st.success(
            "Data Loaded!"
        )

        st.dataframe(
            st.session_state.df.head(10)
        )


# --------------------------------------------------
# PAGE 3: CLEAN DATA
# --------------------------------------------------

elif page == "3. Clean Data":

    st.header("Data Cleaning")

    if st.session_state.df is not None:

        df = st.session_state.df

        col1, col2 = st.columns(2)

        # Remove duplicates
        with col1:

            if st.button(
                "Remove Duplicates"
            ):

                before = len(df)

                df = df.drop_duplicates()

                after = len(df)

                st.session_state.df = df

                removed = before - after

                st.success(
                    f"{removed} duplicate rows removed!"
                )


        # Fill missing values
        with col2:

            if st.button(
                "Fill Missing Values"
            ):

                for col in df.select_dtypes(
                    include=["number"]
                ).columns:

                    df[col] = df[col].fillna(
                        df[col].mean()
                    )

                st.session_state.df = df

                st.success(
                    "Missing numeric values filled!"
                )


        st.subheader(
            "Cleaned Data Preview"
        )

        st.dataframe(
            st.session_state.df.head()
        )

        st.download_button(
            "Export CSV",
            st.session_state.df.to_csv(
                index=False
            ),
            "cleaned_data.csv",
            "text/csv"
        )

    else:

        st.warning(
            "⚠️ Upload data first."
        )


# --------------------------------------------------
# PAGE 4: STATISTICS
# --------------------------------------------------

elif page == "4. Statistics":

    st.header("Data Summary")

    if st.session_state.df is not None:

        st.dataframe(
            st.session_state.df.describe().T
        )

    else:

        st.warning(
            "⚠️ Upload data first."
        )


# --------------------------------------------------
# PAGE 5: VISUALIZE
# --------------------------------------------------

elif page == "5. Visualize":

    st.header("📈 Interactive Charts")

    if st.session_state.df is not None:

        df = st.session_state.df

        num_cols = (
            df.select_dtypes(
                include=["number"]
            )
            .columns
            .tolist()
        )

        cat_cols = (
            df.select_dtypes(
                include=["object"]
            )
            .columns
            .tolist()
        )

        all_cols = num_cols + cat_cols

        if not all_cols:

            st.error(
                "No columns available for visualization."
            )

        else:

            col1, col2 = st.columns(2)

            chart_type = col1.selectbox(
                "Chart Type:",
                [
                    "Boxplot",
                    "Scatter",
                    "Bar",
                    "Histogram",
                    "Heatmap"
                ]
            )

            x_col = col2.selectbox(
                "X Column:",
                all_cols
            )

            y_col = None

            if chart_type == "Scatter":

                if not num_cols:

                    st.error(
                        "Scatter plot needs numeric columns."
                    )

                    st.stop()

                y_col = st.selectbox(
                    "Y Column:",
                    num_cols
                )

            elif chart_type == "Boxplot":

                if not num_cols:

                    st.error(
                        "Boxplot needs numeric columns."
                    )

                    st.stop()

                y_col = st.selectbox(
                    "Y Column:",
                    num_cols
                )

            elif chart_type == "Bar":

                y_col = st.selectbox(
                    "Y Column:",
                    all_cols
                )

            try:

                if chart_type == "Boxplot":

                    fig = px.box(
                        df,
                        x=x_col,
                        y=y_col,
                        title=f"Box Plot: {y_col} by {x_col}"
                    )

                elif chart_type == "Scatter":

                    fig = px.scatter(
                        df,
                        x=x_col,
                        y=y_col,
                        title=f"Scatter: {x_col} vs {y_col}"
                    )

                elif chart_type == "Bar":

                    fig = px.bar(
                        df,
                        x=x_col,
                        y=y_col,
                        title=f"Bar: {y_col} by {x_col}"
                    )

                elif chart_type == "Histogram":

                    fig = px.histogram(
                        df,
                        x=x_col,
                        title=f"Histogram: {x_col}"
                    )

                elif chart_type == "Heatmap":

                    if len(num_cols) < 2:

                        st.error(
                            "Need at least 2 numeric columns."
                        )

                        st.stop()

                    corr_df = df[
                        num_cols
                    ].corr()

                    annotations = [
                        {
                            "x": column,
                            "y": row,
                            "text": (
                                f"{corr_df.loc[row, column]:.2f}"
                                if pd.notna(corr_df.loc[row, column])
                                else ""
                            ),
                            "showarrow": False
                        }
                        for row in corr_df.index
                        for column in corr_df.columns
                    ]

                    fig = go.Figure(
                        data=go.Heatmap(
                            z=corr_df.to_numpy(),
                            x=corr_df.columns,
                            y=corr_df.index,
                            colorscale="RdYlGn",
                            zmin=-1,
                            zmax=1,
                            colorbar={"title": "Correlation"},
                            hovertemplate=(
                                "%{y} / %{x}: %{z:.2f}<extra></extra>"
                            )
                        )
                    )

                    fig.update_layout(
                        title="Correlation Heatmap",
                        annotations=annotations
                    )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                # Download chart as PNG
                try:

                    img_bytes = pio.to_image(
                        fig,
                        format="png"
                    )

                    st.download_button(
                        "💾 Download PNG",
                        img_bytes,
                        f"{chart_type.lower()}.png",
                        "image/png"
                    )

                except Exception:

                    st.info(
                        "PNG export requires Kaleido."
                    )

            except Exception as error:

                st.error(
                    f"Chart error: {error}"
                )

    else:

        st.warning(
            "⚠️ Upload data first."
        )
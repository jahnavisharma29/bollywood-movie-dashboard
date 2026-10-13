import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Bollywood Movie Dashboard", page_icon="🎬", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "bollywood_movies.csv"

# Words used to auto-detect which CSV column is which. Fix any wrong guess in the sidebar.
GUESSES = {
    "title": ["title", "movie", "movie_name", "film", "name"],
    "year": ["year", "release_year", "release_date", "released", "date"],
    "genre": ["genre", "genres", "category"],
    "director": ["director", "directors"],
    "gross": ["box_office_gross", "box_office", "boxoffice", "gross", "worldwide", "revenue", "collection"],
    "rating": ["rating", "imdb_rating", "imdb", "score", "vote_average"],
}
LABELS = {
    "title": "Movie title",
    "year": "Release year / date",
    "genre": "Genre(s)",
    "director": "Director(s)",
    "gross": "Box office gross",
    "rating": "Rating",
}


def guess_column(columns, keys):
    norm = {c: re.sub(r"[^a-z0-9]+", "_", str(c).lower()).strip("_") for c in columns}
    for k in keys:  # exact matches first
        for c, n in norm.items():
            if n == k:
                return c
    for k in keys:  # then partial matches
        for c, n in norm.items():
            if k in n:
                return c
    return None


@st.cache_data
def load_csv(source):
    return pd.read_csv(source)


def split_multi(value):
    parts = re.split(r"\s*[,|/;]\s*", str(value))
    return [p.strip() for p in parts if p.strip() and p.strip().lower() != "nan"]


# ---------- Load data ----------
st.title("🎬 Bollywood Movie Dashboard")

if DATA_PATH.exists():
    raw = load_csv(DATA_PATH)
else:
    st.warning(f"Could not find {DATA_PATH.name} in the data/ folder. Upload your CSV to continue.")
    upload = st.file_uploader("Upload bollywood_movies.csv", type="csv")
    if upload is None:
        st.stop()
    raw = load_csv(upload)

# ---------- Column mapping ----------
cols = list(raw.columns)
mapping = {}
with st.sidebar.expander("Column mapping (fix if a guess is wrong)"):
    for key, label in LABELS.items():
        guess = guess_column(cols, GUESSES[key])
        options = ["(none)"] + cols
        idx = options.index(guess) if guess in options else 0
        choice = st.selectbox(label, options, index=idx, key=f"map_{key}")
        mapping[key] = None if choice == "(none)" else choice

# ---------- Clean ----------
df = raw.copy()

if mapping["year"]:
    yr = pd.to_numeric(df[mapping["year"]], errors="coerce")
    if yr.isna().mean() > 0.5:  # looks like full dates, not years
        yr = pd.to_datetime(df[mapping["year"]], errors="coerce").dt.year
    df["_year"] = yr

if mapping["gross"]:
    cleaned = df[mapping["gross"]].astype(str).str.replace(r"[^0-9.\-]", "", regex=True)
    df["_gross"] = pd.to_numeric(cleaned, errors="coerce")

if mapping["rating"]:
    df["_rating"] = pd.to_numeric(df[mapping["rating"]], errors="coerce")

if mapping["genre"]:
    df["_genres"] = df[mapping["genre"]].apply(split_multi)

if mapping["director"]:
    df["_directors"] = df[mapping["director"]].apply(split_multi)

# ---------- Filters ----------
st.sidebar.header("Filters")
fdf = df.copy()

if mapping["year"] and df["_year"].notna().any():
    y_min, y_max = int(df["_year"].min()), int(df["_year"].max())
    if y_min < y_max:
        y0, y1 = st.sidebar.slider("Release year", y_min, y_max, (y_min, y_max))
        fdf = fdf[fdf["_year"].between(y0, y1)]

if mapping["genre"]:
    all_genres = sorted({g for lst in df["_genres"] for g in lst})
    chosen = st.sidebar.multiselect("Genre", all_genres)
    if chosen:
        fdf = fdf[fdf["_genres"].apply(lambda lst: any(g in chosen for g in lst))]

if mapping["rating"] and df["_rating"].notna().any():
    r_min, r_max = float(df["_rating"].min()), float(df["_rating"].max())
    if r_min < r_max:
        rlo, rhi = st.sidebar.slider("Rating", r_min, r_max, (r_min, r_max))
        fdf = fdf[fdf["_rating"].between(rlo, rhi) | fdf["_rating"].isna()]

if fdf.empty:
    st.warning("No movies match these filters. Try widening them.")
    st.stop()

# ---------- KPIs ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Films", f"{len(fdf):,}")
if mapping["year"]:
    k2.metric("Years covered", f"{int(fdf['_year'].min())}–{int(fdf['_year'].max())}")
if mapping["rating"]:
    k3.metric("Average rating", f"{fdf['_rating'].mean():.2f}")
if mapping["gross"]:
    k4.metric("Median box office", f"{fdf['_gross'].median():,.1f}")

# ---------- Tabs ----------
t_genre, t_dir, t_year, t_box, t_data = st.tabs(
    ["🎭 Genres", "🎬 Directors", "📅 Releases", "💰 Box office", "🗂️ Data"]
)

with t_genre:
    if mapping["genre"]:
        g = fdf.explode("_genres")
        g = g[g["_genres"].notna() & (g["_genres"] != "")]
        top = g["_genres"].value_counts()
        c1, c2 = st.columns(2)
        fig = px.bar(top.head(15).sort_values(), orientation="h",
                     labels={"value": "Films", "index": "Genre"}, title="Most common genres")
        fig.update_layout(showlegend=False)
        c1.plotly_chart(fig, use_container_width=True)
        if mapping["year"]:
            n = st.slider("Genres to show in trend", 3, 12, 6)
            keep = top.head(n).index
            trend = (g[g["_genres"].isin(keep)].groupby(["_year", "_genres"]).size()
                     .reset_index(name="films"))
            fig = px.line(trend, x="_year", y="films", color="_genres",
                          labels={"_year": "Year", "films": "Films", "_genres": "Genre"},
                          title="Genre trends over time")
            c2.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select a genre column in the sidebar mapping.")

with t_dir:
    if mapping["director"]:
        d = fdf.explode("_directors")
        d = d[d["_directors"].notna() & (d["_directors"] != "")]
        n = st.slider("Directors to show", 5, 30, 10)
        c1, c2 = st.columns(2)
        by_count = d["_directors"].value_counts().head(n).sort_values()
        fig = px.bar(by_count, orientation="h", labels={"value": "Films", "index": "Director"},
                     title="Most prolific directors")
        fig.update_layout(showlegend=False)
        c1.plotly_chart(fig, use_container_width=True)
        if mapping["gross"]:
            by_gross = (d.groupby("_directors")["_gross"].sum()
                        .sort_values(ascending=False).head(n).sort_values())
            fig = px.bar(by_gross, orientation="h", labels={"value": "Total box office", "_directors": "Director"},
                         title="Directors by total box office")
            fig.update_layout(showlegend=False)
            c2.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select a director column in the sidebar mapping.")

with t_year:
    if mapping["year"]:
        per_year = fdf.groupby("_year").size().reset_index(name="films")
        fig = px.bar(per_year, x="_year", y="films", labels={"_year": "Year", "films": "Films"},
                     title="Films released per year")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select a year column in the sidebar mapping.")

with t_box:
    if mapping["gross"]:
        log = st.checkbox("Log scale (helps when a few films earn far more than the rest)")
        fig = px.histogram(fdf.dropna(subset=["_gross"]), x="_gross", nbins=40,
                           labels={"_gross": "Box office gross"}, title="Box office distribution")
        if log:
            fig.update_yaxes(type="log")
        st.plotly_chart(fig, use_container_width=True)
        if mapping["rating"]:
            hover = [mapping["title"]] if mapping["title"] else None
            fig = px.scatter(fdf.dropna(subset=["_gross", "_rating"]), x="_rating", y="_gross",
                             hover_name=hover[0] if hover else None,
                             labels={"_rating": "Rating", "_gross": "Box office gross"},
                             title="Rating vs box office")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select a box office column in the sidebar mapping.")

with t_data:
    visible = fdf.drop(columns=[c for c in fdf.columns if c.startswith("_")])
    st.dataframe(visible, use_container_width=True)
    st.download_button("Download filtered data (CSV)", visible.to_csv(index=False).encode("utf-8"),
                       "filtered_bollywood_movies.csv", "text/csv")

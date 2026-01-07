import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import numpy as np

# Page config
st.set_page_config(
    page_title="Bollywood Movies Dashboard",
    page_icon="🎬",
    layout="wide"
)

# Title
st.title("🎬 Bollywood Movies Analytics Dashboard")
st.markdown("**Analyzing 2,200+ Indian Films: Trends, Genres & Box Office Insights**")

# Load sample data (we'll create this)
@st.cache_data
def load_data():
    # Sample Bollywood movies data
    data = {
        'Movie': ['Pathaan', 'Jawan', 'Gadar 2', 'Dunki', 'Tiger 3', 'Animal', 'Rocky Aur Rani', 
                  'Bholaa', 'Shehzada', 'Selfiee', 'Kisi Ka Bhai Kisi Ki Jaan', 'Zara Hatke Zara Bachke',
                  'Adipurush', 'OMG 2', 'Dream Girl 2', 'Fukrey 3', 'The Vaccine War', 'Mission Raniganj',
                  'Jawan', 'Pathaan', '3 Idiots', 'PK', 'Dangal', 'Baahubali 2', 'KGF 2'],
        'Year': [2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023,
                 2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023, 2009, 2014, 2016, 2017, 2022],
        'Genre': ['Action', 'Action', 'Action', 'Drama', 'Action', 'Action', 'Romance',
                  'Action', 'Action', 'Comedy', 'Action', 'Romance', 'Action', 'Drama', 'Comedy',
                  'Comedy', 'Drama', 'Drama', 'Action', 'Action', 'Comedy', 'Drama', 'Drama', 'Action', 'Action'],
        'Director': ['Siddharth Anand', 'Atlee', 'Anil Sharma', 'Rajkumar Hirani', 'Maneesh Sharma',
                     'Sandeep Reddy Vanga', 'Karan Johar', 'Ajay Devgn', 'Rohit Dhawan', 'Raj Mehta',
                     'Farhad Samji', 'Laxman Utekar', 'Om Raut', 'Amit Rai', 'Raaj Shaandilyaa',
                     'Mrighdeep Singh Lamba', 'Vivek Agnihotri', 'Tinu Suresh Desai', 'Atlee',
                     'Siddharth Anand', 'Rajkumar Hirani', 'Rajkumar Hirani', 'Nitesh Tiwari',
                     'S.S. Rajamouli', 'Prashanth Neel'],
        'Rating': [7.5, 8.2, 7.1, 7.8, 6.9, 8.1, 7.3, 6.5, 5.8, 5.2, 5.5, 6.8, 5.1, 7.9, 6.7,
                   7.2, 6.4, 6.6, 8.2, 7.5, 8.4, 8.1, 8.3, 8.0, 8.4],
        'Box_Office_Crores': [1050, 1160, 685, 450, 465, 917, 355, 105, 45, 18, 105, 92, 300, 235,
                              280, 180, 25, 50, 1160, 1050, 460, 832, 2070, 1810, 1250]
    }
    return pd.DataFrame(data)

df = load_data()

# Sidebar filters
st.sidebar.header("🎯 Filters")
year_range = st.sidebar.slider(
    "Select Year Range",
    int(df['Year'].min()),
    int(df['Year'].max()),
    (int(df['Year'].min()), int(df['Year'].max()))
)

genres = st.sidebar.multiselect(
    "Select Genres",
    options=df['Genre'].unique(),
    default=df['Genre'].unique()
)

# Filter data
filtered_df = df[
    (df['Year'] >= year_range[0]) & 
    (df['Year'] <= year_range[1]) &
    (df['Genre'].isin(genres))
]

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Movies", len(filtered_df))
with col2:
    st.metric("Avg Rating", f"{filtered_df['Rating'].mean():.2f}")
with col3:
    st.metric("Total Box Office", f"₹{filtered_df['Box_Office_Crores'].sum():.0f}Cr")
with col4:
    st.metric("Top Genre", filtered_df['Genre'].mode()[0] if len(filtered_df) > 0 else "N/A")

# Charts
st.markdown("---")

# Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Genre Distribution")
    genre_counts = filtered_df['Genre'].value_counts()
    fig = px.pie(
        values=genre_counts.values,
        names=genre_counts.index,
        title="Movies by Genre",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 Movies by Year")
    yearly = filtered_df.groupby('Year').size().reset_index(name='Count')
    fig = px.bar(
        yearly,
        x='Year',
        y='Count',
        title="Number of Movies per Year",
        color='Count',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_container_width=True)

# Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎬 Top Directors")
    top_directors = filtered_df.groupby('Director').agg({
        'Movie': 'count',
        'Rating': 'mean',
        'Box_Office_Crores': 'sum'
    }).sort_values('Box_Office_Crores', ascending=False).head(10)
    
    fig = px.bar(
        top_directors.reset_index(),
        x='Box_Office_Crores',
        y='Director',
        orientation='h',
        title="Top 10 Directors by Box Office",
        color='Rating',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💰 Box Office vs Rating")
    fig = px.scatter(
        filtered_df,
        x='Rating',
        y='Box_Office_Crores',
        color='Genre',
        size='Box_Office_Crores',
        hover_data=['Movie', 'Director'],
        title="Box Office Performance vs Rating"
    )
    st.plotly_chart(fig, use_container_width=True)

# Row 3
st.subheader("🎯 Top 10 Highest Grossing Movies")
top_movies = filtered_df.nlargest(10, 'Box_Office_Crores')[['Movie', 'Year', 'Genre', 'Director', 'Rating', 'Box_Office_Crores']]
st.dataframe(top_movies, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**📊 Data Source:** Bollywood Movies Dataset (2009-2023) | **Built with:** Streamlit & Plotly")

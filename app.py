import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="Netflix Dashboard", page_icon="🎬", layout="wide")
st.markdown(
    """
    <div style="margin-top: -64px;">
        <h1 style='text-align: center; color: #E50914; font-size: 48px; margin-bottom: 0;'>
            🎬 Netflix <span style="color:white;">Data Analysis Dashboard</span>
        </h1>
        <h5 style='text-align: center; color: gray; font-weight: 400; margin-top: 5px;'>
            Insights into Netflix Movies & TV Shows 📊
        </h5>
    </div>
    """,
    unsafe_allow_html=True
)




# Load dataset
df = pd.read_csv("netflix_titles.csv")

# Data Preprocessing
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df['year_added'] = df['date_added'].dt.year
df.dropna(subset=['type'], inplace=True)

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Data")

year_options = ['All'] + sorted(df['year_added'].dropna().unique().tolist())
country_options = ['All'] + sorted(df['country'].dropna().unique().tolist())

year_filter = st.sidebar.selectbox("Select Year", year_options)
country_filter = st.sidebar.selectbox("Select Country", country_options)
genre_filter = st.sidebar.text_input("Search Genre (e.g. Drama, Comedy)")

filtered_df = df.copy()

if year_filter != 'All':
    filtered_df = filtered_df[filtered_df['year_added'] == year_filter]

if country_filter != 'All':
    filtered_df = filtered_df[filtered_df['country'] == country_filter]

if genre_filter:
    filtered_df = filtered_df[filtered_df['listed_in'].str.contains(genre_filter, case=False, na=False)]


# Show dataset
st.subheader("📄 Filtered Dataset Preview")
st.dataframe(filtered_df.head())

# --- Plot 1: Movies vs TV Shows ---
st.subheader("🎬 Total Movies vs TV Shows")

# Group by 'type' to get actual counts
type_count = filtered_df['type'].value_counts().reset_index()
type_count.columns = ['Type', 'Count']

fig1 = px.bar(
    type_count,
    x='Type',
    y='Count',
    color='Type',
    text='Count',
    title="Total Movies vs TV Shows",
    color_discrete_sequence=px.colors.qualitative.Vivid
)
fig1.update_traces(texttemplate='%{text}', textposition='outside')
fig1.update_layout(yaxis_title="Number of Titles", xaxis_title="Type")

st.plotly_chart(fig1, use_container_width=True)

# --- Plot 2: Top 10 Countries ---
st.subheader("🌍 Top 10 Countries Producing Most Titles")
top_countries = df['country'].value_counts().head(10)
fig2 = px.bar(x=top_countries.values, y=top_countries.index,
              orientation='h', title="Top 10 Countries",
              color=top_countries.values, color_continuous_scale='turbo')
st.plotly_chart(fig2, use_container_width=True)

# --- Plot 3: Content Growth Over Years ---
st.subheader("📈 Content Growth Over Years")
growth = df['year_added'].value_counts().sort_index()
fig3 = px.line(x=growth.index, y=growth.values,
               markers=True, title="Content Added Per Year",
               labels={'x': 'Year', 'y': 'Number of Titles'})
st.plotly_chart(fig3, use_container_width=True)

# --- Plot 4: Top Genres ---
st.subheader("🎭 Top Genres on Netflix")
from collections import Counter
genre_list = df['listed_in'].dropna().apply(lambda x: x.split(', '))
all_genres = [g.strip() for sublist in genre_list for g in sublist]
top_genres = pd.Series(Counter(all_genres)).head(10)
fig4 = px.pie(values=top_genres.values, names=top_genres.index,
              title="Top 10 Genres", color_discrete_sequence=px.colors.sequential.RdBu)
st.plotly_chart(fig4, use_container_width=True)

# --- Word Cloud ---
with st.expander("☁️ View Genre Word Cloud"):
    text = " ".join(df['listed_in'].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white',
                          colormap='plasma').generate(text)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

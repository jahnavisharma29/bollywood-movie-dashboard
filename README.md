# 🎬 Bollywood Movie Dashboard

An interactive Streamlit dashboard that explores 2,200+ Bollywood films, showing how genres, directors, release patterns and box office performance have changed over time.

---

## 🎯 What you can explore

- **Genres:** the most common genres and how each one has trended over the years
- **Directors:** the most prolific directors and the ones with the highest total box office
- **Releases:** how many films were released each year
- **Box office:** how gross earnings are distributed, and how ratings relate to box office
- **Data:** browse the dataset and download the filtered results as a CSV

Use the sidebar filters to narrow everything by release year, genre and rating.

## 🛠️ Tech stack

Python · Pandas · Plotly · Streamlit

## 📁 Project structure

```
bollywood-movie-dashboard/
├── data/
│   └── bollywood_movies.csv   # Cleaned movie data
├── app.py                     # Streamlit dashboard
├── requirements.txt           # Python dependencies
├── LICENSE
└── README.md
```

## 🚀 Run it locally

```bash
# 1. Clone the repo
git clone https://github.com/jahnavisharma29/bollywood-movie-dashboard.git
cd bollywood-movie-dashboard

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Start the app
python3 -m streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## 📚 Data

The dataset was compiled from public movie databases and cleaned for analysis. It covers 2,200+ films and includes:

- Movie title
- Release year
- Genre(s)
- Director(s)
- Box office gross
- Ratings (where available)

Some fields, such as ratings, are not available for every film, so a few charts only use the films that have a value.

## 📄 License

Released under the [MIT License](LICENSE).

## 👩‍💻 Author

**Jahnavi Sharma** · [GitHub](https://github.com/jahnavisharma29)

Released under the [MIT License](LICENSE).

## 👩‍💻 Author

**Jahnavi Sharma** · [GitHub](https://github.com/jahnavisharma29)

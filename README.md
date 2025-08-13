# Crypto Watchlist Dashboard

A Streamlit-based dashboard that allows users to track cryptocurrency prices, view price history, and receive alerts when coins hit predefined thresholds.  
This project demonstrates Python backend development, API integration, data visualization, and UI building with Streamlit.



## Features
- **Real-time Price Tracking** — Fetches live crypto prices from the CoinGecko API.
- **Watchlist Management** — Add or remove coins with custom thresholds.
- **Price History Viewer** — Interactive charts and downloadable CSVs for past price data.
- **News Feed** — Fetches the latest crypto-related news articles via GNews API.
- **Auto Refresh** — Keeps data up to date without manual reload.
- **Multi-Page App** — Separate pages for Watchlist, Price History, and News Feed.



##  Tech Stack
- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **Backend/Logic**: Python
- **APIs**:
  - [CoinGecko API](https://www.coingecko.com/en/api) — for crypto prices
  - [GNews API](https://gnews.io/) — for news articles
- **Data Storage**: Local JSON files for watchlist & price history
- **Visualization**: Matplotlib & Streamlit’s built-in chart components


## Project Structure
├── app.py                  # Main Streamlit dashboard
├── pages/                  # Additional pages (e.g., News Feed)
├── utils.py                # API helper functions
├── manage_watchlist.py     # Add/remove coins from watchlist
├── visualize.py            # Chart plotting functions
├── logger.py               # for logging locally
├── price_history.json      # Stored price history (local)
├── watchlist.json          # Stored watchlist (local)
└── requirements.txt        # Python dependencies




##  Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/HarisK15/Crypto_App.git
   cd crypto_alert
   

2.	Create a virtual environment
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows


3.	Install dependencies
pip install -r requirements.txt

4. Create a .env file with your API keys:
GNEWS_API_KEY=your_gnews_api_key_here

5. Run the app
streamlit run app.py


Usage
	1.	Add coins to your watchlist with custom thresholds.
	2.	View live prices in the dashboard.
	3.	Check price history via charts and export to CSV.
	4.	Read latest crypto news from the News Feed page.

Future Improvements
	•	User Authentication — Allow personal accounts & saved preferences.
	•	Database Integration — Replace local JSON storage with a cloud database.
	•	Email/Push Notifications — Send alerts when thresholds are reached.
	•	Deployment — Host on Streamlit Cloud or another platform for public access.


License

This project is open-source and available under the MIT License.





👤 Author

Haris Kamran

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Import our modules
from config_loader import get_config, get_all_config
from database import db_manager, get_watchlist, save_price_data, get_price_history
from utils import fetch_prices_batch, validate_coin_id
from alerts import AlertChecker, AlertDirection
from notifier import notifier

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the page
st.set_page_config(
    page_title="Crypto Alert Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set up session state for the app
if 'alert_checker' not in st.session_state:
    st.session_state.alert_checker = AlertChecker()

if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

def main():
    """Main app function - handles the overall layout and navigation."""
    
    # Sidebar with controls
    with st.sidebar:
        st.title("🔧 Settings")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox(
            "Auto-refresh", 
            value=get_config('app.auto_refresh_interval', 60000) > 0,
            help="Automatically refresh data"
        )
        
        if auto_refresh:
            refresh_interval = st.slider(
                "Refresh interval (seconds)", 
                min_value=30, 
                max_value=300, 
                value=60,
                help="How often to refresh data"
            )
        
        # Theme picker
        theme = st.selectbox(
            "Theme",
            ["light", "dark", "auto"],
            index=0,
            help="Choose your preferred theme"
        )
        
        # Database info
        if st.button("Database Stats", key="sidebar_db_stats"):
            stats = db_manager.get_database_stats()
            if stats:
                st.json(stats)
        
        # Database maintenance buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Backup DB", key="sidebar_backup_db"):
                backup_path = f"backups/crypto_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                if db_manager.backup_database(backup_path):
                    st.success(f"Backup created: {backup_path}")
                else:
                    st.error("Backup failed")
        
        with col2:
            if st.button("Cleanup DB", key="sidebar_cleanup_db"):
                deleted = db_manager.cleanup_old_price_data()
                st.success(f"Cleaned up {deleted} old records")
    
    # Main app content
    st.title("📈 Crypto Alert Dashboard")
    st.caption(f"Version {get_config('app.version', '2.0.0')} | Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
    
    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "👀 Watchlist", 
        "📈 Price History", 
        "🚨 Alerts", 
        "⚙️ Settings"
    ])
    
    with tab1:
        show_dashboard()
    
    with tab2:
        show_watchlist_management()
    
    with tab3:
        show_price_history()
    
    with tab4:
        show_alerts()
    
    with tab5:
        show_settings()
    
    # Handle auto-refresh
    if auto_refresh and 'refresh_interval' in locals():
        if (datetime.now() - st.session_state.last_refresh).seconds >= refresh_interval:
            st.session_state.last_refresh = datetime.now()
            st.rerun()

def show_dashboard():
    """Shows the main dashboard with current prices and market overview."""
    st.header("Current Market Overview")
    
    # Get the current watchlist
    watchlist = get_watchlist()
    
    if not watchlist:
        st.warning("No coins in watchlist. Add some coins in the Watchlist tab!")
        return
    
    # Fetch current prices for all coins
    coin_ids = [item['coin_id'] for item in watchlist]
    price_data = fetch_prices_batch(coin_ids)
    
    # Display prices in a grid layout
    cols = st.columns(min(len(watchlist), 4))
    
    for i, item in enumerate(watchlist):
        col_idx = i % len(cols)
        with cols[col_idx]:
            coin_id = item['coin_id']
            price = price_data.get(coin_id, {}).get('usd')
            
            if price:
                # Store the price data
                save_price_data(coin_id, price)
                
                # Check if any alerts should trigger
                check_and_display_alerts(item, price)
                
                # Show the price metric
                st.metric(
                    label=f"{item['coin_name'].title()}",
                    value=f"${price:,.2f}",
                    delta=get_price_change_24h(price_data, coin_id)
                )
                
                # Display alert thresholds
                if item.get('threshold_above'):
                    st.caption(f"Alert above: ${item['threshold_above']:,.2f}")
                if item.get('threshold_below'):
                    st.caption(f"Alert below: ${item['threshold_below']:,.2f}")
            else:
                st.error(f"Could not fetch price for {coin_id}")
    
    # Show market summary stats
    if price_data:
        st.subheader("Market Summary")
        total_market_cap = sum(
            price_data.get(coin, {}).get('usd_market_cap', 0) 
            for coin in price_data
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Market Cap", f"${total_market_cap:,.0f}")
        with col2:
            st.metric("Coins Tracked", len(watchlist))
        with col3:
            st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))

def show_watchlist_management():
    """Handles adding and removing coins from the watchlist."""
    st.header("Watchlist Management")
    
    # Form to add new coins
    with st.expander("Add New Coin", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            coin_id = st.text_input("Coin ID", placeholder="bitcoin", key="add_coin_id")
        
        with col2:
            threshold_above = st.number_input("Alert Above ($)", min_value=0.0, step=0.01, key="add_threshold_above")
        
        with col3:
            threshold_below = st.number_input("Alert Below ($)", min_value=0.0, step=0.01, key="add_threshold_below")
        
        with col4:
            if st.button("Add Coin", key="add_coin_button"):
                if coin_id and validate_coin_id(coin_id):
                    # Verify the coin exists by checking its price
                    price_data = fetch_prices_batch([coin_id])
                    if coin_id in price_data:
                        coin_name = coin_id.title()
                        if db_manager.add_to_watchlist(
                            coin_id, coin_name, threshold_above, threshold_below
                        ):
                            st.success(f"Added {coin_name} to watchlist")
                            st.rerun()
                        else:
                            st.error("Failed to add coin to watchlist")
                    else:
                        st.error(f"Coin {coin_id} not found")
                else:
                    st.error("Invalid coin ID")
    
    # Show current watchlist
    st.subheader("Current Watchlist")
    watchlist = get_watchlist()
    
    if watchlist:
        # Create a table view of the watchlist
        df = pd.DataFrame(watchlist)
        
        # Display the watchlist data
        st.dataframe(
            df[['coin_name', 'threshold_above', 'threshold_below', 'enabled', 'created_at']],
            use_container_width=True
        )
        
        # Interface to remove coins
        coin_to_remove = st.selectbox(
            "Select coin to remove",
            [item['coin_name'] for item in watchlist],
            key="remove_coin_select"
        )
        
        if st.button("Remove Selected Coin", key="remove_coin_button"):
            coin_id = next(item['coin_id'] for item in watchlist if item['coin_name'] == coin_to_remove)
            if db_manager.remove_from_watchlist(coin_id):
                st.success(f"Removed {coin_to_remove} from watchlist")
                st.rerun()
            else:
                st.error("Failed to remove coin")
    else:
        st.info("No coins in watchlist. Add some coins above!")

def show_price_history():
    """Displays price history charts and data for selected coins."""
    st.header("Price History")
    
    watchlist = get_watchlist()
    if not watchlist:
        st.warning("No coins in watchlist to show history for.")
        return
    
    # Let user pick which coin to view
    selected_coin = st.selectbox(
        "Select a coin",
        [item['coin_name'] for item in watchlist],
        key="history_coin_select"
    )
    
    if selected_coin:
        coin_id = next(item['coin_id'] for item in watchlist if item['coin_name'] == selected_coin)
        
        # Time period selection
        col1, col2 = st.columns([1, 3])
        with col1:
            timeframe = st.selectbox(
                "Timeframe",
                ["1d", "7d", "30d", "90d"],
                key="timeframe_select"
            )
        
        # Get the historical data
        days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(timeframe, 30)
        
        df = get_price_history(coin_id, days)
        
        if not df.empty:
            # Show current price
            current_price = df.iloc[-1]['price'] if len(df) > 0 else None
            if current_price:
                st.metric(f"{selected_coin} Current Price", f"${current_price:,.2f}")
            
            # Create the price chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['price'],
                mode='lines+markers',
                name='Price',
                line=dict(color='#1f77b4', width=2)
            ))
            
            fig.update_layout(
                title=f"{selected_coin} Price History ({timeframe})",
                xaxis_title="Time",
                yaxis_title="Price (USD)",
                hovermode='x unified',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show price statistics
            if len(df) > 1:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Min Price", f"${df['price'].min():,.2f}")
                with col2:
                    st.metric("Max Price", f"${df['price'].max():,.2f}")
                with col3:
                    st.metric("Avg Price", f"${df['price'].mean():,.2f}")
                with col4:
                    price_change = df['price'].iloc[-1] - df['price'].iloc[0]
                    st.metric("Change", f"${price_change:,.2f}")
            
            # Download option for the data
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{selected_coin}_{timeframe}_price_history.csv",
                mime="text/csv",
                key=f"download_{selected_coin}_{timeframe}"
            )
        else:
            st.info(f"No price history available for {selected_coin}")

def show_alerts():
    """Shows alert history and notification settings."""
    st.header("Alerts & Notifications")
    
    # Display recent alerts
    st.subheader("Recent Alerts")
    alerts = db_manager.get_alerts(limit=50)
    
    if alerts:
        # Convert to a table for display
        df = pd.DataFrame(alerts)
        df['triggered_at'] = pd.to_datetime(df['triggered_at'])
        
        # Filter by acknowledgment status
        show_acknowledged = st.checkbox("Show acknowledged alerts", value=False, key="show_acknowledged_alerts")
        if not show_acknowledged:
            df = df[df['acknowledged'] == 0]
        
        if not df.empty:
            st.dataframe(
                df[['coin_id', 'alert_type', 'threshold', 'current_price', 'message', 'triggered_at', 'acknowledged']],
                use_container_width=True
            )
            
            # Button to acknowledge all unacknowledged alerts
            if st.button("Acknowledge All Unacknowledged", key="acknowledge_all_alerts"):
                unacknowledged = df[df['acknowledged'] == 0]['id'].tolist()
                for alert_id in unacknowledged:
                    db_manager.acknowledge_alert(alert_id)
                st.success(f"Acknowledged {len(unacknowledged)} alerts")
                st.rerun()
        else:
            st.info("No alerts to display")
    else:
        st.info("No alerts found")
    
    # Notification configuration
    st.subheader("Notification Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Email Notifications**")
        email_enabled = st.checkbox("Enable email alerts", value=get_config('notifications.email.enabled', False), key="email_enabled_checkbox")
        
        if email_enabled:
            recipient = st.text_input("Email address for alerts", key="email_recipient")
            if st.button("Test Email", key="test_email_button"):
                if recipient:
                    success = notifier.send_notification(
                        recipient, 
                        "Test Alert", 
                        "This is a test notification from Crypto Alert Dashboard",
                        "email"
                    )
                    if success:
                        st.success("Test email sent successfully!")
                    else:
                        st.error("Failed to send test email")
    
    with col2:
        st.write("**Webhook Notifications**")
        webhook_enabled = st.checkbox("Enable webhook alerts", value=get_config('notifications.webhook.enabled', False), key="webhook_enabled_checkbox")
        
        if webhook_enabled:
            webhook_url = st.text_input("Webhook URL", key="webhook_url_input")
            if st.button("Test Webhook", key="test_webhook_button"):
                if webhook_url:
                    success = notifier.send_notification(
                        webhook_url,
                        "Test Alert",
                        "This is a test webhook notification",
                        "webhook"
                    )
                    if success:
                        st.success("Test webhook sent successfully!")
                    else:
                        st.error("Failed to send test webhook")

def show_settings():
    """Displays application settings and database management options."""
    st.header("Application Settings")
    
    # Configuration management
    st.subheader("Current Configuration")
    
    if st.button("Reload Configuration", key="reload_config_button"):
        from config_loader import reload_config
        reload_config()
        st.success("Configuration reloaded!")
    
    # Show the current config
    config_data = get_all_config()
    st.json(config_data)
    
    # Database management section
    st.subheader("Database Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Database Stats", key="settings_db_stats"):
            stats = db_manager.get_database_stats()
            st.json(stats)
    
    with col2:
        if st.button("Backup Database", key="settings_backup_db"):
            backup_path = f"backups/crypto_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            if db_manager.backup_database(backup_path):
                st.success(f"Backup created: {backup_path}")
            else:
                st.error("Backup failed")
    
    with col3:
        if st.button("Optimize Database", key="settings_optimize_db"):
            db_manager.vacuum_database()
            st.success("Database optimized!")

def check_and_display_alerts(watchlist_item, current_price):
    """Checks if price alerts should trigger and displays them."""
    if not current_price:
        return
    
    coin_id = watchlist_item['coin_id']
    threshold_above = watchlist_item.get('threshold_above')
    threshold_below = watchlist_item.get('threshold_below')
    
    # Check if price is above the upper threshold
    if threshold_above and current_price > threshold_above:
        alert_message = f"🚨 {watchlist_item['coin_name'].title()} is above ${threshold_above:,.2f} (Current: ${current_price:,.2f})"
        st.warning(alert_message)
        
        # Save this alert to the database
        db_manager.save_alert(
            coin_id, "above", threshold_above, current_price, alert_message
        )
    
    # Check if price is below the lower threshold
    if threshold_below and current_price < threshold_below:
        alert_message = f"🚨 {watchlist_item['coin_name'].title()} is below ${threshold_below:,.2f} (Current: ${current_price:,.2f})"
        st.error(alert_message)
        
        # Save this alert to the database
        db_manager.save_alert(
            coin_id, "below", threshold_below, current_price, alert_message
        )

def get_price_change_24h(price_data, coin_id):
    """Gets the 24-hour price change percentage for display."""
    if coin_id in price_data:
        change_24h = price_data[coin_id].get('usd_24h_change', 0)
        if change_24h is not None:
            return f"{change_24h:+.2f}%"
    return None

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)



import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)

class AlertDirection(Enum):
    """Different types of alert directions we support."""
    ABOVE = "above"
    BELOW = "below"
    PERCENTAGE_CHANGE = "percentage_change"
    VOLATILITY = "volatility"

@dataclass
class AlertCondition:
    """Holds all the info about an alert condition."""
    coin: str
    threshold: float
    direction: AlertDirection
    enabled: bool = True
    created_at: datetime = None
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class AlertChecker:
    """Handles all the alert checking logic."""
    
    def __init__(self):
        self.alert_history = []
    
    def check_alert(self, price: float, threshold: float, direction: AlertDirection, coin: str) -> Tuple[bool, str]:
        """
        Checks if an alert should trigger based on current price.
        
        Args:
            price: Current price of the coin
            threshold: Price threshold to check against
            direction: Which way to check (above/below)
            coin: Name of the coin
            
        Returns:
            Tuple of (did it trigger, message to show)
        """
        if not isinstance(price, (int, float)) or price < 0:
            logger.error(f"Invalid price value: {price}")
            return False, f"Invalid price value: {price}"
            
        if not isinstance(threshold, (int, float)) or threshold < 0:
            logger.error(f"Invalid threshold value: {threshold}")
            return False, f"Invalid threshold value: {threshold}"
        
        try:
            if direction == AlertDirection.ABOVE:
                is_triggered = price > threshold
                if is_triggered:
                    message = f"🚨 ALERT! {coin.capitalize()} is above threshold of ${threshold:,.2f}, current value is ${price:,.2f}"
                else:
                    message = f"✅ {coin.capitalize()} is below threshold of ${threshold:,.2f}, current value is ${price:,.2f}"
                    
            elif direction == AlertDirection.BELOW:
                is_triggered = price < threshold
                if is_triggered:
                    message = f"🚨 ALERT! {coin.capitalize()} is below threshold of ${threshold:,.2f}, current value is ${price:,.2f}"
                else:
                    message = f"✅ {coin.capitalize()} is above threshold of ${threshold:,.2f}, current value is ${price:,.2f}"
                    
            elif direction == AlertDirection.PERCENTAGE_CHANGE:
                # TODO: Need previous price data to implement this
                message = f"Percentage change alerts not yet implemented for {coin}"
                is_triggered = False
                
            elif direction == AlertDirection.VOLATILITY:
                # TODO: Need historical data to implement this
                message = f"Volatility alerts not yet implemented for {coin}"
                is_triggered = False
                
            else:
                logger.error(f"Unknown alert direction: {direction}")
                return False, f"Unknown alert direction: {direction}"
            
            # Log what happened
            logger.info(f"Alert check for {coin}: {message}")
            
            return is_triggered, message
            
        except Exception as e:
            logger.error(f"Error checking alert for {coin}: {e}")
            return False, f"Error checking alert: {str(e)}"
    
    def check_alert_condition(self, price: float, condition: AlertCondition) -> Tuple[bool, str]:
        """
        Checks an alert condition and updates its state.
        
        Args:
            price: Current price of the coin
            condition: The alert condition to check
            
        Returns:
            Tuple of (did it trigger, message to show)
        """
        if not condition.enabled:
            return False, f"Alert for {condition.coin} is disabled"
            
        is_triggered, message = self.check_alert(
            price, condition.threshold, condition.direction, condition.coin
        )
        
        if is_triggered:
            condition.last_triggered = datetime.now()
            condition.trigger_count += 1
            self._record_alert(condition, price, message)
            
        return is_triggered, message
    
    def _record_alert(self, condition: AlertCondition, price: float, message: str):
        """Keeps track of when alerts were triggered."""
        alert_record = {
            'timestamp': datetime.now(),
            'coin': condition.coin,
            'price': price,
            'threshold': condition.threshold,
            'direction': condition.direction.value,
            'message': message
        }
        self.alert_history.append(alert_record)
        
        # Keep only last 1000 alerts to avoid memory issues
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
    
    def get_alert_history(self, coin: Optional[str] = None, limit: int = 100) -> list:
        """
        Gets the history of alerts, optionally filtered by coin.
        
        Args:
            coin: Optional coin filter
            limit: Max number of alerts to return
            
        Returns:
            List of alert records
        """
        if coin:
            filtered_history = [alert for alert in self.alert_history if alert['coin'] == coin]
        else:
            filtered_history = self.alert_history
            
        return filtered_history[-limit:]
    
    def clear_alert_history(self):
        """Clears the alert history."""
        self.alert_history.clear()
        logger.info("Alert history cleared")

# Keep the old function for backward compatibility
def check_alert(price, threshold, direction, coin):
    """
    Old function that some code might still use.
    
    Args:
        price: Current price
        threshold: Price threshold
        direction: 'above' or 'below'
        coin: Coin name
        
    Returns:
        Alert message string
    """
    try:
        # Convert string direction to enum
        if direction.lower() == 'above':
            alert_direction = AlertDirection.ABOVE
        elif direction.lower() == 'below':
            alert_direction = AlertDirection.BELOW
        else:
            return f"Invalid direction: {direction}"
        
        # Create temporary condition
        condition = AlertCondition(coin=coin, threshold=threshold, direction=alert_direction)
        
        # Check alert
        checker = AlertChecker()
        is_triggered, message = checker.check_alert(price, threshold, alert_direction, coin)
        
        return message
        
    except Exception as e:
        logger.error(f"Error in old check_alert function: {e}")
        return f"Error checking alert: {str(e)}"


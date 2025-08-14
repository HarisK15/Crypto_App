import pytest
from unittest.mock import Mock, patch
import requests
from utils import fetch_price, fetch_prices_batch, validate_coin_id

class TestUtils:
    """Test cases for utility functions."""
    
    def test_validate_coin_id_valid(self):
        """Test valid coin ID validation."""
        valid_ids = ["bitcoin", "ethereum", "solana", "cardano"]
        for coin_id in valid_ids:
            assert validate_coin_id(coin_id) == True
    
    def test_validate_coin_id_invalid(self):
        """Test invalid coin ID validation."""
        invalid_ids = ["", None, "123", "BITCOIN", "bit coin", "bit-coin"]
        for coin_id in invalid_ids:
            assert validate_coin_id(coin_id) == False
    
    @patch('utils.requests.get')
    def test_fetch_price_success(self, mock_get):
        """Test successful price fetch."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"bitcoin": {"usd": 50000.0}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_price("bitcoin")
        assert result == 50000.0
    
    @patch('utils.requests.get')
    def test_fetch_price_coin_not_found(self, mock_get):
        """Test price fetch when coin is not found."""
        # Mock response with coin not found
        mock_response = Mock()
        mock_response.json.return_value = {"ethereum": {"usd": 3000.0}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_price("bitcoin")
        assert result is None
    
    @patch('utils.requests.get')
    def test_fetch_price_no_usd_price(self, mock_get):
        """Test price fetch when no USD price is available."""
        # Mock response with no USD price
        mock_response = Mock()
        mock_response.json.return_value = {"bitcoin": {}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_price("bitcoin")
        assert result is None
    
    @patch('utils.requests.get')
    def test_fetch_price_request_exception(self, mock_get):
        """Test price fetch when request fails."""
        # Mock request exception
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = fetch_price("bitcoin")
        assert result is None
    
    @patch('utils.requests.get')
    def test_fetch_price_invalid_json(self, mock_get):
        """Test price fetch when response is invalid JSON."""
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_price("bitcoin")
        assert result is None
    
    @patch('utils.requests.get')
    def test_fetch_prices_batch_success(self, mock_get):
        """Test successful batch price fetch."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "bitcoin": {"usd": 50000.0},
            "ethereum": {"usd": 3000.0}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_prices_batch(["bitcoin", "ethereum"])
        assert result == {
            "bitcoin": {"usd": 50000.0},
            "ethereum": {"usd": 3000.0}
        }
    
    def test_fetch_prices_batch_empty_list(self):
        """Test batch price fetch with empty coin list."""
        result = fetch_prices_batch([])
        assert result == {}
    
    def test_fetch_prices_batch_invalid_coins(self):
        """Test batch price fetch with invalid coin IDs."""
        result = fetch_prices_batch([None, "", "123"])
        assert result == {}
    
    @patch('utils.requests.get')
    def test_fetch_prices_batch_request_exception(self, mock_get):
        """Test batch price fetch when request fails."""
        # Mock request exception
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = fetch_prices_batch(["bitcoin", "ethereum"])
        assert result == {}
    
    @patch('utils.requests.get')
    def test_fetch_prices_batch_invalid_response_format(self, mock_get):
        """Test batch price fetch with invalid response format."""
        # Mock invalid response format
        mock_response = Mock()
        mock_response.json.return_value = "invalid_format"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_prices_batch(["bitcoin", "ethereum"])
        assert result == {}

if __name__ == "__main__":
    pytest.main([__file__])

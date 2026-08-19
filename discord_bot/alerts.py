import json
import os

ALERTS_FILE = 'alerts.json'

def load_alerts():
    if os.path.exists(ALERTS_FILE):
        try:
            with open(ALERTS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_alerts(data):
    with open(ALERTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_alert(user_id, ticker, condition, target_price):
    """
    Adds a new alert for a user.
    Condition should be either '>' or '<'.
    """
    data = load_alerts()
    user_id_str = str(user_id)

    if user_id_str not in data:
        data[user_id_str] = []

    new_alert = {
        'ticker': ticker.upper(),
        'condition': condition,
        'price': float(target_price)
    }

    # Check if this exact alert already exists
    if new_alert not in data[user_id_str]:
        data[user_id_str].append(new_alert)
        save_alerts(data)
        return True
    return False

def get_user_alerts(user_id):
    """Returns a list of alerts for a specific user."""
    data = load_alerts()
    return data.get(str(user_id), [])

def remove_alert(user_id, index):
    """Removes an alert for a user by index (0-based internally, user might provide 1-based)."""
    data = load_alerts()
    user_id_str = str(user_id)

    if user_id_str in data and 0 <= index < len(data[user_id_str]):
        removed = data[user_id_str].pop(index)
        save_alerts(data)
        return removed
    return None

def remove_alert_by_value(user_id, alert_obj):
    """Removes a specific alert object for a user."""
    data = load_alerts()
    user_id_str = str(user_id)

    if user_id_str in data and alert_obj in data[user_id_str]:
        data[user_id_str].remove(alert_obj)
        save_alerts(data)
        return True
    return False

def get_all_alerts():
    """Returns all alerts for the background task."""
    return load_alerts()

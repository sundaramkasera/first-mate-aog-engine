import subprocess
import json
import os
from utils.weather import get_hub_conditions

def run_coral_query(sql_query: str) -> str:
    """
    Executes a structured SQL check across mock enterprise databases via the Coral CLI.
    """
    try:
        # Use ./coral if on Linux/Streamlit, or coral/coral.exe depending on the local env
        executable = "coral" 
        if os.path.exists("./coral"):
            executable = "./coral"
            
        # Execute the query directly. The catalog is already registered via 'coral source add'
        result = subprocess.run(
            [executable, "sql", sql_query],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Database Execution Error: {e.stderr}"
    except FileNotFoundError:
        return "Error: Coral CLI not found in PATH or local directory."

def check_live_aviation_weather(airport_code: str) -> str:
    """
    Retrieves live meteorological metrics for Indian hubs to calculate ground delays.
    """
    return get_hub_conditions(airport_code)

# Dictionary mapping function names to the actual Python functions
TOOL_FUNCTIONS = {
    "run_coral_query": run_coral_query,
    "check_live_aviation_weather": check_live_aviation_weather
}

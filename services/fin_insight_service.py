# services/fin_insight_service.py
import json
import os
import re
import subprocess
import sys

def get_financial_data(ticker):
    """Call the fin_insight CLI tool and parse its output"""
    # Find the fin_insight.py file location
    fin_insight_path = None
    for path in sys.path:
        potential_path = os.path.join(path, 'fin_insight.py')
        if os.path.exists(potential_path):
            fin_insight_path = potential_path
            break
            
    if not fin_insight_path:
        # Try to find it in the site-packages directory
        for path in sys.path:
            if 'site-packages' in path:
                potential_path = os.path.join(path, 'fin_insight', 'fin_insight.py')
                if os.path.exists(potential_path):
                    fin_insight_path = potential_path
                    break
    
    if not fin_insight_path:
        print("Could not find fin_insight.py")
        raise ValueError("fin-insight package not found in the system")
    
    # Run the fin_insight command with the ticker as an argument
    try:
        result = subprocess.run(
            [sys.executable, fin_insight_path, ticker],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Print the output for debugging
        print(f"fin_insight output: {result.stdout}")
        
        # Extract JSON from the output
        # Look for JSON content (starts with { and ends with })
        json_match = re.search(r'(\{.*\})', result.stdout, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            try:
                data = json.loads(json_str)
                return data
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in fin-insight output: {e}")
        else:
            raise ValueError("No JSON data found in fin-insight output")
            
    except subprocess.CalledProcessError as e:
        print(f"Error calling fin_insight: {e}")
        print(f"stderr: {e.stderr}")
        raise ValueError(f"Error executing fin-insight: {e.stderr}")
import streamlit as st
import json
from github import Github
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Function to connect to GitHub and retrieve files
def get_github_files(repo_name, access_key, file_names):
    try:
        g = Github(access_key)
        repo = g.get_repo(repo_name)
        files = {}
        for file_name in file_names:
            try:
                file_content = repo.get_contents(file_name).decoded_content.decode()
                files[file_name] = file_content
                print(f"Successfully retrieved {file_name}")
            except Exception as e:
                print(f"Error retrieving {file_name}: {e}")
        
        # Retrieve preferences.json
        preferences_file = 'preferences.json'
        try:
            preferences_content = repo.get_contents(preferences_file).decoded_content.decode()
            preferences = json.loads(preferences_content)
            files[preferences_file] = preferences
            print(f"Successfully retrieved {preferences_file}")
        except Exception as e:
            print(f"Error retrieving {preferences_file}: {e}")
        
        return files
    except Exception as e:
        print(f"Error connecting to GitHub: {e}")
        return {}

# Function to update preferences.json on GitHub
def update_github_file(repo_name, access_key, file_name, new_content):
    g = Github(access_key)
    repo = g.get_repo(repo_name)
    contents = repo.get_contents(file_name)
    repo.update_file(contents.path, "Update preferences.json", new_content, contents.sha)
import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go

# Function to parse date and time from your data format
def parse_date_time(line):
    try:
        # Example line: "Date: Thursday 06/20/2024, Time: 00:00:00, Count: 1, Pin: D1"
        date_str = line.split(", ")[0].split(": ")[1]  # Extract "Thursday 06/20/2024"
        time_str = line.split(", ")[1].split(": ")[1]  # Extract "00:00:00"
        
        datetime_str = f"{date_str} {time_str}"
        return datetime.datetime.strptime(datetime_str, '%A %m/%d/%Y %H:%M:%S')
    except IndexError:
        return None
    except ValueError:
        return None

# Function to read and filter data
def read_and_filter_data(file_content):
    try:
        lines = file_content.splitlines()
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return []

    data = []
    for line in lines:
        timestamp = parse_date_time(line)
        if timestamp is None:
            continue
        
        try:
            count = int(line.split(", ")[2].split(": ")[1])  # Extract "Count: 1"
            sensor_name = line.split(", ")[3].split(": ")[1]  # Extract "Pin: D1" and get "D1"
        except (IndexError, ValueError):
            continue
        
        data.append((timestamp, count, sensor_name))
    
    if not data:
        print("No valid data found in the file.")
    
    # Sort data by timestamp
    data.sort(key=lambda x: x[0])
    
    return data

def clip_to_last_24_hours(filtered_data):
    if not filtered_data:
        return []
    
    # Find the most recent timestamp
    most_recent_time = filtered_data[-1][0]
    
    # Calculate the cutoff time (24 hours before the most recent time)
    cutoff_time = most_recent_time - datetime.timedelta(hours=24)
    
    # Filter data to include only entries within the last 24 hours
    clipped_data = [(ts, count, sensor_name) for (ts, count, sensor_name) in filtered_data if ts >= cutoff_time]
    
    return clipped_data

# Function to find the first value at the start of the 24-hour period


def clip_to_last_1_hour(filtered_data):
    if not filtered_data:
        return []
    
    # Find the most recent timestamp
    most_recent_time = filtered_data[-1][0]
    
    # Calculate the cutoff time (1 hour before the most recent time)
    cutoff_time = most_recent_time - datetime.timedelta(hours=1)
    
    # Filter data to include only entries within the last 1 hour
    clipped_data = [(ts, count, sensor_name) for (ts, count, sensor_name) in filtered_data if ts >= cutoff_time]
    
    return clipped_data


# Main function for Streamlit app
def main():
    st.title("Sensor Data Dashboard")
    
    # Settings page
    settings = st.sidebar.selectbox("Select Page", ["Settings", "Main"])
    
    if settings == "Settings":
        st.header("Settings")
        
        # Local settings
        st.subheader("Local Settings")
        github_repo = st.text_input("GitHub Repository")
        github_access_key = st.text_input("GitHub Access Key", type="password")
        
        st.write("OR")
        uploaded_files = st.file_uploader("Manually upload .txt here", accept_multiple_files=True, type="txt")
        apply_button = st.button("Apply Settings")
        
        if apply_button:
            files = {}
            if github_repo and github_access_key:
                st.write("Retrieving data from GitHub...")
                file_names = [f"hall_effect_sensor_{i}.txt" for i in range(1, 9)]
                file_names.append("preferences.json")  # Add preferences.json to file list
                files.update(get_github_files(github_repo, github_access_key, file_names))
            if uploaded_files:
                for file in uploaded_files:
                    file_name = file.name
                    file_content = file.read().decode()
                    files[file_name] = file_content
                st.write("Uploaded files processed.")
            
            if not files:
                st.error("Failed to retrieve files from GitHub and no files uploaded.")
            else:
                st.success("Settings applied and files retrieved/uploaded successfully.")
                # Store files in session state to be used in Main page
                st.session_state.files = files
        
        # Counter settings
        st.subheader("Counter Settings")
        if "files" in st.session_state and "preferences.json" in st.session_state.files:
            preferences = st.session_state.files["preferences.json"]
        else:
            with open('preferences.json') as f:
                preferences = json.load(f)
        
        time_between_pushes = st.number_input("Time Between Pushes (minutes)", value=preferences['time_between_pushes_minutes'])
        sensor_names = preferences['sensor_names']
        for pin, name in sensor_names.items():
            sensor_names[pin] = st.text_input(f"Sensor Name for {pin}", value=name)
        character_lcd = st.checkbox("Character LCD", value=preferences['character_lcd'])
        uln2003_stepper = st.checkbox("ULN2003 Stepper", value=preferences['uln2003_stepper'])
        update_button = st.button("Update Counter Settings")
        
        if update_button:
            preferences = {
                "time_between_pushes_minutes": time_between_pushes,
                "sensor_names": sensor_names,
                "character_lcd": character_lcd,
                "uln2003_stepper": uln2003_stepper
            }
            with open('preferences.json', 'w') as f:
                json.dump(preferences, f, indent=4)
            
            if "files" in st.session_state:
                st.session_state.files["preferences.json"] = preferences
            
            st.write("Counter settings updated.")
        
        # Restore settings
        st.subheader("Restore")
        download_settings = st.download_button("Download Settings File", data=json.dumps(preferences), file_name="settings.json")
        restore_settings = st.file_uploader("Upload Settings File", type="json")
        
        if restore_settings:
            new_preferences = json.load(restore_settings)
            with open('preferences.json', 'w') as f:
                json.dump(new_preferences, f, indent=4)
            
            if "files" in st.session_state:
                st.session_state.files["preferences.json"] = new_preferences
            
            st.write("Settings restored.")
    
    elif settings == "Main":
        st.title("Sensor Data Dashboard - Main Page")
        
        # Ensure files have been retrieved or uploaded
        if "files" not in st.session_state or not st.session_state.files:
            st.error("No files found. Please apply settings on the Settings page first.")
            return
        
        files = st.session_state.files
        
        # Dropdown for selecting time frame
        setting = st.selectbox("Select Time Frame", ['all', 'twenty four', 'one hour'])
        
        # Create figure for Plotly chart
        fig = go.Figure()
        
        # Parse data based on selected time frame
        if setting == 'all':
            for file_name, file_content in files.items():
                if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                    filtered_data = read_and_filter_data(file_content)
                    
                    if filtered_data:
                        timestamps = [entry[0] for entry in filtered_data]
                        counts = [entry[1] for entry in filtered_data]
                        sensor_names = [entry[2] for entry in filtered_data]
                        
                        # Add trace to Plotly figure with sensor name as label
                        fig.add_trace(go.Scatter(x=timestamps, y=counts, mode='lines', name=sensor_names[0]))
            
            # Customize layout
            fig.update_layout(title='Sensor Data over Time',
                              xaxis_title='Time',
                              yaxis_title='Count',
                              hovermode='x unified')
        
        elif setting == 'twenty four':
            # Parse data from each .txt file and add to Plotly figure
            for file_name, file_content in files.items():
                if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                    filtered_data = read_and_filter_data(file_content)
                    if filtered_data:
                        # Clip data to the last 24 hours
                        filtered_data = clip_to_last_24_hours(filtered_data)
                        first_count = filtered_data[0][1]
                        if filtered_data:
                            timestamps = [entry[0] for entry in filtered_data]
                            counts = [entry[1]-first_count for entry in filtered_data]
                            sensor_names = [entry[2] for entry in filtered_data]
                            
                            # Add trace to Plotly figure with sensor name as label
                            fig.add_trace(go.Scatter(x=timestamps, y=counts, mode='lines', name=sensor_names[0]))
            
            # Customize layout
            fig.update_layout(title='Sensor Data over Time (Last 24 Hours)',
                              xaxis_title='Time',
                              yaxis_title='Count',
                              hovermode='x unified')
        
        elif setting == 'one hour':
            # Parse data from each .txt file and add to Plotly figure
            for file_name, file_content in files.items():
                if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                    filtered_data = read_and_filter_data(file_content)
                    if filtered_data:
                        # Clip data to the last 1 hour
                        filtered_data = clip_to_last_1_hour(filtered_data)
                        first_count = filtered_data[0][1]
                        if filtered_data:
                            timestamps = [entry[0] for entry in filtered_data]
                            counts = [entry[1]-first_count for entry in filtered_data]
                            sensor_names = [entry[2] for entry in filtered_data]
                            
                            # Add trace to Plotly figure with sensor name as label
                            fig.add_trace(go.Scatter(x=timestamps, y=counts, mode='lines', name=sensor_names[0]))
            
            # Customize layout
            fig.update_layout(title='Sensor Data over Time (Last 1 Hour)',
                              xaxis_title='Time',
                              yaxis_title='Count',
                              hovermode='x unified')
        
        # Render Plotly chart
        st.plotly_chart(fig)
if __name__ == "__main__":
    main()
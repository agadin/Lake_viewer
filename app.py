import streamlit as st
import json
from github import Github
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu


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

import plotly.graph_objects as go
import datetime

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

    lines = file_content.splitlines()


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


def clip_to_previous_24_hours(filtered_data):
    if not filtered_data:
        return []
    
    # Find the most recent timestamp
    most_recent_time = filtered_data[-1][0]
    
    # Calculate the cutoff times
    end_time = most_recent_time - datetime.timedelta(hours=24)
    start_time = end_time - datetime.timedelta(hours=24)
    
    # Filter data to include only entries within the 24-hour period before the last 24 hours
    clipped_data = [(ts, count, sensor_name) for (ts, count, sensor_name) in filtered_data if start_time <= ts < end_time]
    
    return clipped_data

# Function to clip data to the most recent 7am to 7am period
def clip_to_7am_period(filtered_data):
    if not filtered_data:
        return []
    
    # Find the most recent timestamp
    most_recent_time = filtered_data[-1][0]
    
    # Find the most recent 7am before the most recent timestamp
    most_recent_7am = most_recent_time.replace(hour=7, minute=0, second=0, microsecond=0)
    if most_recent_time.hour < 7:
        most_recent_7am -= datetime.timedelta(days=1)
    
    # Calculate the cutoff times for the last 7am to 7am period
    cutoff_time_start = most_recent_7am - datetime.timedelta(days=1)
    cutoff_time_end = most_recent_7am
    
    # Filter data to include only entries within the last 7am to 7am period
    clipped_data = [(ts, count, sensor_name) for (ts, count, sensor_name) in filtered_data if cutoff_time_start <= ts < cutoff_time_end]
    
    return clipped_data, cutoff_time_start, cutoff_time_end

# Function to clip data to the 7am to 7am period before the most recent one
def clip_to_previous_7am_period(filtered_data):
    if not filtered_data:
        return []
    
    # Find the most recent timestamp
    most_recent_time = filtered_data[-1][0]
    
    # Find the most recent 7am before the most recent timestamp
    most_recent_7am = most_recent_time.replace(hour=7, minute=0, second=0, microsecond=0)
    if most_recent_time.hour < 7:
        most_recent_7am -= datetime.timedelta(days=1)
    
    # Calculate the cutoff times for the previous 7am to 7am period
    cutoff_time_start = most_recent_7am - datetime.timedelta(days=2)
    cutoff_time_end = most_recent_7am - datetime.timedelta(days=1)
    
    # Filter data to include only entries within the previous 7am to 7am period
    clipped_data = [(ts, count, sensor_name) for (ts, count, sensor_name) in filtered_data if cutoff_time_start <= ts < cutoff_time_end]
    
    return clipped_data, cutoff_time_start, cutoff_time_end

# Function to calculate counts per 7am to 7am period
def calculate_counts_per_7am_period(filtered_data):
    if not filtered_data:
        return []
    
    counts_per_period = {}
    current_date = filtered_data[0][0].date()
    start_time = datetime.time(7, 0, 0)
    end_time = datetime.time(7, 0, 0)

    current_period_start = datetime.datetime.combine(current_date, start_time)
    current_period_end = datetime.datetime.combine(current_date, end_time)

    total_count = 0
    for timestamp, count, sensor_name in filtered_data:
        if timestamp >= current_period_start and timestamp < current_period_end:
            total_count = count
        elif timestamp >= current_period_end:
            counts_per_period[current_period_start.strftime('%Y-%m-%d %H:%M:%S')] = total_count
            # Move to the next 7am to 7am period
            current_date = timestamp.date()
            current_period_start = datetime.datetime.combine(current_date, start_time)
            current_period_end = datetime.datetime.combine(current_date + datetime.timedelta(days=1), end_time)
            total_count = count
    
    # Add the last period
    counts_per_period[current_period_start.strftime('%Y-%m-%d %H:%M:%S')] = total_count
    
    return counts_per_period

import numpy as np

def calculate_7am_to_7am_ranges(filtered_data):
    if not filtered_data:
        return pd.DataFrame()
    
    # Create a DataFrame from filtered_data
    df = pd.DataFrame(filtered_data, columns=['timestamp', 'count', 'sensor_name'])
    
    # Extract date and time components
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    
    # Group by date and calculate start/end timestamps for each 7am to 7am period
    df['7am_period'] = np.where(df['hour'] >= 7, df['date'], df['date'] - pd.Timedelta(days=1))
    df['7am_period_start'] = pd.to_datetime(df['7am_period']) + pd.Timedelta(hours=7)
    df['7am_period_end'] = df['7am_period_start'] + pd.Timedelta(hours=24)
    
    # Group by 7am periods and calculate range of counts
    ranges = df.groupby(['7am_period', 'sensor_name']).agg({
        'count': lambda x: x.max() - x.min()
    }).reset_index()
    
    # Pivot table to have sensors as columns and 7am periods as rows
    pivot_table = pd.pivot_table(ranges, values='count', index='7am_period', columns='sensor_name')
    
    return pivot_table





# Function to record timestamp in local time
def record_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Main function for Streamlit app
def main():
    selected2 = option_menu(None, ["Settings", "Home"], 
                           icons=['gear', 'house'], 
                           menu_icon="cast", default_index=0, orientation="horizontal")
   
    
    if selected2 == "Settings":
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
                st.session_state.github_repo = github_repo
                st.session_state.github_access_key = github_access_key
                st.session_state.file_names= file_names
                
                # Note refresh time 
                timestamp_last_refresh = record_timestamp()
                st.session_state.timestamp_last_refresh = timestamp_last_refresh
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
        is_from_device = True
        if "files" in st.session_state and "preferences.json" in st.session_state.files:
            preferences = st.session_state.files["preferences.json"]
            is_from_device = False
        else:
            try:
                with open('preferences.json') as f:
                    preferences = json.load(f)
            except FileNotFoundError:
                st.warning("Please connect to GitHub to modify preferences.")
                preferences = {
                    "time_between_pushes_minutes": 60,
                    "sensor_names": {
                        "D3": "Sensor 1",
                        "D4": "Sensor 2",
                        "D5": "Sensor 3",
                        "D6": "Sensor 4",
                        "D7": "Sensor 5",
                        "D8": "Sensor 6",
                        "D9": "Sensor 7",
                        "D41": "Sensor 8"
                    },
                    "character_lcd": True,
                    "uln2003_stepper": False
                }
        
        # Display settings and indicate if they are from device or GitHub
        if is_from_device:
            st.write("Local Counter Settings (From Device)")
        else:
            st.write("Counter Settings (From GitHub)")
        
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
            
            # Update last updated time
            st.session_state.last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            st.write("Counter settings updated.")
        
        # Display last updated time for preferences.json
        if "last_update_time" in st.session_state:
            st.write(f"Last Updated: {st.session_state.last_update_time}")
     
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
    
    elif selected2 == "Home":
        
        # Ensure files have been retrieved or uploaded
        if "files" not in st.session_state or not st.session_state.files:
            st.error("No files found. Please apply settings on the Settings page first.")
            return
        
        files = st.session_state.files
        
        
        # Dropdown for selecting time frame        
        
        
        #Second section Metric Setting 
        metric_timeframe = st.selectbox("Select Metric Time Frame", ['Last 24 Hours Available', 'Last 7am to 7am Period'], help='Indicate the tim range for metrics. Note the secondary numbers are change from previous time point.')
        
        if metric_timeframe == 'Last 24 Hours Available':
            # Initialize variables to store total counts
            total_counts_24 = {}
            total_counts_24_prev = {}
            sensor_names_24_out = {}
            
            for i, (file_name, file_content) in enumerate(files.items(), start=1):
                if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                    filtered_data = read_and_filter_data(file_content)
                    if filtered_data:
                        # Clip data to the last 24 hours
                        filtered_data_24 = clip_to_last_24_hours(filtered_data)
                        if filtered_data_24:
                            first_count_24 = filtered_data_24[0][1]
                            timestamps_24 = [entry[0] for entry in filtered_data_24]
                            counts_24 = [entry[1] - first_count_24 for entry in filtered_data_24]
                            sensor_names_24 = [entry[2] for entry in filtered_data_24]
                            total_counts_24[f'total_counts_24_hall_{i}'] = max(counts_24)
                            
                            start_time_24 = timestamps_24[0].strftime('%Y-%m-%d %H:%M:%S')
                            end_time_24 = timestamps_24[-1].strftime('%Y-%m-%d %H:%M:%S')
                            sensor_names_24_out[i]=sensor_names_24[-1]
                        # Clip data to the previous 24 hours
                        filtered_data_prev_24 = clip_to_previous_24_hours(filtered_data)
                        if filtered_data_prev_24:
                            first_count_prev_24 = filtered_data_prev_24[0][1]
                            counts_prev_24 = [entry[1] - first_count_prev_24 for entry in filtered_data_prev_24]
                            total_counts_24_prev[f'total_counts_24_hall_{i}'] = max(counts_prev_24)
                        else:
                            total_counts_24_prev[f'total_counts_24_hall_{i}'] = 0
            
            # Display total counts and deltas in a 4-column by 2-row grid
            cols = st.columns(4)
            for i, (key, value) in enumerate(total_counts_24.items()):
                col = cols[i % 4]
                delta = value - total_counts_24_prev[key]
                sensor_name = sensor_names_24_out[i+1]
                col.metric(f"Total Counts {sensor_name}", value, delta)
                
            
            st.markdown(f"**Date Range for Last 24 Hours**: {start_time_24} to {end_time_24}", help='Time range for data values shown above. Note: Date range may appear to be greater than 24 hours due to how the date increases at midnight, this is normal.')
            
        elif metric_timeframe == 'Last 7am to 7am Period':
            total_counts_7am = {}
            total_counts_7am_prev = {}
            date_ranges_7am = {}
            date_ranges_7am_prev = {}
            sensor_names_7am_out = {}
            
            # Parse data from each .txt file and add to Plotly figure
            for i, (file_name, file_content) in enumerate(files.items(), start=1):
                if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                    filtered_data = read_and_filter_data(file_content)
                    if filtered_data:
                        # Clip data to the last 7am to 7am period
                        filtered_data_7am, cutoff_time_start_7am, cutoff_time_end_7am = clip_to_7am_period(filtered_data)
                        if filtered_data_7am:
                            first_count_7am = filtered_data_7am[0][1]
                            timestamps_7am = [entry[0] for entry in filtered_data_7am]
                            counts_7am = [entry[1] - first_count_7am for entry in filtered_data_7am]
                            sensor_names_7am = [entry[2] for entry in filtered_data_7am]
                            total_counts_7am[f'total_counts_7am_hall_{i}'] = max(counts_7am)
                            date_ranges_7am[f'total_counts_7am_hall_{i}'] = f"{cutoff_time_start_7am.strftime('%Y-%m-%d %H:%M:%S')} to {cutoff_time_end_7am.strftime('%Y-%m-%d %H:%M:%S')}"
                            
                            sensor_names_7am_out[i]=sensor_names_7am[-1]
                        
                        # Clip data to the previous 7am to 7am period
                        filtered_data_prev_7am, cutoff_time_start_prev_7am, cutoff_time_end_prev_7am = clip_to_previous_7am_period(filtered_data)
                        if filtered_data_prev_7am:
                            first_count_prev_7am = filtered_data_prev_7am[0][1]
                            counts_prev_7am = [entry[1] - first_count_prev_7am for entry in filtered_data_prev_7am]
                            total_counts_7am_prev[f'total_counts_7am_hall_{i}'] = max(counts_prev_7am)
                            date_ranges_7am_prev[f'total_counts_7am_hall_{i}'] = f"{cutoff_time_start_prev_7am.strftime('%Y-%m-%d %H:%M:%S')} to {cutoff_time_end_prev_7am.strftime('%Y-%m-%d %H:%M:%S')}"
                        else:
                            total_counts_7am_prev[f'total_counts_7am_hall_{i}'] = 0

            
            
            cols = st.columns(4)
            for i, (key, value) in enumerate(total_counts_7am.items()):
                col = cols[i % 4]
                delta = value - total_counts_7am_prev[key]
                sensor_name = sensor_names_7am_out[i+1]
                col.metric(f"Total Counts {sensor_name}", value, delta)
                
            # Display the first date range below the metrics
            first_key = next(iter(date_ranges_7am))
            first_date_range = date_ranges_7am[first_key]
            st.markdown(f"**Date Range for Displayed Data**: {first_date_range}", help='Time range for data values shown above. Note: Date range may appear to be greater than 24 hours due to how the date increases at midnight, this is normal.')
            
            
            
        #Second section
        # Create figure for Plotly chart
        setting = st.selectbox("Select Time Frame", ['All', 'Last 24 Hours Available', 'Last Hour Avaible'], help='Select the time frame to be displayed in the figure')

        fig = go.Figure()
        
        # Parse data based on selected time frame
        if setting == 'All':
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
        
        elif setting == 'Last 24 Hours Available':
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
        
        elif setting == 'Last Hour Avaible':
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
        
        
       #third section
        # Initialize DataFrame for display
        ranges_df = pd.DataFrame()
        
        # Process each file for 7am to 7am periods
        for file_name, file_content in files.items():
            if file_name.startswith("hall_effect_sensor_") and file_name.endswith(".txt"):
                filtered_data = read_and_filter_data(file_content)
                if filtered_data:
                    ranges_data = calculate_7am_to_7am_ranges(filtered_data)
                    ranges_df = pd.concat([ranges_df, ranges_data], axis=1)
        
        # Display the ranges DataFrame using Plotly bar charts
        st.subheader("Ranges of Counts per 7am to 7am Periods")
        
        # Create a figure for Plotly bar chart
        fig = go.Figure()
        
        # Add bar traces for each sensor
        for sensor_name in ranges_df.columns:
            fig.add_trace(go.Bar(x=ranges_df.index, y=ranges_df[sensor_name], name=sensor_name))
        
        # Customize layout
        fig.update_layout(
            barmode='group',
            xaxis_tickangle=-45,
            xaxis=dict(title='7am to 7am Period'),
            yaxis=dict(title='Range of Counts'),
            legend=dict(title='Sensor'),
            title='Ranges of Counts per 7am to 7am Periods'
        )
        
        # Display the Plotly figure using st.plotly_chart
        st.plotly_chart(fig)
                    
            
        with st.expander("Raw 7am to 7am data"):
            
            # Calculate counts per 7am to 7am period all
            

            # Display the ranges DataFrame
            st.dataframe(ranges_df)
            # Check if refresh button is clicked
        # Button to refresh data
        if st.button("Refresh Data"):
            # Check if GitHub credentials are defined
            github_repo_s = st.session_state.get('github_repo')
            github_access_key_s = st.session_state.get('github_access_key')
            
            if github_repo_s and github_access_key_s:
                file_names_s = st.session_state.get('file_names', [])
                st.write("Refreshing data...")
                files.update(get_github_files(github_repo_s, github_access_key_s, file_names_s))
                
                # Record the timestamp of last refresh
                timestamp_last_refresh = record_timestamp()
                st.session_state.timestamp_last_refresh = timestamp_last_refresh
                
                # Display confirmation
                st.write("Data refreshed successfully!")
            
            else:
                st.error('GitHub repository name or access key is not defined. Please apply settings first.')
    
        # Display last refreshed timestamp
        if 'timestamp_last_refresh' in st.session_state:
            st.write(f"Last Refreshed: {st.session_state.timestamp_last_refresh}")


if __name__ == "__main__":
    main()
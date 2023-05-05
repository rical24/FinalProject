"""
Name: Ricardo Rodriguez
CS230: Section 3
Data: ShipwrecksDatabase.csv
Description:
This program analyzes a shipwrecks database and displays the top 3 locations with the highest occurrences of shipwrecks,
a bar chart of these occurrences, and a map showing the shipwrecks locations. The program allows users to filter the
data by year and choose the number of top locations to display.
"""
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk
import re

def load_data():
    # Read CSV file
    df = pd.read_csv("ShipwreckDatabase.csv")

    # Convert the 'LOCATION LOST' column to string and remove the last 7 characters
    df['Location Lost Short'] = df['LOCATION LOST'].astype(str).apply(lambda x: x.strip()[:-7] if isinstance(x, str) and len(x.strip()) > 15 else x)

    return df

def get_top_n_locations(df, n=3):
    return df['Location Lost Short'].value_counts().nlargest(n)

def plot_top_n_locations(locations_counts):
    fig, ax = plt.subplots()
    ax.bar(locations_counts.index, locations_counts.values)
    ax.set_xlabel('Locations')
    ax.set_ylabel('Occurrences')
    ax.set_title('Top Locations with Highest Occurrences of Shipwrecks')

    return fig

def filter_top_n_locations(df, top_n_occurrences):
    # Convert the top_n_occurrences Series to a DataFrame
    top_n_locations_df = top_n_occurrences.reset_index().rename(columns={'index': 'Location Lost Short', 'Location Lost Short': 'count'})

    # Get the list of top_n locations
    top_n_locations_list = top_n_locations_df['Location Lost Short'].values.tolist()

    # Filter the DataFrame to keep only the rows that belong to the top_n_locations
    filtered_df = df[df['Location Lost Short'].isin(top_n_locations_list)].copy()

    return filtered_df


def get_top_n_departure_ports(df, n=3):
        return df['DEPARTURE PORT'].value_counts().nlargest(n)

def plot_top_n_departure_ports(departure_ports_counts):
        fig, ax = plt.subplots()
        ax.bar(departure_ports_counts.index, departure_ports_counts.values)
        ax.set_xlabel('Departure Ports')
        ax.set_ylabel('Occurrences')
        ax.set_title('Top Departure Ports with Highest Occurrences of Shipwrecks')

        return fig

def sanitize_string(s):
    return re.sub(r'[^a-zA-Z0-9 ]', '', s)

def main():
    st.title("Shipwreck Analysis")

    df = load_data()

    st.sidebar.header("Filter Data")
    min_year = int(df["YEAR"].min())
    max_year = int(df["YEAR"].max())
    selected_years = st.sidebar.slider("Select a year range for shipwrecks", min_year, max_year, (min_year, max_year))

    top_n = st.sidebar.number_input("Number of top locations to display", min_value=1, max_value=10, value=3, step=1)

    # Filter data by selected years
    filtered_df = df[(df["YEAR"] >= selected_years[0]) & (df["YEAR"] <= selected_years[1])]

    # Display the top n highest occurrences of locations lost
    top_n_occurrences = get_top_n_locations(filtered_df, n=top_n)
    st.write(f"Top {top_n} Locations with Highest Occurrences of Shipwrecks (within selected year range):")
    st.write(top_n_occurrences)

    # Plot the top n locations using a bar chart
    chart = plot_top_n_locations(top_n_occurrences)
    st.pyplot(chart)

    # Display the top n highest occurrences of departure ports
    top_n_departure_ports = get_top_n_departure_ports(filtered_df, n=top_n)
    st.write(f"Top {top_n} Departure Ports with Highest Occurrences of Shipwrecks (within selected year range):")
    st.write(top_n_departure_ports)

    # Filter out rows with non-numeric latitude and longitude values
    filtered_df = filtered_df.dropna(subset=["LATITUDE_BACKUP", "LONGITUDE_BACKUP"])

    # Convert the latitude and longitude to numeric format
    filtered_df["LATITUDE_BACKUP"] = pd.to_numeric(filtered_df["LATITUDE_BACKUP"], errors='coerce')
    filtered_df["LONGITUDE_BACKUP"] = pd.to_numeric(filtered_df["LONGITUDE_BACKUP"], errors='coerce')

    # Filter dataset to include only the top_n_locations
    top_n_locations_df = filter_top_n_locations(filtered_df, top_n_occurrences)

    # Remove rows with NaN values in the latitude and longitude columns
    top_n_locations_df = top_n_locations_df.dropna(subset=["LATITUDE_BACKUP", "LONGITUDE_BACKUP"])

    # Convert 'Location Lost Short' column to string type
    top_n_locations_df['Location Lost Short'] = top_n_locations_df['Location Lost Short'].astype(str)

    # Sanitize 'Location Lost Short' column
    top_n_locations_df['Location Lost Short'] = top_n_locations_df['Location Lost Short'].apply(sanitize_string)

    json_data = top_n_locations_df.to_json(orient="records")

    # Display the map using PyDeck for top_n_locations if the filtered dataset of Longitude & Latitude are not empty
    if not top_n_locations_df.empty:
        st.subheader(f"Map of Top {top_n} Locations with Highest Occurrences of Shipwrecks")
        '''
        scatterplot_layer = pdk.Layer("ScatterplotLayer", data=json_data,
                                       get_position=["LONGITUDE_BACKUP", "LATITUDE_BACKUP"],
                                       get_radius=5000, get_fill_color="[180, 0, 200, 140]", pickable=True) '''
        scatterplot_layer = pdk.Layer("ScatterplotLayer", data=json_data,
                                      get_position=["LONGITUDE_BACKUP", "LATITUDE_BACKUP"],
                                      get_radius=100000,
                                      get_fill_color="[255, 0, 0, 140]",
                                      pickable=True,
                                      auto_highlight=True,
                                      filled=True)
        deck = pdk.Deck(layers=[scatterplot_layer], initial_view_state={
            "latitude": top_n_locations_df["LATITUDE_BACKUP"].mean(),
            "longitude": top_n_locations_df["LONGITUDE_BACKUP"].mean(),
            "zoom": 2,
            "pitch": 0,
            "bearing": 0
        })
        st.pydeck_chart(deck)
    else:
        st.warning("No data available for the selected top locations.")

if __name__ == "__main__":
    main()

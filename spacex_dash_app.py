# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
path = "/home/claudio/Documents/Coursera/notes/data_science/Capstone/week_3/spacex_launch_dash.csv"
spacex_df = pd.read_csv(path)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                    dcc.Dropdown(id='site-dropdown',
                                                options=[{'label': 'All Sites', 'value': 'ALL'}] +
                                                    [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                                value='ALL',
                                                placeholder='Select a Launch Site here',
                                                searchable=True),
                                    html.Br(),


                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: f'{i}' for i in range(0, 10001, 1000)},  # Adjust marks to include every 1000 kg up to 10000 kg
                                    value=[min_payload, max_payload]
                                ),
                                html.Div(id='output-payload-slider'),


                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
                                
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Filter data for successful launches only if needed or use the entire dataset based on your criteria
        filtered_df = spacex_df[spacex_df['class'] == 1]  # Assuming 'class' indicates success
        # Create a pie chart for all sites
        fig = px.pie(filtered_df, values='class', 
                    names='Launch Site', 
                    title='Total Successful Launches for All Sites')
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts()
        # Define the labels and colors explicitly
        labels = {0: 'Failures', 1: 'Successes'}
        colors = ['#FF0000', '#0000FF']  # Red for failures, Blue for successes

        # Create the labels in the correct order

        # Map the colors to the custom labels
        color_map = {'Failures': '#ef553b ', 'Successes': '#636efa'}

        # Plot the pie chart with correct labels and consistent colors
        fig = px.pie(
            values=success_counts, 
            names=[labels[key] for key in success_counts.index],
            color=[labels[key] for key in success_counts.index],
            color_discrete_map=color_map,
            labels=labels,
            title=f"Success vs. Failed Launches for {entered_site}"
        )
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)

def update_scatter_plot(selected_site, selected_payload_range):
    # Filter data based on the payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
                            (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])]

    if selected_site == 'ALL':
        # If 'ALL' sites are selected, use the filtered data without further site-based filtering
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         labels={"class": "Launch Outcome"},
                         title="Launch Outcome by Payload Mass across All Sites")
    else:
        # If a specific site is selected, filter data for that site
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(site_filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         labels={"class": "Launch Outcome"},
                         title=f"Launch Outcome by Payload Mass for {selected_site}")

    # Update the layout if necessary
    fig.update_layout(xaxis_title="Payload Mass (kg)",
                      yaxis_title="Launch Outcome",
                      legend_title="Booster Version")
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import base64
import os
import tempfile
from io import BytesIO
from PIL import Image
import numpy as np
import plotly.graph_objects as go
from backend import Backend

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    # Container for the "Select Image" button and sliders
    html.Div([
        # File upload button
        dcc.Upload(
            id='upload-image',
            children=html.Button('Select Image', style={'padding': '10px', 'font-size': '16px'}),
            multiple=False
        ),

        html.Label('Noise Kernel Size (1-10):'),
        html.Div(
            dcc.Slider(
                id='noise-slider',
                min=1,
                max=10,
                step=1,
                value=3,
                marks={i: str(i) for i in range(1, 11)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            style={'width': '80%', 'margin': '10px auto'}
        ),
        html.Label('Close Kernel Size (1-10):'),
        html.Div(
            dcc.Slider(
                id='close-slider',
                min=1,
                max=10,
                step=1,
                value=5,
                marks={i: str(i) for i in range(1, 11)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            style={'width': '80%', 'margin': '10px auto'}
        ),

        # Sliders for image processing parameters
        html.Div([
            html.Label('Blur Kernel Size (2-10):'),
            html.Div(
                dcc.Slider(
                    id='blur-slider',
                    min=2,
                    max=10,
                    step=1,
                    value=7,
                    marks={i: str(i) for i in range(2, 11)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                style={'width': '80%', 'margin': '10px auto'}
            ),
            html.Label('Morphological Operation Kernel (2-10):'),
            html.Div(
                dcc.Slider(
                    id='morph-slider',
                    min=2,
                    max=10,
                    step=1,
                    value=5,
                    marks={i: str(i) for i in range(2, 11)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                style={'width': '80%', 'margin': '10px auto'}
            ),
            html.Label('Contour Area Threshold (50-150):'),
            html.Div(
                dcc.Slider(
                    id='contour-thresh-slider',
                    min=50,
                    max=150,
                    step=1,
                    value=115,
                    marks={i: str(i) for i in range(50, 151, 10)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                style={'width': '80%', 'margin': '10px auto'}
            ),
            # Roundness Threshold Slider
            html.Label('Roundness Threshold (0.2 - 1):'),
            html.Div(
                dcc.Slider(
                    id='roundness-thresh-slider',
                    min=0.2,
                    max=1,
                    step=0.05,
                    value=0.35,
                    marks={
                        int(i * 0.05) if (i * 0.05) % 1 == 0 else round(i * 0.05, 2): 
                        str(int(i * 0.05)) if (i * 0.05) % 1 == 0 else str(round(i * 0.05, 2)) 
                        for i in range(4, 21)
                    },
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                style={'width': '80%', 'margin': '10px auto'}
            ),
        ], style={'textAlign': 'center', 'marginTop': '20px', 'marginBottom': '20px'}),
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),  # Center the button and sliders

    # Horizontal rule with margin for separation
    html.Hr(style={'marginTop': '20px', 'marginBottom': '20px'}),

    # Container to display the Plotly image
    html.Div(id='output-image-upload', 
             style={'height': 'auto', 'width': '100%', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center'})
])

# Define callback to update the image display and apply processing
@app.callback(
    Output('output-image-upload', 'children'),
    Input('upload-image', 'contents'),
    Input('noise-slider', 'value'),
    Input('close-slider', 'value'),
    Input('blur-slider', 'value'),
    Input('morph-slider', 'value'),
    Input('contour-thresh-slider', 'value'),
    Input('roundness-thresh-slider', 'value')  # Include the new slider input
)
def update_image(image_contents, noise_kernel, close_kernel, blur_kernel, morph_kernel, area_thresh, roundness_thresh):
    # If no image is uploaded, return a message to upload one
    if image_contents is None:
        return 'Upload an image to display.'

    try:
        # Decode the image from base64
        content_type, content_string = image_contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Save the decoded image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            tmp_file.write(decoded)
            tmp_file_path = tmp_file.name  # This is the absolute file path

        # Now pass the file path to the Backend class
        final_image, num_barnacles = Backend(tmp_file_path, noise_kernel, close_kernel, blur_kernel, morph_kernel, area_thresh, roundness_thresh).count()

        # Convert the processed image back to a Plotly-compatible format
        processed_image = np.array(final_image)

        # Create a Plotly figure with the processed image
        fig = go.Figure(go.Image(z=processed_image))

        # Adjust the layout of the figure to fit in the container
        fig.update_layout(
            xaxis={
                'showgrid': False, 
                'zeroline': False, 
                'showticklabels': False, 
                'scaleanchor': 'y'  # Constrains the x-axis to the aspect ratio of the y-axis
            },
            yaxis={
                'showgrid': False, 
                'zeroline': False, 
                'showticklabels': False, 
                'scaleanchor': 'x'  # Constrains the y-axis to the aspect ratio of the x-axis
            },
            margin=dict(l=0, r=0, t=0, b=0),  # Remove margins around the image
            dragmode='zoom',  # Enable zooming
            hovermode='closest',  # Show data point details on hover (optional)
            title="Zoom and Pan Enabled",  # Optional title
        )

        # Return both the figure and the barnacle count as text
        return html.Div(
            children=[
                dcc.Graph(
                    figure=fig,
                    config={
                        'displayModeBar': True,  # Show the mode bar for interaction options
                        'scrollZoom': True,      # Enable zooming with mouse scroll
                        'doubleClick': 'reset',  # Reset zoom on double click
                        'showTips': False,       # Disable hover tips for cleaner display
                        'displaylogo': False,    # Hide the Plotly logo
                        'modeBarButtonsToRemove': ['toImage', 'resetScale2d'],  # Optional: Customize the mode bar
                        'modeBarButtonsToAdd': [
                            'zoom2d', 'pan2d', 'resetScale2d', 'zoomIn2d', 'zoomOut2d'
                        ]
                    }
                ),
                # Display the number of barnacles
                html.Div(
                    children=f'Number of Barnacles Detected: {num_barnacles}',
                    style={'textAlign': 'center', 'fontSize': '20px', 'marginTop': '20px'}
                )
            ],
            style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}
        )

    except Exception as e:
        # Return error message in case something goes wrong with the image processing
        return f"Error processing image: {e}"

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
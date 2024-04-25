from dash import Dash, html, dash_table, dcc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import itertools

df = pd.read_csv('../display/monitor_datasets/monitor_started_at_2024_04_21_11_31_32_964152.csv')

# Initialize the app
app = Dash(__name__)

battleships = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12",
        "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12",
        "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12",
        "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12",
        "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12",
        "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
        "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10", "G11", "G12",
        "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12"
]

df = pd.read_csv("../display/monitor_datasets/monitor_started_at_2024_04_21_11_43_03_287450.csv")

# App layout
fig = make_subplots(rows=8, cols=12, shared_xaxes = True, shared_yaxes = True)

for idx, (row, col) in enumerate(itertools.product(range(8), range(12))):
    print(idx, row, col)
    fig.add_trace(
    go.Scatter(x=df[f"seconds_since_start"], y=df[f"V_electrode_{idx}"]), row=row + 1, col=col + 1)
fig.update_layout(height=600, width=800, title_text="Side By Side Subplots")

app.layout = html.Div(className = 'wrapper',
                      children = dcc.Graph(figure = fig))

# if __name__ == '__main__':
app.run(debug=True)

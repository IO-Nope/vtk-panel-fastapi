import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.responses import HTMLResponse as HTMLR

app = FastAPI()

template = pn.template.BootstrapTemplate(title='Bootstrap Template')

xs = np.linspace(0, np.pi)
freq = pn.widgets.FloatSlider(name="Frequency", start=0, end=10, value=2)
phase = pn.widgets.FloatSlider(name="Phase", start=0, end=np.pi)

def sine(freq, phase):
    return pd.DataFrame(dict(y=np.sin(xs*freq+phase)), index=xs)

def cosine(freq, phase):
    return pd.DataFrame(dict(y=np.cos(xs*freq+phase)), index=xs)

dfi_sine = hvplot.bind(sine, freq, phase).interactive()
dfi_cosine = hvplot.bind(cosine, freq, phase).interactive()

plot_opts = dict(responsive=True, min_height=400)

template.sidebar.append(freq)

template.sidebar.append(phase)

template.main.append(
    pn.Row(
        pn.Card(dfi_sine.hvplot(**plot_opts).output(), title='Sine'),
        pn.Card(dfi_cosine.hvplot(**plot_opts).output(), title='Cosine'),
    )
)


pn.serve(
    template,
    port=5006,
    allow_websocket_origin=["127.0.0.1:5006", "localhost:5006"],  
    show=True,
    )


@app.get("/panel",response_class=HTMLR)
def server_panel():
    return RedirectResponse(url="http://localhost:5006")

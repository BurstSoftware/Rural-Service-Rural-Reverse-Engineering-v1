rural-re/
├── app.py
├── pages/
│   ├── 1_Upload.py              # kept — CSV / JSON / GeoJSON only
│   ├── 2_Map_Viewer.py          # renamed from 2_Viewer.py
│   ├── 3_Place_Directory.py     # renamed from 3_Measure.py
│   └── 4_Place_Reports.py       # renamed from 4_Reports.py
├── src/
│   ├── __init__.py
│   ├── io_loaders.py            # geojson / json / csv + column aliases
│   ├── geo.py
│   ├── places.py                # NEW — cascading state/city/county/zip/road/address
│   └── viz.py
├── data/
│   └── sample_places.geojson    # optional demo
├── requirements.txt
└── .streamlit/config.toml

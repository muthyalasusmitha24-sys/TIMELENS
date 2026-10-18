# 🏺 TimeLens AI

Upload a photo of a sculpture, temple, coin, inscription, manuscript or artifact and explore it:
identification, period/civilization/origin, evidence, script reading, timeline, map, knowledge graph,
similar museum objects (The Met + Art Institute of Chicago), region questions, AI historian chat,
Explorer / Student / Archaeologist / Story modes, live camera, and a downloadable Virtual Museum.

No API key? The app runs in **demo mode** with clearly labelled sample data.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Optional key: copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your Anthropic key.

## Deploy: GitHub → Streamlit Community Cloud
1. Create a new GitHub repo and push this folder (never commit `secrets.toml`; it is git-ignored).
2. Go to share.streamlit.io → **New app** → pick the repo, branch `main`, main file `app.py`.
3. **Advanced settings → Secrets**: paste `ANTHROPIC_API_KEY = "sk-ant-..."`.
4. Deploy. (If you skip the secret, visitors can paste their own key in the sidebar, otherwise demo mode.)

Tip: a key in Secrets means every visitor spends YOUR credits. Set a spend limit in the Anthropic console,
or leave Secrets empty and let users bring their own key.

## Tests
```bash
pip install pytest && python -m pytest
```
Model can be changed with the `TIMELENS_MODEL` environment variable (default `claude-sonnet-5-5`).

## Notes
AI identifications, dates and script translations are estimates. Verify with scholarly sources.

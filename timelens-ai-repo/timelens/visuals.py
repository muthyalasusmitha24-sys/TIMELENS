"""Plotly figures: timeline, map, knowledge graph."""
import math

import networkx as nx
import plotly.graph_objects as go

from .schema import fmt_year

COLORS = {"dynasty": "#d4a017", "architecture": "#c0714f", "trade": "#4f9dc0", "religion": "#a06fd0",
          "war": "#d05050", "object": "#6fd08c", "event": "#c9b99a", "person": "#e0a0c0",
          "technique": "#7fd0c8", "style": "#e0c070", "other": "#a89f8c"}
BG = "rgba(0,0,0,0)"


def _layout(fig, h=420):
    fig.update_layout(height=h, paper_bgcolor=BG, plot_bgcolor=BG, font=dict(color="#f1e6d0"),
                      margin=dict(l=10, r=10, t=30, b=10))
    return fig


def timeline_fig(a):
    ev = a["timeline"]
    if not ev:
        return None
    fig = go.Figure()
    ys = [(-1) ** i * (1 + (i % 3) * 0.6) for i in range(len(ev))]
    fig.add_trace(go.Scatter(x=[e["year"] for e in ev], y=[0] * len(ev), mode="lines",
                             line=dict(color="#8a7a5a", width=2), hoverinfo="skip", showlegend=False))
    for e, y in zip(ev, ys):
        fig.add_trace(go.Scatter(x=[e["year"], e["year"]], y=[0, y], mode="lines",
                                 line=dict(color="#5a4e38", width=1), hoverinfo="skip", showlegend=False))
    for kind in sorted({e["kind"] for e in ev}):
        pts = [(e, y) for e, y in zip(ev, ys) if e["kind"] == kind]
        fig.add_trace(go.Scatter(
            x=[p[0]["year"] for p in pts], y=[p[1] for p in pts], mode="markers+text", name=kind,
            marker=dict(size=14, color=COLORS.get(kind, "#c9b99a")),
            text=[p[0]["event"][:38] for p in pts], textposition="top center", textfont=dict(size=10),
            hovertext=[f"{fmt_year(p[0]['year'])}: {p[0]['event']}" for p in pts], hoverinfo="text"))
    p = a["period"]
    if p["start_year"] is not None and p["end_year"] is not None:
        fig.add_vrect(x0=p["start_year"], x1=p["end_year"], fillcolor="#d4a017", opacity=0.15, line_width=0,
                      annotation_text=p["label"], annotation_position="top left")
    fig.update_yaxes(visible=False, range=[-3, 3])
    fig.update_xaxes(title="Year (negative = BCE)", gridcolor="#3a3224")
    return _layout(fig, 460)


def map_fig(a):
    pts = list(a["map_points"])
    o = a["origin"]
    if not pts and o["lat"] is not None and o["lon"] is not None:
        pts = [{"name": o["place"], "lat": o["lat"], "lon": o["lon"], "role": "Origin"}]
    if not pts:
        return None
    fig = go.Figure(go.Scattergeo(
        lat=[p["lat"] for p in pts], lon=[p["lon"] for p in pts], mode="markers+text",
        text=[p["name"] for p in pts], textposition="top right",
        hovertext=[f"{p['name']}: {p['role']}" for p in pts], hoverinfo="text",
        marker=dict(size=11, color="#d4a017", line=dict(width=1, color="#fff"))))
    fig.update_geos(projection_type="natural earth", showland=True, landcolor="#2e2619", showocean=True,
                    oceancolor="#16222b", showcountries=True, countrycolor="#5a4e38", bgcolor=BG,
                    fitbounds="locations")
    return _layout(fig, 460)


def graph_fig(a):
    g = a["graph"]
    if not g["nodes"]:
        return None
    G = nx.Graph()
    for n in g["nodes"]:
        G.add_node(n["id"], group=n["group"])
    for e in g["edges"]:
        G.add_edge(e["source"], e["target"], label=e["label"])
    pos = nx.spring_layout(G, seed=7, k=1.4 / math.sqrt(max(len(G), 1)))
    fig = go.Figure()
    for u, v, d in G.edges(data=True):
        fig.add_trace(go.Scatter(x=[pos[u][0], pos[v][0]], y=[pos[u][1], pos[v][1]], mode="lines",
                                 line=dict(color="#6a5d45", width=1.5), hoverinfo="skip", showlegend=False))
        fig.add_annotation(x=(pos[u][0] + pos[v][0]) / 2, y=(pos[u][1] + pos[v][1]) / 2, text=d["label"],
                           showarrow=False, font=dict(size=9, color="#b8a98a"))
    for grp in sorted({d["group"] for _, d in G.nodes(data=True)}):
        ns = [n for n, d in G.nodes(data=True) if d["group"] == grp]
        fig.add_trace(go.Scatter(x=[pos[n][0] for n in ns], y=[pos[n][1] for n in ns], mode="markers+text",
                                 name=grp, text=ns, textposition="bottom center", hoverinfo="text",
                                 marker=dict(size=22, color=COLORS.get(grp, "#a89f8c"),
                                             line=dict(width=1, color="#fff"))))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _layout(fig, 520)

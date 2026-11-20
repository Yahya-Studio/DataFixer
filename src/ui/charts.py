"""Interactive Plotly visualizations for DataFixer."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Consistent modern SaaS color palette
THEME_BG = "rgba(0,0,0,0)"
THEME_TEXT = "#cbd5e1"
THEME_GRID = "#334155"
PRIMARY_COLOR = "#6366f1"
SUCCESS_COLOR = "#10b981"
WARNING_COLOR = "#f59e0b"
DANGER_COLOR = "#ef4444"


def _apply_saas_layout(fig: go.Figure, title: str = "", height: int = 340) -> go.Figure:
    """Apply uniform SaaS styling across all charts."""
    fig.update_layout(
        title={"text": title, "font": {"family": "Cairo, sans-serif", "size": 15, "color": "#f8fafc"}},
        paper_bgcolor=THEME_BG,
        plot_bgcolor=THEME_BG,
        height=height,
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        font={"family": "Cairo, sans-serif", "color": THEME_TEXT, "size": 12},
        hoverlabel={"bgcolor": "#1e293b", "font_size": 12, "font_family": "Cairo, sans-serif"},
    )
    return fig


def plot_missing_values_bar(df: pd.DataFrame) -> go.Figure | None:
    """Horizontal bar chart showing missing values percentage across columns."""
    null_counts = df.isna().sum()
    null_cols = null_counts[null_counts > 0].sort_values(ascending=True)

    if null_cols.empty:
        return None

    pcts = (null_cols / len(df)) * 100
    fig = go.Figure(
        go.Bar(
            x=pcts.values,
            y=null_cols.index.tolist(),
            orientation="h",
            marker={
                "color": pcts.values,
                "colorscale": [[0.0, "#fde68a"], [0.5, "#f59e0b"], [1.0, "#ef4444"]],
                "showscale": False,
            },
            text=[f"{cnt:,} ({pct:.1f}%)" for cnt, pct in zip(null_cols.values, pcts.values)],
            textposition="auto",
        )
    )
    fig.update_xaxes(
        title="نسبة القيم المفقودة (%)", gridcolor=THEME_GRID, range=[0, max(100, max(pcts.values) * 1.15)]
    )
    fig.update_yaxes(gridcolor=THEME_GRID)
    return _apply_saas_layout(fig, "توزيع القيم المفقودة حسب الأعمدة")


def plot_duplicates_donut(total_rows: int, duplicate_rows: int) -> go.Figure:
    """Donut chart illustrating unique vs duplicate rows ratio."""
    unique_rows = max(0, total_rows - duplicate_rows)
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["صفوف فريدة (Unique)", "صفوف مكررة (Duplicate)"],
                values=[unique_rows, duplicate_rows],
                hole=0.65,
                marker={"colors": [SUCCESS_COLOR, DANGER_COLOR if duplicate_rows > 0 else "#64748b"]},
                textinfo="percent+label",
            )
        ]
    )
    return _apply_saas_layout(fig, "نسبة التكرارات في البيانات", height=280)


def plot_dtypes_donut(df: pd.DataFrame) -> go.Figure:
    """Donut chart showing composition of data types in dataset."""
    dtypes_counts = df.dtypes.astype(str).value_counts()
    fig = go.Figure(
        data=[
            go.Pie(
                labels=dtypes_counts.index.tolist(),
                values=dtypes_counts.values.tolist(),
                hole=0.6,
                marker={"colors": ["#6366f1", "#3b82f6", "#06b6d4", "#10b981", "#8b5cf6", "#ec4899"]},
                textinfo="percent+label",
            )
        ]
    )
    return _apply_saas_layout(fig, "توزيع أنواع البيانات (Data Types)", height=280)


def plot_numeric_distribution(df: pd.DataFrame, column: str) -> go.Figure:
    """Histogram and KDE box distribution for a specific numeric column."""
    clean_s = pd.to_numeric(df[column], errors="coerce").dropna()
    fig = px.histogram(
        clean_s,
        x=clean_s.values,
        marginal="box",
        nbins=30,
        color_discrete_sequence=[PRIMARY_COLOR],
        labels={"x": column},
    )
    fig.update_xaxes(gridcolor=THEME_GRID, title=column)
    fig.update_yaxes(gridcolor=THEME_GRID, title="التكرار")
    return _apply_saas_layout(fig, f"توزيع القيم الرقمية: {column}", height=320)


def plot_top_categorical_values(df: pd.DataFrame, column: str, top_n: int = 8) -> go.Figure:
    """Horizontal bar chart showing top frequent categories in a text column."""
    counts = df[column].dropna().astype(str).value_counts().head(top_n).sort_values(ascending=True)
    fig = go.Figure(
        go.Bar(
            x=counts.values,
            y=counts.index.tolist(),
            orientation="h",
            marker={"color": "#3b82f6"},
            text=counts.values,
            textposition="auto",
        )
    )
    fig.update_xaxes(title="التكرار", gridcolor=THEME_GRID)
    fig.update_yaxes(gridcolor=THEME_GRID)
    return _apply_saas_layout(fig, f"أكثر القيم تكراراً في: {column}", height=320)


def plot_quality_comparison(score_before: float, score_after: float) -> go.Figure:
    """Bar chart comparing quality score before and after cleaning."""
    fig = go.Figure(
        data=[
            go.Bar(
                name="قبل التنظيف",
                x=["مؤشر الجودة الكلي"],
                y=[score_before],
                marker_color="#64748b",
                text=[f"{score_before:.1f}"],
                textposition="auto",
            ),
            go.Bar(
                name="بعد التنظيف",
                x=["مؤشر الجودة الكلي"],
                y=[score_after],
                marker_color=SUCCESS_COLOR,
                text=[f"{score_after:.1f}"],
                textposition="auto",
            ),
        ]
    )
    fig.update_yaxes(range=[0, 105], gridcolor=THEME_GRID, title="درجة الجودة (0 - 100)")
    fig.update_layout(barmode="group")
    return _apply_saas_layout(fig, "مقارنة جودة البيانات (قبل وبعد التنظيف)", height=280)


def plot_score_gauge(score: float, title: str = "مؤشر جودة البيانات") -> go.Figure:
    """Speedometer / Gauge chart for Data Quality Score (0 to 100)."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": title, "font": {"size": 16, "family": "Cairo, sans-serif", "color": "#f8fafc"}},
            number={"font": {"size": 38, "family": "Cairo, sans-serif", "color": "#f8fafc"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#94a3b8"},
                "bar": {"color": "#6366f1", "thickness": 0.25},
                "bgcolor": "#1e293b",
                "borderwidth": 1,
                "bordercolor": "#334155",
                "steps": [
                    {"range": [0, 50], "color": "rgba(239, 68, 68, 0.2)"},
                    {"range": [50, 75], "color": "rgba(245, 158, 11, 0.2)"},
                    {"range": [75, 100], "color": "rgba(16, 185, 129, 0.2)"},
                ],
                "threshold": {
                    "line": {"color": SUCCESS_COLOR, "width": 4},
                    "thickness": 0.75,
                    "value": score,
                },
            },
        )
    )
    return _apply_saas_layout(fig, height=220)

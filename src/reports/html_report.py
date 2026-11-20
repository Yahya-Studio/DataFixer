"""HTML Audit Report Generator for DataFixer."""

from typing import Any


def generate_html_report(data: dict[str, Any]) -> str:
    """Generate self-contained HTML report with responsive SaaS styling."""

    data.get("initial_score", 0.0)
    score_final = data.get("final_score", 0.0)
    score_diff = data.get("score_improvement", 0.0)

    score_color = "#10b981" if score_final >= 85 else ("#f59e0b" if score_final >= 65 else "#ef4444")

    issues_rows = ""
    for issue in data.get("detected_issues", []):
        sev_color = "#ef4444" if issue.severity == "high" else ("#f59e0b" if issue.severity == "medium" else "#3b82f6")
        issues_rows += f"""
        <tr>
            <td><strong>{issue.title}</strong></td>
            <td><span class="badge" style="background:{sev_color}20; color:{sev_color};">{issue.severity.upper()}</span></td>
            <td>{issue.affected_column or "كل البيانات"}</td>
            <td>{issue.affected_count:,} ({issue.affected_ratio * 100:.1f}%)</td>
            <td>{issue.description}</td>
        </tr>
        """

    actions_rows = ""
    for act in data.get("actions_log", []):
        time_str = act.timestamp.strftime("%H:%M:%S") if hasattr(act.timestamp, "strftime") else str(act.timestamp)
        actions_rows += f"""
        <tr>
            <td>{time_str}</td>
            <td><strong>{act.name}</strong></td>
            <td>{", ".join(act.target_columns) if act.target_columns else "الجدول بالكامل"}</td>
            <td>{act.rows_before:,} &rarr; {act.rows_after:,}</td>
            <td>{act.cells_modified:,}</td>
            <td>+{act.score_after - act.score_before:.1f} ({act.score_after:.1f})</td>
        </tr>
        """

    if not actions_rows:
        actions_rows = (
            "<tr><td colspan='6' style='text-align:center; color:#94a3b8;'>لم يتم تنفيذ أي عمليات تنظيف بعد.</td></tr>"
        )

    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير تنظيف وجودة البيانات | DataFixer Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Cairo:wght@400;600;700;800&display=swap');
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Cairo', 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1050px;
            margin: 0 auto;
            background: #1e293b;
            border-radius: 20px;
            border: 1px solid #334155;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
            padding: 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #4f46e5;
        }}
        .logo-title {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .logo-icon {{
            background: #6366f1;
            color: white;
            font-weight: 800;
            font-size: 24px;
            width: 52px;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 14px;
            box-shadow: 0 8px 16px rgba(99, 102, 241, 0.4);
        }}
        .title h1 {{
            font-size: 26px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 4px;
        }}
        .title p {{
            color: #c7d2fe;
            font-size: 14px;
        }}
        .score-pill {{
            text-align: center;
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 16px 28px;
            border-radius: 16px;
        }}
        .score-pill .label {{
            font-size: 13px;
            color: #cbd5e1;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .score-pill .score-num {{
            font-size: 42px;
            font-weight: 800;
            color: {score_color};
            line-height: 1.1;
        }}
        .content {{
            padding: 40px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: #0f172a;
            border: 1px solid #334155;
            padding: 20px;
            border-radius: 14px;
        }}
        .metric-card .label {{
            font-size: 13px;
            color: #94a3b8;
            margin-bottom: 6px;
        }}
        .metric-card .val {{
            font-size: 24px;
            font-weight: 700;
            color: #f1f5f9;
        }}
        .metric-card .sub {{
            font-size: 12px;
            color: #10b981;
            margin-top: 4px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: #e2e8f0;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid #334155;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 35px;
            background: #0f172a;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #334155;
        }}
        th, td {{
            padding: 14px 18px;
            text-align: right;
            border-bottom: 1px solid #1e293b;
            font-size: 14px;
        }}
        th {{
            background: #1e293b;
            color: #94a3b8;
            font-weight: 600;
        }}
        tr:hover td {{
            background: #1e293b80;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
        }}
        .footer {{
            padding: 24px 40px;
            background: #0f172a;
            border-top: 1px solid #334155;
            display: flex;
            justify-content: space-between;
            color: #64748b;
            font-size: 13px;
        }}
        @media print {{
            body {{
                background: white;
                color: #0f172a;
                padding: 0;
            }}
            .container {{
                border: none;
                box-shadow: none;
                background: white;
            }}
            .header {{
                background: #4338ca !important;
                -webkit-print-color-adjust: exact;
            }}
            th {{
                background: #f1f5f9;
                color: #334155;
            }}
            td {{
                color: #0f172a;
                border-bottom: 1px solid #e2e8f0;
            }}
            .metric-card {{
                background: #f8fafc;
                border: 1px solid #cbd5e1;
            }}
            .metric-card .val {{
                color: #0f172a;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo-title">
                <div class="logo-icon">&#10003;</div>
                <div class="title">
                    <h1>DataFixer &bull; تقرير جودة وتنظيف البيانات</h1>
                    <p>الملف المستهدف: {data.get("filename")} | التاريخ: {data.get("generated_at")}</p>
                </div>
            </div>
            <div class="score-pill">
                <div class="label">درجة الجودة النهائية</div>
                <div class="score-num">{score_final:.1f}</div>
                <div class="label" style="color:#10b981;">{"+" if score_diff >= 0 else ""}{score_diff:.1f} نقطة</div>
            </div>
        </div>

        <div class="content">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="label">عدد الصفوف قبل / بعد</div>
                    <div class="val">{data.get("rows_before")} &rarr; {data.get("rows_after")}</div>
                    <div class="sub">تغير: {data.get("rows_diff")} صف</div>
                </div>
                <div class="metric-card">
                    <div class="label">عدد الأعمدة</div>
                    <div class="val">{data.get("cols_before")} &rarr; {data.get("cols_after")}</div>
                    <div class="sub">تغير: {data.get("cols_diff")} عمود</div>
                </div>
                <div class="metric-card">
                    <div class="label">الخلايا المعدلة</div>
                    <div class="val">{data.get("cells_modified")}</div>
                    <div class="sub">خلية تم تصحيحها</div>
                </div>
                <div class="metric-card">
                    <div class="label">العمليات المنفذة</div>
                    <div class="val">{len(data.get("actions_log", []))}</div>
                    <div class="sub">إجراءات تنظيف مسجلة</div>
                </div>
            </div>

            <div class="section-title">
                <span>&bull;</span> المشكلات المكتشفة في الملف الأصلي ({len(data.get("detected_issues", []))})
            </div>
            <table>
                <thead>
                    <tr>
                        <th>نوع المشكلة</th>
                        <th>الخطورة</th>
                        <th>العمود المتأثر</th>
                        <th>العدد والنسبة</th>
                        <th>تفاصيل المشكلة</th>
                    </tr>
                </thead>
                <tbody>
                    {issues_rows}
                </tbody>
            </table>

            <div class="section-title">
                <span>&bull;</span> سجل إجراءات التنظيف المنفذة (Audit Log)
            </div>
            <table>
                <thead>
                    <tr>
                        <th>الوقت</th>
                        <th>العملية</th>
                        <th>الأعمدة المستهدفة</th>
                        <th>تأثير الصفوف</th>
                        <th>الخلايا المعدلة</th>
                        <th>التحسن في الجودة</th>
                    </tr>
                </thead>
                <tbody>
                    {actions_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <span>تم الإنشاء تلقائياً بواسطة منصة DataFixer</span>
            <span>معرف التقرير: {data.get("report_id")}</span>
        </div>
    </div>
</body>
</html>
"""
    return html

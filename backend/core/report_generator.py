"""
HTML Report Generator
Creates beautiful, shareable reports with recommendations
"""

from datetime import datetime
from typing import Dict, List
import os


class ReportGenerator:
    """Generate HTML reports"""

    def generate_html_report(self, target_profile: Dict, recommendations: List[Dict]) -> str:
        """
        Generate HTML report

        Args:
            target_profile: Target playlist profile
            recommendations: List of track recommendations

        Returns:
            Path to generated HTML file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.html"
        filepath = os.path.join("reports", filename)

        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)

        html_content = self.build_html(target_profile, recommendations)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filepath

    def build_html(self, target_profile: Dict, recommendations: List[Dict]) -> str:
        """Build HTML content"""

        # Build target profile table
        profile_rows = ""
        feature_names = {
            'bpm': 'BPM (Tempo)',
            'energy': 'Energy',
            'loudness': 'Loudness (LUFS)',
            'spectral_centroid': 'Brightness (Hz)',
            'rms': 'RMS Energy',
            'zero_crossing_rate': 'Zero Crossing Rate'
        }

        for key, stats in target_profile.items():
            name = feature_names.get(key, key)
            profile_rows += f"""
                <tr>
                    <td>{name}</td>
                    <td>{stats['mean']:.2f}</td>
                    <td>{stats['min']:.2f} - {stats['max']:.2f}</td>
                    <td>{stats['std']:.2f}</td>
                </tr>
            """

        # Build recommendations sections
        recommendations_html = ""
        for track_rec in recommendations:
            filename = track_rec['filename']
            recs = track_rec['recommendations']

            # Get score
            score = recs[0]['score'] if recs else 0
            score_color = self.get_score_color(score)

            # Build recommendation items
            rec_items = ""
            for rec in recs:
                status_icon = self.get_status_icon(rec['status'])
                status_color = self.get_status_color_hex(rec['status'])

                rec_items += f"""
                    <div class="recommendation-item" style="border-left-color: {status_color};">
                        <span class="status-icon">{status_icon}</span>
                        <span class="rec-message">{rec['message']}</span>
                    </div>
                """

            recommendations_html += f"""
                <div class="track-section">
                    <h3>🎵 {filename}</h3>
                    <div class="score-badge" style="background-color: {score_color};">
                        Match Score: {score}%
                    </div>
                    <div class="recommendations">
                        {rec_items}
                    </div>
                </div>
            """

        # Complete HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audio Analysis Report - {datetime.now().strftime("%Y-%m-%d %H:%M")}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 100%);
            color: #e0e6ff;
            padding: 40px 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: #0f1419;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }}

        header {{
            text-align: center;
            margin-bottom: 50px;
            padding-bottom: 30px;
            border-bottom: 2px solid #1e293b;
        }}

        h1 {{
            font-size: 2.5em;
            color: #a5b4fc;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}

        .subtitle {{
            color: #818cf8;
            font-size: 1.1em;
            font-style: italic;
        }}

        .timestamp {{
            color: #64748b;
            margin-top: 10px;
            font-size: 0.9em;
        }}

        h2 {{
            color: #818cf8;
            font-size: 1.8em;
            margin: 40px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #4f46e5;
        }}

        h3 {{
            color: #a5b4fc;
            font-size: 1.3em;
            margin-bottom: 15px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: #131822;
            border-radius: 8px;
            overflow: hidden;
        }}

        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #1e293b;
        }}

        th {{
            background-color: #1a2332;
            color: #a5b4fc;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 1px;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover {{
            background-color: #1a2332;
        }}

        .track-section {{
            background-color: #131822;
            border-radius: 12px;
            padding: 25px;
            margin: 25px 0;
            border: 2px solid #1e293b;
        }}

        .score-badge {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1em;
            margin: 15px 0;
            color: white;
        }}

        .recommendations {{
            margin-top: 20px;
        }}

        .recommendation-item {{
            background-color: #0f1419;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid;
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .status-icon {{
            font-size: 1.5em;
            min-width: 30px;
        }}

        .rec-message {{
            flex: 1;
            color: #e0e6ff;
        }}

        footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #1e293b;
            color: #64748b;
        }}

        @media print {{
            body {{
                background: white;
                color: black;
            }}

            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎵 Audio Analysis Report</h1>
            <p class="subtitle">Playlist DNA Decoded • Actionable Recommendations</p>
            <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </header>

        <section>
            <h2>🎯 Target Playlist Profile</h2>
            <table>
                <thead>
                    <tr>
                        <th>Feature</th>
                        <th>Average</th>
                        <th>Range</th>
                        <th>Std Dev</th>
                    </tr>
                </thead>
                <tbody>
                    {profile_rows}
                </tbody>
            </table>
        </section>

        <section>
            <h2>🤖 AI Recommendations</h2>
            {recommendations_html}
        </section>

        <footer>
            <p>Generated by Audio Playlist Analyzer</p>
            <p>Decode • Match • Dominate</p>
        </footer>
    </div>
</body>
</html>
"""
        return html

    def get_status_icon(self, status: str) -> str:
        """Get emoji icon for status"""
        icons = {
            'perfect': '✅',
            'good': '✓',
            'warning': '⚠️',
            'critical': '❌'
        }
        return icons.get(status, '•')

    def get_status_color_hex(self, status: str) -> str:
        """Get hex color for status"""
        colors = {
            'perfect': '#10b981',
            'good': '#84cc16',
            'warning': '#f59e0b',
            'critical': '#ef4444'
        }
        return colors.get(status, '#64748b')

    def get_score_color(self, score: float) -> str:
        """Get color based on score"""
        if score >= 80:
            return '#10b981'
        elif score >= 60:
            return '#84cc16'
        elif score >= 40:
            return '#f59e0b'
        else:
            return '#ef4444'

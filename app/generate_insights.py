import os
import urllib.parse

import pandas as pd
import matplotlib.pyplot as plt

from flask import current_app, render_template, abort, url_for
from openai import OpenAI

from app.models import Subject, LogSession

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_ai_insight(prompt: str) -> str:
    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data-analysis assistant."},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=1000
    )
    return resp.choices[0].message.content.strip()


def _build_insight_data(user_id: int, subject_name: str) -> dict:
    """
    Returns exactly:
      {
        'plot_url': <str|None>,
        'performance_insight': [<str>, …]
      }
    """

    # 1) fetch *all* Subject rows matching this user & name
    subs = Subject.query.filter_by(
        user_id=user_id, name=subject_name
    ).all()
    if not subs:
        abort(404)
    subject_ids = [s.id for s in subs]

    # 2) fetch all LogSession rows for any of those subject IDs
    sessions = (
        LogSession.query
        .filter(
            LogSession.user_id == user_id,
            LogSession.subject_id.in_(subject_ids)
        )
        .order_by(LogSession.created_at)
        .all()
    )
    if not sessions:
        return {'plot_url': None, 'performance_insight': []}

    # 3) Build exactly your original list-of-dicts
    user_data_all = [
        {
            "user_id":               s.user_id,
            "subject":               subject_name,
            "avg_study_duration":    s.study_duration,
            "avg_break_time":        s.break_time,
            "avg_mood":              s.mood_level,
            "common_environment":    s.study_environment,
            "avg_mental_load":       s.mental_load,
            "common_distraction":    s.distractions,
            "common_task_types":     s.description,
            "avg_focus_level":       s.focus_level,
            "avg_effectiveness":     s.effectiveness,
            "goal_progress_summary": s.goal_progress
        }
        for s in sessions
    ]

    # 4) Turn that into a DataFrame & compute productive_score
    df = pd.DataFrame(user_data_all)
    df['productive_score'] = df['avg_focus_level'] * df['avg_effectiveness']
    df['session_number']   = df.index + 1

    # 5) Render the plot to a PNG in static/images
    images_dir = os.path.join(current_app.static_folder, 'images')
    os.makedirs(images_dir, exist_ok=True)
    slug  = urllib.parse.quote_plus(subject_name)
    fname = f"{user_id}_{slug}_prod_score.png"
    out_fp = os.path.join(images_dir, fname)

    plt.figure()
    plt.plot(df['session_number'], df['productive_score'], marker='o')
    plt.xlabel('Session Number')
    plt.ylabel('Productive Score')
    plt.title('Productive Score Over Sessions')
    plt.tight_layout()
    plt.savefig(out_fp)
    plt.close()

    # 6) Compute summary insights exactly as you had them
    mean_score = df['productive_score'].mean()
    max_score  = df['productive_score'].max()
    min_score  = df['productive_score'].min()
    best_idx   = int(df['productive_score'].idxmax() + 1)
    worst_idx  = int(df['productive_score'].idxmin() + 1)

    performance_insight = [
        f"Your average productive score is {mean_score:.1f}.",
        (f"Great job on session {best_idx}! This is your standout session."
         if max_score > mean_score * 1.1
         else f"Your sessions are consistent; session {best_idx} is highest."),
        (f"Session {worst_idx} has room for improvement."
         if min_score < mean_score * 0.9
         else f"Even your lowest session ({worst_idx}) is close to average.")
    ]

    # 7) Append AI narrative
    narrative = call_ai_insight(
        f"Given input {user_data_all} filtered by {user_id}'s data and the {subject_name} that is being queried in the url. Use 'you' instead of user3 person narrative"
        "Provide insightful analysis on focus trends, peak productivity times, and areas for improvement. Don't need to be too verbose, just a few sentences." 
        "The summary should include Daily/weekly/monthly study durations, - Subject-wise efficiency, - Personalized productivity trends" 
        "This application motivates users by giving them clear visual feedback and enables sharing progress with peers or mentors."
    )
    performance_insight.append(narrative)

    return {
        'plot_url': url_for('static', filename=f'images/{fname}'),
        'performance_insight': performance_insight
    }


def generate_insights_core(user_id: int, subject_name: str):
    """
    View-renderer for /insights/<…>.
    """
    data = _build_insight_data(user_id, subject_name)
    return render_template(
        'insight.html',
        subject=subject_name,
        plot_url=data['plot_url'],
        performance_insight=data['performance_insight']
    )

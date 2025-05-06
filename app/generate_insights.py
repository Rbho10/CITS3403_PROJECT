import os
import urllib.parse

import pandas as pd
import matplotlib.pyplot as plt

from flask import current_app, render_template, abort, url_for
from openai import OpenAI

from app.models import Subject, LogSession, ApiResponse, db

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
    subject_id  = subject_ids[0]

    # 2) fetch sessions early to allow cache invalidation
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
        # no sessions means no plot or insight
        return {'plot_url': None, 'performance_insight': []}

    session_count = len(sessions)

    # 3) precompute slug, filename, and plot_url
    slug     = urllib.parse.quote_plus(subject_name)
    fname    = f"{user_id}_{slug}_prod_score.png"
    plot_url = url_for('static', filename=f'images/{fname}')

    # 4) check for cached AI response and valid session_count
    cached = ApiResponse.query.filter_by(
        user_id=user_id,
        subject_id=subject_id
    ).first()
    if cached:
        cached_data = cached.response_data or {}
        if cached_data.get('session_count') == session_count:
            return {
                'plot_url': plot_url,
                'performance_insight': cached_data.get('performance_insight', [])
            }
        # session count changed => invalidate old cache
        db.session.delete(cached)
        db.session.commit()

    # 5) Build list-of-dicts from sessions
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

    # 6) create dataframe and compute score
    df = pd.DataFrame(user_data_all)
    df['productive_score'] = df['avg_focus_level'] * df['avg_effectiveness']
    df['session_number']   = df.index + 1

    # 7) plot to PNG
    images_dir = os.path.join(current_app.static_folder, 'images')
    os.makedirs(images_dir, exist_ok=True)
    out_fp = os.path.join(images_dir, fname)

    plt.figure()
    plt.plot(df['session_number'], df['productive_score'], marker='o')
    plt.xlabel('Session Number')
    plt.ylabel('Productive Score')
    plt.title('Productive Score Over Sessions')
    plt.tight_layout()
    plt.savefig(out_fp)
    plt.close()

    # 8) compute summary insights
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

    # 9) append AI narrative
    narrative = call_ai_insight(
        f"Given input {user_data_all} for {subject_name}, use 'you' narrative. "
        "Provide insightful analysis on focus trends, peak productivity times, and areas for improvement. "
        "Just a few sentences."
    )
    performance_insight.append(narrative)

    # 10) cache new response with session_count
    new_cache = ApiResponse(
        user_id=user_id,
        subject_id=subject_id,
        response_data={
            'session_count': session_count,
            'performance_insight': performance_insight
        }
    )
    db.session.add(new_cache)
    db.session.commit()

    return {
        'plot_url': plot_url,
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

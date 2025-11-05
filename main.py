from fasthtml.common import *
from monsterui.all import *
import uuid
import time
import os

# Shared state (per-process, fine for a simple demo)
# We no longer keep a running cup_counts (avoids drift). Compute counts from student_cups + last_seen.
student_cups = {}  # {session_id: "green"/"yellow"/"red"}
sessions_seen = set()  # track unique sessions that visited the student view

# heartbeat: last-seen timestamps for sessions that currently have the student view open
last_seen = {}  # {session_id: timestamp}
ACTIVE_TIMEOUT = 60 * 3  # seconds considered "active"
STALE_TIMEOUT = 60 * 60 * 24  # 24 hours - prune sessions older than this
last_prune_time = 0  # Track when we last pruned to avoid excessive pruning

# Choose a theme color (blue, green, red, etc)
hdrs = Theme.blue.headers()

app, rt = fast_app(secret_key=os.environ.get('FASTHTMLCUPS_SECRET', 'this-is-the-way'), hdrs=hdrs)


def prune_stale_sessions():
    """
    Remove session ids from last_seen and student_cups if last_seen is older than STALE_TIMEOUT.
    Also remove from sessions_seen to bound total_seen.
    NOTE: This changes the semantics of 'total_seen' to 'currently tracked unique visitors'
    rather than all-time unique visitors.
    """
    global last_prune_time
    now = time.time()
    
    # Throttle: only prune if it's been at least 5 minutes since last prune
    if now - last_prune_time < 300:  # 5 minutes
        return
    
    last_prune_time = now
    
    # Compute stale sessions once per call
    stale_sessions = [sid for sid, ts in last_seen.items() if now - ts > STALE_TIMEOUT]
    
    for sid in stale_sessions:
        # Remove from all tracking structures
        last_seen.pop(sid, None)
        student_cups.pop(sid, None)
        sessions_seen.discard(sid)


@rt
def index(session):
    # Ensure each browser gets a stable session ID
    if "id" not in session:
        session["id"] = str(uuid.uuid4())
    # record that we've seen this session (counts total students seen)
    sessions_seen.add(session["id"])

    return Titled(
        "Student View - FastHTMLCups",
        Div(
            Div(
                Ul(
                    Li("Use the cups below to indicate how you're doing. Click a cup button to select it. The selected cup will be filled with color."),
                    Li("Green = Fully Understand"),
                    Li("Yellow = Unsure"),
                    Li("Red = Stuck and Need Help")
                ),
            ),
            Br(),
            # selection text target
            Div(id="dest", hx_get="/current_selection", hx_trigger="load"),
            # SVG panel that will be replaced by /cups_svg (updates based on session)
            Div(id="cups", hx_get="/cups_svg", hx_trigger="load, every 1s"),
            A("Teacher View", href="/teacher")
        )
    )


@rt
def current_selection(session):
    sid = session.get("id")
    if not sid:
        return "No cup selected yet"
    return student_cups.get(sid, "No cup selected yet")


@rt("/select_cup/{color}")
def select_cup(session, color: str):
    # Make sure we have a session id even if this is the first hit
    sid = session.setdefault("id", str(uuid.uuid4()))
    # record seen even if they jumped straight to select endpoint
    sessions_seen.add(sid)

    # Validate input - only accept valid colors
    valid_colors = {'green', 'yellow', 'red'}
    if color not in valid_colors:
        return Div("Invalid color selection. Please choose green, yellow, or red.")
    
    # Just record this session's current selection.
    # Don't maintain a separate running counter.
    student_cups[sid] = color

    # Return a small confirmation to be shown in #dest
    return Div("You selected a ", Strong(color.capitalize()), " cup.")


@rt("/teacher")
def teacher():
    return Titled(
        "Teacher View - FastHTMLCups",
        Div(id="chart-container", hx_get="/chart", hx_trigger="every 2s"),
    )


@rt
def chart():
    # Prune stale sessions opportunistically
    prune_stale_sessions()
    
    # total seen (visited) and active (currently have student view open)
    total_seen = len(sessions_seen)
    now = time.time()
    active_sessions = {sid for sid, ts in last_seen.items() if now - ts <= ACTIVE_TIMEOUT}
    active = len(active_sessions)
    inactive = max(0, total_seen - active)

    # compute distribution only from active sessions (ignore historical selections)
    bars = []

    # derive counts from active student_cups only
    active_counts = {"green": 0, "yellow": 0, "red": 0}
    for sid, color in student_cups.items():
        if sid in active_sessions and color in active_counts:
            active_counts[color] += 1

    # compute denominator from total counts instead of active sessions
    denom = sum(active_counts.values()) or 1

    # render a bar for each color in a stable order
    for color in ("green", "yellow", "red"):
        count = active_counts.get(color, 0)
        display_color = "goldenrod" if color == "yellow" else color
        percentage = (count / denom * 100) if denom > 0 else 0
        bars.append(
            Div(
                Div(
                    f"{color.capitalize()}: {count}",
                    style=(
                        f"width: {percentage}%; "
                        f"background-color: {display_color}; "
                        "padding: 10px; margin: 5px 0; color: white; font-weight: bold;"
                    ),
                )
            )
        )

    return Div(
        H3(f"Students seen: {total_seen} — Active responses: {active} — Inactive: {inactive}"),
        H4("Cup Distribution (of active responses):"),
        *bars,
        style="max-width: 700px; padding:8px;",
    )


@rt
def cups_svg(session):
    """
    Return an HTML snippet with three inline SVG cups.
    Each cup has its selection button directly underneath.
    The selected cup is filled with its color; others are transparent.
    """
    # Prune stale sessions opportunistically
    prune_stale_sessions()
    
    # ensure a stable session id and record heartbeat (this endpoint is polled every 1s)
    sid = session.setdefault("id", str(uuid.uuid4()))
    last_seen[sid] = time.time()
    sessions_seen.add(sid)

    selected = student_cups.get(sid)

    def fill_for(c):
        if selected == c:
            return {
                "green": "#38a169",
                "yellow": "goldenrod",
                "red": "#e53e3e",
            }.get(c, "#000")
        return "transparent"

    html = f'''
   <div style="display:flex; gap:24px; align-items:flex-end; justify-content:space-between;">
      <!-- Green column -->
      <div style="display:flex; flex-direction:column; align-items:center; width:33%;">
        <svg id="cup-green" width="100" height="100" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-label="Green cup">
          <path d="M6 2h12l-1 6a5 5 0 0 1-10 0L6 2z" fill="{fill_for('green')}" stroke="#2d3748" stroke-width="1"/>
          <rect x="5" y="10" width="14" height="8" rx="1" fill="{fill_for('green')}" stroke="#2d3748" stroke-width="1" opacity="0.95"/>
        </svg>
        <button hx-get="/select_cup/green" hx-target="#dest" class="uk-button uk-button-primary" style="margin-top:8px; padding:8px 16px; background:#38a169; color:white; border-radius:6px; border:none;">
          Green
        </button>
      </div>

      <!-- Yellow column -->
      <div style="display:flex; flex-direction:column; align-items:center; width:33%;">
        <svg id="cup-yellow" width="100" height="100" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-label="Yellow cup">
          <path d="M6 2h12l-1 6a5 5 0 0 1-10 0L6 2z" fill="{fill_for('yellow')}" stroke="#2d3748" stroke-width="1"/>
          <rect x="5" y="10" width="14" height="8" rx="1" fill="{fill_for('yellow')}" stroke="#2d3748" stroke-width="1" opacity="0.95"/>
        </svg>
        <button hx-get="/select_cup/yellow" hx-target="#dest" class="uk-button" style="margin-top:8px; padding:8px 16px; background:goldenrod; color:white; border-radius:6px; border:none;">
          Yellow
        </button>
      </div>

      <!-- Red column -->
      <div style="display:flex; flex-direction:column; align-items:center; width:33%;">
        <svg id="cup-red" width="100" height="100" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-label="Red cup">
          <path d="M6 2h12l-1 6a5 5 0 0 1-10 0L6 2z" fill="{fill_for('red')}" stroke="#2d3748" stroke-width="1"/>
          <rect x="5" y="10" width="14" height="8" rx="1" fill="{fill_for('red')}" stroke="#2d3748" stroke-width="1" opacity="0.95"/>
        </svg>
        <button hx-get="/select_cup/red" hx-target="#dest" class="uk-button uk-button-danger" style="margin-top:8px; padding:8px 16px; background:#e53e3e; color:white; border-radius:6px; border:none;">
          Red
        </button>
      </div>
    </div>
    '''
    return html


serve()
---
title: FastHTML on HuggingFace!
emoji: 🤗
colorFrom: indigo
colorTo: green
sdk: docker
pinned: false
---

## FastHTMLCups

This is a FastHTML application [hosted on HuggingFace](https://parmsam-fasthtmlcups.hf.space/) that allows students to select colored cups and view their selections in real-time. The app demonstrates session management, real-time updates, and interactive UI components using FastHTML. Teachers can see all student selections live, while students can only see their own choices. A link is provided on the student view to access the [teacher's dashboard](https://parmsam-fasthtmlcups.hf.space/teacher), in case also  want to see what the teacher sees and for the teacher to easily access the teacher view.

## About FastHTMLCups

FastHTMLCups is a lightweight visual-assessment app that uses the "colored cups" method to capture quick, classroom-wide student feedback. Students select Green/Yellow/Red in a simple student view; teachers see real-time aggregated, active responses in a teacher view. Built with FastHTML for minimal setup and low-latency polling.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if you have one
python main.py
# open / on student devices and /teacher for the instructor view
```

### Deploying the FasHTML app

See deployment examples from AnswerAI [here](https://github.com/AnswerDotAI/fh-deploy?tab=readme-ov-file) and `fasthtml-hf` documentation [here](https://github.com/AnswerDotAI/fasthtml-hf).
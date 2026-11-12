"""Presentation primitives for the judge interface; dynamic content is escaped."""
from html import escape
from pathlib import Path
import streamlit as st

VERDICTS = {'AC':'Accepted', 'WA':'Wrong Answer', 'TLE':'Time Limit Exceeded',
            'RE':'Runtime Error', 'CE':'Compilation Error'}


def styles(dark=True):
    colors = ({'bg':'#0d1117','surface':'#151b23','surface-alt':'#1d2633','ink':'#dce5f0','muted':'#8e9bad','line':'#2a3443',
               'accent':'#a1a9ff','accent-soft':'#232942','on-accent':'#11152b','success':'#71d8ac','success-soft':'#142f29',
               'warning':'#e4bc72','warning-soft':'#30291d','danger':'#f196ab','danger-soft':'#34212b'} if dark else
              {'bg':'#f8fafc','surface':'#ffffff','surface-alt':'#f0f3f8','ink':'#202b3d','muted':'#718097','line':'#e2e7ef',
               'accent':'#5146c9','accent-soft':'#eeedfc','on-accent':'#ffffff','success':'#137b59','success-soft':'#e9f7f0',
               'warning':'#94631a','warning-soft':'#fff6e5','danger':'#b84869','danger-soft':'#fff0f4'})
    variables=':root {'+';'.join('--'+k+':'+v for k,v in colors.items())+'}'
    st.markdown('<style>'+variables+Path(__file__).with_name('theme.css').read_text()+'</style>',unsafe_allow_html=True)


def html(value):
    st.markdown(value, unsafe_allow_html=True)


def heading(eyebrow, title, description=''):
    html(f'<div class="page-heading"><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1><p>{escape(description)}</p></div>')


def badge(value, tone='neutral'):
    return f'<span class="pill {escape(tone)}">{escape(str(value))}</span>'


def empty(title, description, symbol='↗'):
    html(f'<div class="empty-state"><span>{escape(symbol)}</span><h3>{escape(title)}</h3><p>{escape(description)}</p></div>')


def problem_header(problem, number, solved=False):
    difficulty = {'Iniciante':'easy','Intermediário':'medium','Avançado':'hard'}[problem['difficulty']]
    html(f'<div class="problem-heading"><div class="eyebrow">PROBLEMA {number:04d} · {escape(problem["topic"])}</div>'
         f'<h2>{escape(problem["title"])}</h2><div class="pills">{badge(problem["difficulty"],difficulty)}'
         f'{badge("Resolvido", "accepted") if solved else badge("Para praticar")}'
         f'{badge(str(problem["time_limit_sec"]) + " s")}{badge(str(problem["memory_limit_mb"]) + " MB")}'
         f'{badge("C++17")}</div></div>')


def verdict_card(result):
    verdict = result['verdict']
    tests = result['tests']
    elapsed = max((t['execution_time_ms'] for t in tests), default=0)
    passed = sum(t['verdict'] == 'AC' for t in tests)
    html(f'<div class="verdict-card {"verdict-ac" if verdict == "AC" else "verdict-fail"}">'
         f'<span class="eyebrow">RESULTADO DA SUBMISSÃO</span><h2>{escape(VERDICTS[verdict])}</h2>'
         f'<div class="verdict-code">{verdict}</div><p>{passed} testes aprovados de {len(tests)} executados · maior tempo: {elapsed:.1f} ms</p></div>')

"""Canonical bibliography and classic book catalog for competitive programming."""
from functools import lru_cache
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / 'data' / 'canonical_books.json'


@lru_cache(maxsize=1)
def load_catalog():
    if not DATA_PATH.exists():
        return {'version': 1, 'books': []}
    return json.loads(DATA_PATH.read_text(encoding='utf-8'))


def all_books():
    """Return all cataloged reference books."""
    return load_catalog().get('books', [])


def books_for_topic(topic_id, limit=5):
    """Return books that cover the requested topic with chapter details."""
    catalog = all_books()
    matching = []
    for book in catalog:
        if topic_id in book.get('topics', {}):
            matching.append({
                'id': book['id'],
                'title': book['title'],
                'authors': book['authors'],
                'edition': book['edition'],
                'publisher': book['publisher'],
                'open_access': book.get('open_access', False),
                'url': book['url'],
                'overview': book['overview'],
                'chapter_reading': book['topics'][topic_id]
            })
    # Prioritize open access books first for student convenience, then classic authority
    matching.sort(key=lambda b: (not b['open_access'], b['title']))
    return matching[:limit]


def format_reading_recommendations(topic_id, limit=4):
    """Format an informative Markdown section with reading suggestions."""
    recommendations = books_for_topic(topic_id, limit=limit)
    if not recommendations:
        return ''
    lines = [
        '### 📚 Leituras Recomendadas nos Livros Clássicos',
        'Para aprofundar a fundamentação teórica e ver demonstrações completas na literatura consagrada:\n'
    ]
    for b in recommendations:
        authors_str = ', '.join(b['authors'][:2]) + (' et al.' if len(b['authors']) > 2 else '')
        badge = ' `Acesso Aberto`' if b['open_access'] else ''
        lines.append(f"- **[{b['title']}]({b['url']})**{badge} · *{authors_str}* ({b['edition']})")
        lines.append(f"  - 📖 **Capítulo recomendado:** {b['chapter_reading']}")
    return '\n'.join(lines)

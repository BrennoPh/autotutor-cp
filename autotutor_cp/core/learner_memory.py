"""Portable, local long-term memory for each learner.

The design is inspired by ai-memory's capture -> consolidate -> recall ->
handoff flow.  Markdown pages are the source of truth; SQLite only indexes
them for bounded retrieval.  No language-model request is necessary to keep
or search this memory.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any
import unicodedata
import uuid


MEMORY_VERSION = 1
_SECRET = re.compile(r"(?i)(AIza[\w-]+|sk-[\w-]+|\b(?:api[_ -]?key|token|password)\s*[:=]\s*[^\s,;]+)")


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()
    text = re.sub(r"[^\w\s-]", "", text).strip()
    return re.sub(r"[-\s]+", "_", text)[:40] or "geral"


CANONICAL_TOPICS = {
    'prefix': 'Soma de prefixos',
    'prefix sum': 'Soma de prefixos',
    'soma de prefixos': 'Soma de prefixos',
    'somas de prefixos': 'Soma de prefixos',
    'somatorio': 'Soma de prefixos',
    'bfs': 'BFS e Grafos',
    'grafo': 'BFS e Grafos',
    'grafos': 'BFS e Grafos',
    'busca em largura': 'BFS e Grafos',
    'dp': 'Programação Dinâmica',
    'dinamica': 'Programação Dinâmica',
    'programacao dinamica': 'Programação Dinâmica',
    'simulacao': 'Simulação e Ad Hoc',
    'ad hoc': 'Simulação e Ad Hoc',
    'collatz': 'Simulação e Ad Hoc',
    'matematica': 'Simulação e Ad Hoc',
    'busca binaria': 'Busca Binária',
    'binary search': 'Busca Binária',
    'segtree': 'Segment Tree',
    'segment tree': 'Segment Tree',
    'arvore de segmentos': 'Segment Tree',
    'vetor': 'Vetores e Contagem',
    'vetores': 'Vetores e Contagem',
    'contagem': 'Vetores e Contagem',
    'frequencia': 'Vetores e Contagem',
    'arrays': 'Vetores e Contagem',
    'array': 'Vetores e Contagem',
}

QUERY_EXPANSIONS = {
    'intervalos': 'prefixos soma_de_prefixos consultas sentinela',
    'cumulativas': 'prefixos soma_de_prefixos somatorio',
    'consultas': 'prefixos consultas_de_soma',
    'distancia': 'bfs grafos menor_caminho fila',
    'distancias': 'bfs grafos menor_caminho fila',
    'vizinhos': 'dp programacao_dinamica nao_adjacentes',
    'selecao': 'dp programacao_dinamica',
    'passo': 'simulacao ad_hoc regras',
    'regras': 'simulacao ad_hoc collatz',
    'frequencias': 'vetores contagem frequencia residual reinicializado',
    'frequencia': 'vetores contagem frequencia residual reinicializado',
    'contar': 'vetores contagem frequencia',
}


def _canonical_topic(text: str) -> str:
    cleaned = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower().strip()
    for key, canonical in CANONICAL_TOPICS.items():
        if re.search(r'\b' + re.escape(key) + r'\b', cleaned) or key in cleaned:
            return canonical
    return text.strip() or "Geral"


class LearnerMemory:
    """Owner-scoped memory with an auditable Markdown source of truth."""

    def __init__(self, store):
        self.store = store
        self.root = store.path.parent / "memory"
        self.root.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self):
        with self.store.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS memory_events (
                id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, kind TEXT NOT NULL,
                title TEXT NOT NULL, body TEXT NOT NULL, source_id TEXT NOT NULL,
                created_at TEXT NOT NULL)""")
            db.execute("CREATE INDEX IF NOT EXISTS memory_events_profile ON memory_events(profile_id, created_at)")
            db.execute("""CREATE TABLE IF NOT EXISTS memory_pages (
                id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, path TEXT NOT NULL,
                title TEXT NOT NULL, body TEXT NOT NULL, updated_at TEXT NOT NULL,
                access_count INTEGER NOT NULL DEFAULT 0, last_used_at TEXT, UNIQUE(profile_id, path))""")
            db.execute("""CREATE TABLE IF NOT EXISTS memory_audit (
                id TEXT PRIMARY KEY, profile_id TEXT NOT NULL, action TEXT NOT NULL,
                target TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL)""")
            try:
                db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(profile_id UNINDEXED, page_id UNINDEXED, title, body)")
            except Exception:
                # SQLite builds without FTS5 still use the deterministic lexical fallback.
                pass

    @staticmethod
    def _clean(value: Any, limit: int = 1200) -> str:
        text = re.sub(r"\s+", " ", str(value or "")).strip()
        text = _SECRET.sub("[dado sensível removido]", text)
        return text[:limit]

    def _profile_dir(self, profile_id: str) -> Path:
        self.store.validate_id(profile_id)
        path = self.root / profile_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _audit(self, profile_id: str, action: str, target: str, detail: str = ""):
        with self.store.connect() as db:
            db.execute("INSERT INTO memory_audit VALUES (?,?,?,?,?,?)", (
                uuid.uuid4().hex,
                profile_id, action, target, self._clean(detail, 300), self.store.now()))

    def capture(self, profile_id: str, kind: str, title: str, body: str = "", source_id: str = "") -> str:
        """Capture a sanitized observation once; deduplication is content based."""
        self.store.validate_id(profile_id)
        kind = self._clean(kind, 60) or "atividade"
        title = self._clean(title, 180) or "Atividade sem título"
        body = self._clean(body)
        source_id = self._clean(source_id, 100)
        digest = hashlib.sha256((profile_id + "|" + kind + "|" + source_id + "|" + title + "|" + body).encode()).hexdigest()
        now = self.store.now()
        with self.store.connect() as db:
            db.execute("INSERT OR IGNORE INTO memory_events VALUES (?,?,?,?,?,?,?)", (digest, profile_id, kind, title, body, source_id, now))
        self._audit(profile_id, "capture", digest, kind + ": " + title)
        self.consolidate(profile_id)
        return digest

    def capture_artifact(self, profile_id: str, kind: str, title: str, payload: dict, source_id: str):
        """Keep metadata and learner intent, never reference solutions or full code."""
        if not isinstance(payload, dict):
            payload = {}
        if kind == "submission":
            record = payload.get("record") if isinstance(payload.get("record"), dict) else {}
            result = payload.get("result") if isinstance(payload.get("result"), dict) else {}
            topic = self._clean(record.get("topic") or payload.get("topic") or payload.get("concept") or "Geral", 80)
            verdict = self._clean(record.get("verdict") or result.get("verdict") or "Submetido", 40)
            time_ms = record.get("time_ms")
            time_part = f" ({time_ms} ms)" if time_ms is not None else ""
            body = f"Tópico: {topic} · Veredito: {verdict}{time_part} no problema '{self._clean(title, 80)}'. O código e a solução de referência não entram na memória recuperável."
        elif kind == "quiz":
            topic = self._clean(payload.get("concept") or payload.get("topic") or title.replace("Fixação · ", "").replace("Diagnóstico inicial", "Fundamentos"), 80)
            score = payload.get("score")
            total = payload.get("total")
            score_part = f" · Desempenho: {score}/{total} acertos" if score is not None and total is not None else ""
            body = f"Tópico: {topic}{score_part} no questionário. Respostas individuais omitidas."
        elif kind == "feedback":
            topic = self._clean(payload.get("concept") or payload.get("topic") or "Geral", 80)
            diag = self._clean(payload.get("content"), 300)
            diag_part = f" · Diagnóstico pedagógico: {diag}" if diag else ""
            body = f"Tópico: {topic}{diag_part}"
        elif kind == "problem":
            topic = self._clean(payload.get("topic") or payload.get("concept") or "Geral", 80)
            body = f"Tópico: {topic} · Problema prático disponibilizado na arena. Solução de referência protegida."
        else:
            body = " · ".join(x for x in (
                self._clean(payload.get("concept") or payload.get("topic"), 120),
                self._clean(payload.get("learning_request"), 500),
                self._clean(payload.get("source") or payload.get("origin"), 100),
            ) if x)
        self.capture(profile_id, "artefato:" + kind, title, body, source_id)

    def capture_model_call(self, profile_id: str, record: dict):
        """A bounded handoff observation, without system prompt, credentials or raw code."""
        prompt = self._clean(record.get("prompt"), 700)
        response = self._clean(record.get("response"), 700)
        if not prompt and not response:
            return
        title = f"Interação com {self._clean(record.get('provider'), 40)} · {self._clean(record.get('model'), 80)}"
        body = "Pedido: " + prompt + (" | Resposta: " + response if response else "")
        self.capture(profile_id, "chat", title, body, hashlib.sha256(body.encode()).hexdigest()[:24])

    def _events(self, profile_id: str, limit: int = 120):
        with self.store.connect() as db:
            rows = db.execute("SELECT id,kind,title,body,source_id,created_at FROM memory_events WHERE profile_id=? ORDER BY created_at DESC,rowid DESC LIMIT ?", (profile_id, limit)).fetchall()
        return [dict(id=r[0], kind=r[1], title=r[2], body=r[3], source_id=r[4], created_at=r[5]) for r in rows]

    def consolidate(self, profile_id: str):
        """Build readable, portable pages from observations; no facts are inferred."""
        events = list(reversed(self._events(profile_id, limit=120)))
        directory = self._profile_dir(profile_id)

        # 1. memoria.md: diário cronológico de eventos
        lines = ["# Memória de estudos", "", "Esta página é gerada localmente a partir de atividades registradas. Ela não certifica domínio e não infere desempenho além das evidências listadas.", ""]
        if not events:
            lines += ["Nenhuma atividade foi registrada ainda."]
        for event in events[-60:]:
            suffix = (" — " + event["body"]) if event["body"] else ""
            lines += [f"## {event['created_at']} · {event['kind']}", f"**{event['title']}**{suffix}", ""]
        self._write_page(profile_id, directory / "memoria.md", "Memória de estudos", "\n".join(lines).strip() + "\n")

        # Mapeamento temático para tópicos individuais e progresso
        topics_map = {}
        for e in events:
            topic_name = None
            m = re.search(r"Tópico:\s*([^·\n]+)", e["body"])
            if m:
                topic_name = _canonical_topic(m.group(1).strip())
            elif "artefato:material" in e["kind"]:
                parts = e["body"].split(" · ")
                if parts and parts[0]:
                    topic_name = _canonical_topic(parts[0].strip())
            if not topic_name or topic_name in {"Geral", "Fundamentos"}:
                text_combined = (e["title"] + " " + e["body"]).lower()
                topic_name = _canonical_topic(text_combined)
            if topic_name and topic_name not in {"Geral", "Fundamentos"}:
                topics_map.setdefault(topic_name, []).append(e)

        # 2. topicos/<slug>.md: páginas estruturadas por tópico consolidado
        topicos_dir = directory / "topicos"
        topicos_dir.mkdir(parents=True, exist_ok=True)
        topic_summaries = []
        for t_name, t_events in topics_map.items():
            slug = _slugify(t_name)
            t_materials = [ev for ev in t_events if "material" in ev["kind"]]
            t_subs = [ev for ev in t_events if "submission" in ev["kind"]]
            t_feedbacks = [ev for ev in t_events if "feedback" in ev["kind"]]

            t_lines = [
                f"# Tópico: {t_name}",
                "",
                "> Retenção pedagógica (AI Memory): leituras e materiais não comprovam domínio.",
                "",
                "## Dificuldades e Diagnósticos Observados",
            ]
            if t_feedbacks:
                for fb in t_feedbacks[-4:]:
                    t_lines.append(f"- {fb['body']}")
            elif any("Wrong Answer" in s['body'] or "WA" in s['body'] or "TLE" in s['body'] for s in t_subs):
                t_lines.append("- Falhas observadas em submissões anteriores (Wrong Answer ou TLE). Recomenda-se atenção a casos extremos e limites.")
            else:
                t_lines.append("- Nenhuma dificuldade crítica registrada até o momento.")

            t_lines += ["", "## Prática e Submissões"]
            if t_subs:
                for sub in t_subs[-6:]:
                    t_lines.append(f"- **{sub['title']}** ({sub['created_at']}): {sub['body']}")
            else:
                t_lines.append("- Nenhuma submissão registrada no juiz para este tópico.")

            t_lines += ["", "## Histórico de Materiais e Pedidos"]
            if t_materials:
                for mat in t_materials[-4:]:
                    t_lines.append(f"- **{mat['title']}** ({mat['created_at']}): {mat['body']}")
            else:
                t_lines.append("- Nenhum material registrado diretamente.")

            t_lines += ["", "## Recomendações e Próximos Passos", "- Resolver exercícios graduais e verificar casos de teste antes de avançar para tópicos complexos.", ""]
            self._write_page(profile_id, topicos_dir / f"{slug}.md", f"Tópico: {t_name}", "\n".join(t_lines).strip() + "\n")

            ac_count = sum(1 for s in t_subs if "Accepted" in s["body"])
            fail_count = sum(1 for s in t_subs if any(v in s["body"] for v in ("Wrong Answer", "WA", "TLE", "CE", "RE")))
            topic_summaries.append(f"- **{t_name}**: {len(t_materials)} materiais · {len(t_subs)} submissões ({ac_count} AC, {fail_count} falhas)")

        # 3. progresso.md: síntese consolidada de retenção
        prog_lines = [
            "# Progresso de Estudo e Retenção",
            "",
            "Esta visão consolidada da memória reflete o aprendizado retido e as atividades práticas verificadas.",
            "",
            "## Síntese por Tópico",
        ]
        if topic_summaries:
            prog_lines += topic_summaries
        else:
            prog_lines.append("- Nenhum tópico consolidado com atividades práticas ainda.")
        prog_lines += [
            "",
            "## Diretriz Pedagógica para RAG e Tutor",
            "- Não atribuir domínio com base apenas em materiais abertos.",
            "- Conectar novos materiais às dificuldades retidas e aos vereditos anteriores.",
            "- Manter foco em fundamentos algorítmicos e casos de borda.",
            ""
        ]
        self._write_page(profile_id, directory / "progresso.md", "Progresso de Estudo e Retenção", "\n".join(prog_lines).strip() + "\n")

        # 4. handoff.md: resumo portátil de passagem entre agentes/sessões
        handoff_lines = [
            "# Handoff de estudo", "",
            "Use apenas como contexto limitado para personalizar explicações. Leituras e geração de conteúdo não comprovam domínio.",
            "", "## Atividades recentes", "",
            *[f"- {e['created_at']}: {e['kind']} — {e['title']}" for e in events[-12:]], "",
            "## Dificuldades e lacunas observadas", "",
        ]
        feedbacks = [e for e in events if "feedback" in e["kind"]]
        if feedbacks:
            handoff_lines += [f"- {fb['body']}" for fb in feedbacks[-4:]]
        else:
            handoff_lines.append("- Nenhuma dificuldade específica registrada no momento.")
        handoff_lines += [
            "", "## Perguntas em aberto", "",
            "- Confirme com exercícios, questionários e submissões antes de concluir que um conteúdo foi aprendido.", ""
        ]
        self._write_page(profile_id, directory / "handoff.md", "Handoff de estudo", "\n".join(handoff_lines).strip() + "\n")
        self._audit(profile_id, "consolidate", "memoria.md", f"{len(events)} observações consolidadas")

    def _write_page(self, profile_id: str, file: Path, title: str, body: str):
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(body, encoding="utf-8")
        rel_path = str(file.relative_to(self._profile_dir(profile_id)))
        page_id = hashlib.sha256((profile_id + "/" + rel_path).encode()).hexdigest()
        now = self.store.now()
        with self.store.connect() as db:
            db.execute("INSERT INTO memory_pages(id,profile_id,path,title,body,updated_at,access_count,last_used_at) VALUES (?,?,?,?,?,?,0,NULL) ON CONFLICT(profile_id,path) DO UPDATE SET title=excluded.title,body=excluded.body,updated_at=excluded.updated_at", (page_id, profile_id, rel_path, title, body, now))
            try:
                db.execute("DELETE FROM memory_fts WHERE page_id=?", (page_id,))
                db.execute("INSERT INTO memory_fts(profile_id,page_id,title,body) VALUES (?,?,?,?)", (profile_id, page_id, title, body))
            except Exception:
                pass

    def recall(self, profile_id: str, query: str, limit: int = 4, max_chars: int = 1400) -> list[dict]:
        self.store.validate_id(profile_id)
        cleaned_query = self._clean(query, 500).casefold()
        extra_terms = " ".join(val for key, val in QUERY_EXPANSIONS.items() if key in cleaned_query)
        canonical = _canonical_topic(cleaned_query)
        if canonical not in {"Geral", "Fundamentos"}:
            extra_terms += " " + _slugify(canonical) + " " + canonical.casefold()
        terms = set(re.findall(r"[\wÀ-ÿ]{2,}", (cleaned_query + " " + extra_terms).casefold()))
        with self.store.connect() as db:
            rows = db.execute("SELECT id,path,title,body,updated_at,access_count FROM memory_pages WHERE profile_id=?", (profile_id,)).fetchall()
        ranked = []
        for row in rows:
            haystack = (row[1] + " " + row[2] + " " + row[3]).casefold()
            path_bonus = 20 if row[1].startswith("topicos/") else (8 if row[1] in ("handoff.md", "progresso.md") else 0)
            score = sum(term in haystack for term in terms) * 10 + min(row[5], 20) + path_bonus
            if score or not terms:
                excerpt = row[3][:max_chars]
                ranked.append(dict(id=row[0], path=row[1], title=row[2], excerpt=excerpt, updated_at=row[4], score=score))
        ranked.sort(key=lambda item: (item["score"], item["updated_at"]), reverse=True)
        result = ranked[:max(1, min(limit, 8))]
        if result:
            with self.store.connect() as db:
                db.executemany("UPDATE memory_pages SET access_count=access_count+1,last_used_at=? WHERE id=?", [(self.store.now(), item["id"]) for item in result])
            self._audit(profile_id, "recall", ",".join(item["path"] for item in result), self._clean(query, 200))
        return result

    def brief(self, profile_id: str, query: str, max_chars: int = 1400) -> dict:
        target_excerpt_len = max(250, min(800, (max_chars - 180) // 2))
        pages = self.recall(profile_id, query, limit=2, max_chars=target_excerpt_len)
        value = {"memory_policy": "Memória local, baseada em atividades registradas; não trate leitura ou geração como domínio.",
                 "recalled_pages": [{"title": page["title"], "excerpt": page["excerpt"]} for page in pages]}
        while len(value["recalled_pages"]) > 1 and len(json.dumps(value, ensure_ascii=False)) > max_chars:
            value["recalled_pages"].pop()
        if value["recalled_pages"] and len(json.dumps(value, ensure_ascii=False)) > max_chars:
            budget_for_excerpt = max(80, max_chars - 200)
            value["recalled_pages"][0]["excerpt"] = value["recalled_pages"][0]["excerpt"][:budget_for_excerpt]
        return value

    def export(self, profile_id: str) -> dict:
        self.store.validate_id(profile_id)
        self.consolidate(profile_id)
        with self.store.connect() as db:
            pages = db.execute("SELECT path,title,body,updated_at,access_count,last_used_at FROM memory_pages WHERE profile_id=? ORDER BY path", (profile_id,)).fetchall()
            audit = db.execute("SELECT action,target,detail,created_at FROM memory_audit WHERE profile_id=? ORDER BY created_at,rowid", (profile_id,)).fetchall()
        return {"schema_version": MEMORY_VERSION, "format": "autotutor-ai-memory", "profile_id": profile_id,
                "pages": [dict(path=r[0], title=r[1], content=r[2], updated_at=r[3], access_count=r[4], last_used_at=r[5]) for r in pages],
                "events": self._events(profile_id),
                "audit": [dict(action=r[0], target=r[1], detail=r[2], time=r[3]) for r in audit]}

    def markdown_bundle(self, profile_id: str) -> str:
        exported = self.export(profile_id)
        return "\n\n---\n\n".join(f"<!-- {page['path']} -->\n{page['content'].rstrip()}" for page in exported["pages"]) + "\n"

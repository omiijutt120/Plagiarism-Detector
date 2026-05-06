"""
models.py – OOP Data Models
Academic Plagiarism Detector · ACP Project

Classes: BaseModel → Document, CheckResult
"""

import json
from database import get_db


class BaseModel:
    TABLE = ''

    @classmethod
    def get_all(cls, limit: int = 100):
        db  = get_db()
        rows = db.execute(
            f'SELECT * FROM {cls.TABLE} ORDER BY rowid DESC LIMIT ?', (limit,)
        ).fetchall()
        db.close()
        return [dict(r) for r in rows]

    @classmethod
    def get_by_id(cls, record_id: int):
        db  = get_db()
        row = db.execute(
            f'SELECT * FROM {cls.TABLE} WHERE id=?', (record_id,)
        ).fetchone()
        db.close()
        return dict(row) if row else None

    @classmethod
    def delete(cls, record_id: int):
        db = get_db()
        db.execute(f'DELETE FROM {cls.TABLE} WHERE id=?', (record_id,))
        db.commit()
        db.close()


class Document(BaseModel):
    """
    Represents a document stored in the vault.
    Encapsulates: title, author, subject, content, word_count
    """
    TABLE = 'vault'

    def __init__(self, title: str, author: str, subject: str,
                 content: str, doc_id: int = None):
        self.id         = doc_id
        self.title      = title.strip()
        self.author     = author.strip()
        self.subject    = subject.strip()
        self.content    = content.strip()
        self.word_count = len(content.split())

    def save(self) -> bool:
        try:
            db = get_db()
            db.execute(
                'INSERT INTO vault (title, author, subject, content, word_count)'
                ' VALUES (?,?,?,?,?)',
                (self.title, self.author, self.subject,
                 self.content, self.word_count)
            )
            db.commit()
            db.close()
            return True
        except Exception:
            return False

    @classmethod
    def search(cls, term: str):
        db   = get_db()
        rows = db.execute(
            'SELECT * FROM vault WHERE title LIKE ? OR author LIKE ? OR subject LIKE ?'
            ' ORDER BY id DESC',
            (f'%{term}%', f'%{term}%', f'%{term}%')
        ).fetchall()
        db.close()
        return [dict(r) for r in rows]


class CheckResult(BaseModel):
    """
    Stores the summary of a plagiarism check.
    Full analysis stored in session; only summary persisted to DB.
    """
    TABLE = 'checks'

    def __init__(self, report: dict):
        self.doc1_title   = report.get('title1', 'Doc A')
        self.doc2_title   = report.get('title2', 'Doc B')
        self.doc1_snippet = report.get('snippet1', '')
        self.doc2_snippet = report.get('snippet2', '')
        self.overall_pct  = report.get('overall_pct', 0)
        self.cosine_pct   = report.get('cosine_pct', 0)
        self.jaccard_pct  = report.get('jaccard_pct', 0)
        self.ngram_pct    = report.get('ngram3_pct', 0)
        self.risk_level   = report.get('risk_label', 'LOW')
        self.matched_count= report.get('matched_count', 0)

    def save(self) -> int:
        """Returns new row id."""
        db  = get_db()
        cur = db.execute(
            '''INSERT INTO checks
               (doc1_title, doc2_title, doc1_snippet, doc2_snippet,
                overall_pct, cosine_pct, jaccard_pct, ngram_pct,
                risk_level, matched_count)
               VALUES (?,?,?,?,?,?,?,?,?,?)''',
            (self.doc1_title, self.doc2_title,
             self.doc1_snippet[:200], self.doc2_snippet[:200],
             self.overall_pct, self.cosine_pct, self.jaccard_pct,
             self.ngram_pct, self.risk_level, self.matched_count)
        )
        db.commit()
        new_id = cur.lastrowid
        db.close()
        return new_id

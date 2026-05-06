"""
app.py – Flask Application
Academic Plagiarism Detector · ACP Project

Routes:
  /              → Dashboard
  /check         → Submit 2 texts for comparison
  /vault         → Stored document library
  /history       → Past check results
  /report/<id>   → Saved check summary
"""

from flask import (Flask, render_template, request,
                   redirect, url_for, flash, session)
from database import init_db, get_db
from models import Document, CheckResult
from nlp_engine import PlagiarismAnalyzer
import json

app = Flask(__name__)
app.secret_key = 'acp_plagiarism_2024_xk9'

init_db()
analyzer = PlagiarismAnalyzer()


# ── Dashboard ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    db = get_db()
    stats = {
        'checks':    db.execute('SELECT COUNT(*) AS n FROM checks').fetchone()['n'],
        'docs':      db.execute('SELECT COUNT(*) AS n FROM vault').fetchone()['n'],
        'flagged':   db.execute(
                        "SELECT COUNT(*) AS n FROM checks WHERE risk_level IN ('HIGH','CRITICAL')"
                     ).fetchone()['n'],
        'avg_score': db.execute(
                        'SELECT ROUND(AVG(overall_pct),1) AS a FROM checks'
                     ).fetchone()['a'] or 0,
    }
    recent_checks = db.execute(
        'SELECT * FROM checks ORDER BY checked_at DESC LIMIT 6'
    ).fetchall()
    db.close()
    return render_template('index.html', stats=stats, recent=recent_checks)


# ── Check ─────────────────────────────────────────────────────────────────
@app.route('/check', methods=['GET', 'POST'])
def check():
    vault_docs = Document.get_all(limit=50)

    if request.method == 'POST':
        mode = request.form.get('mode', 'direct')

        # ── Direct: two pasted texts ──────────────────────────────
        if mode == 'direct':
            text1   = request.form.get('text1', '').strip()
            text2   = request.form.get('text2', '').strip()
            title1  = request.form.get('title1', 'Document A').strip() or 'Document A'
            title2  = request.form.get('title2', 'Document B').strip() or 'Document B'

            if len(text1) < 30 or len(text2) < 30:
                flash('⚠️ Both documents need at least 30 characters.', 'warning')
                return redirect(url_for('check'))

            report = analyzer.analyze(text1, text2, title1, title2)
            report['snippet1'] = text1[:120]
            report['snippet2'] = text2[:120]

        # ── Vault: compare pasted text against stored doc ─────────
        elif mode == 'vault':
            text1   = request.form.get('text1', '').strip()
            title1  = request.form.get('title1', 'Submitted Text').strip() or 'Submitted Text'
            vault_id = request.form.get('vault_id', '')

            if not vault_id or len(text1) < 30:
                flash('⚠️ Select a vault document and paste text (min 30 chars).', 'warning')
                return redirect(url_for('check'))

            doc = Document.get_by_id(int(vault_id))
            if not doc:
                flash('❌ Vault document not found.', 'danger')
                return redirect(url_for('check'))

            report = analyzer.analyze(text1, doc['content'],
                                      title1, doc['title'])
            report['snippet1'] = text1[:120]
            report['snippet2'] = doc['content'][:120]

        else:
            flash('Invalid mode.', 'danger')
            return redirect(url_for('check'))

        # Save summary to DB
        result = CheckResult(report)
        result.save()

        # Store full report in session for report page
        # (only serialisable data — strip highlighted lists for session)
        session['last_report'] = {
            k: v for k, v in report.items()
            if isinstance(v, (str, int, float, list, dict, bool))
        }
        return redirect(url_for('report'))

    return render_template('check.html', vault_docs=vault_docs)


# ── Report ────────────────────────────────────────────────────────────────
@app.route('/report')
def report():
    data = session.get('last_report')
    if not data:
        flash('No report found. Run a check first.', 'warning')
        return redirect(url_for('check'))
    return render_template('report.html', r=data)


# ── Vault ─────────────────────────────────────────────────────────────────
@app.route('/vault', methods=['GET', 'POST'])
def vault():
    search = request.args.get('q', '').strip()
    docs   = Document.search(search) if search else Document.get_all()

    if request.method == 'POST':
        doc = Document(
            title   = request.form.get('title', ''),
            author  = request.form.get('author', 'Unknown'),
            subject = request.form.get('subject', ''),
            content = request.form.get('content', ''),
        )
        if len(doc.content) < 30:
            flash('⚠️ Content too short (min 30 chars).', 'warning')
        elif doc.save():
            flash('✅ Document added to vault.', 'success')
        else:
            flash('❌ Failed to save document.', 'danger')
        return redirect(url_for('vault'))

    return render_template('vault.html', docs=docs, search=search)


@app.route('/vault/delete/<int:doc_id>')
def delete_vault(doc_id):
    Document.delete(doc_id)
    flash('🗑️ Document removed from vault.', 'warning')
    return redirect(url_for('vault'))


# ── History ───────────────────────────────────────────────────────────────
@app.route('/history')
def history():
    checks = CheckResult.get_all(limit=50)
    return render_template('history.html', checks=checks)


@app.route('/history/delete/<int:check_id>')
def delete_check(check_id):
    CheckResult.delete(check_id)
    flash('🗑️ Check record deleted.', 'warning')
    return redirect(url_for('history'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)

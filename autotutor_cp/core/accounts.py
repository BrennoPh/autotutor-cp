"""Local account authentication and expiring sessions, with no passwords in profiles."""
import hashlib
import hmac
import re
import secrets
import sqlite3
import time
import uuid
from core.progress_store import ProgressStore

ITERATIONS=600_000


class AccessError(PermissionError):
    """The current account cannot access the requested resource."""


class Accounts:
    def __init__(self, store):
        self.store=store
        with store.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE, name TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN (\'student\',\'teacher\')), profile_id TEXT NOT NULL UNIQUE, salt TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL, expires_at INTEGER NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS login_failures (username TEXT PRIMARY KEY, attempts INTEGER NOT NULL, blocked_until INTEGER NOT NULL)')

    def count(self):
        with self.store.connect() as db:return db.execute('SELECT COUNT(*) FROM users').fetchone()[0]

    @staticmethod
    def _password(password,salt):
        return hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),ITERATIONS).hex()

    def register(self,username,name,password,role='student',claim_legacy=False):
        username=username.strip().lower();name=name.strip()
        if not re.fullmatch(r'[a-z0-9_.-]{3,40}',username):raise ValueError('Use um usuário com 3 a 40 letras, números, ponto, hífen ou sublinhado.')
        if not 2<=len(name)<=80:raise ValueError('Informe um nome com 2 a 80 caracteres.')
        if not 8<=len(password)<=128:raise ValueError('Use uma senha com 8 a 128 caracteres.')
        if role not in ('student','teacher'):raise ValueError('Tipo de conta inválido.')
        salt=secrets.token_hex(32);password_hash=self._password(password,salt)
        user_id=uuid.uuid4().hex
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            first=db.execute('SELECT COUNT(*) FROM users').fetchone()[0]==0
            if claim_legacy and not first:raise AccessError('O progresso legado só pode ser vinculado à primeira conta deste computador.')
            legacy=db.execute('SELECT id FROM profiles ORDER BY updated_at DESC,rowid DESC LIMIT 1').fetchone() if claim_legacy else None
            profile_id=legacy[0] if legacy else uuid.uuid4().hex
            try:
                db.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?,?)',(user_id,username,name,role,profile_id,salt,password_hash,self.store.now()))
            except sqlite3.IntegrityError as exc:raise ValueError('Esse nome de usuário já está em uso.') from exc
        return user_id

    def login(self,username,password):
        username=username.strip().lower();now=int(time.time())
        with self.store.connect() as db:
            blocked=db.execute('SELECT attempts,blocked_until FROM login_failures WHERE username=?',(username,)).fetchone()
            if blocked and blocked[1]>now:raise ValueError('Muitas tentativas. Aguarde 15 minutos antes de tentar novamente.')
            row=db.execute('SELECT id,salt,password_hash FROM users WHERE username=?',(username,)).fetchone()
            salt=row[1] if row else '0'*64
            valid=hmac.compare_digest(self._password(password,salt),row[2] if row else '0'*64)
            if not row or not valid:
                count=(blocked[0] if blocked and blocked[1]==0 else 0)+1
                db.execute('INSERT INTO login_failures VALUES (?,?,?) ON CONFLICT(username) DO UPDATE SET attempts=excluded.attempts,blocked_until=excluded.blocked_until',
                           (username,count,now+900 if count>=5 else 0))
            else:
                db.execute('DELETE FROM login_failures WHERE username=?',(username,))
                token=secrets.token_urlsafe(40)
                db.execute('DELETE FROM sessions WHERE expires_at<=?',(now,))
                db.execute('INSERT INTO sessions VALUES (?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),row[0],now+24*3600))
                return token
        raise ValueError('Usuário ou senha incorretos.')

    def current(self,token):
        if not isinstance(token,str) or not token:return None
        with self.store.connect() as db:
            row=db.execute('SELECT u.id,u.username,u.name,u.role,u.profile_id FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.token_hash=? AND s.expires_at>?',
                           (hashlib.sha256(token.encode()).hexdigest(),int(time.time()))).fetchone()
        return dict(zip(('id','username','name','role','profile_id'),row)) if row else None

    def logout(self,token):
        with self.store.connect() as db:db.execute('DELETE FROM sessions WHERE token_hash=?',(hashlib.sha256(token.encode()).hexdigest(),))

    def user(self,user_id):
        with self.store.connect() as db:row=db.execute('SELECT id,username,name,role,profile_id FROM users WHERE id=?',(user_id,)).fetchone()
        if not row:raise AccessError('Conta não encontrada.')
        return dict(zip(('id','username','name','role','profile_id'),row))

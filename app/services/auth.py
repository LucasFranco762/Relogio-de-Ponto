"""Caso de uso de autenticação."""

from datetime import datetime

from sqlalchemy import select

from app.core.security import PasswordHasher
from app.database.engine import Database
from app.models import User


class AuthenticationService:
    """Autentica usuários e cria a conta inicial de operação."""

    def __init__(self, database: Database, hasher: PasswordHasher) -> None:
        self.database, self.hasher = database, hasher

    def ensure_initial_user(self) -> None:
        with self.database.session() as session:
            if session.scalar(select(User).where(User.login == "001")) is None:
                session.add(User(login="001", senha_hash=self.hasher.hash("01"), nome="Administrador"))

    def authenticate(self, login: str, password: str) -> User | None:
        with self.database.session() as session:
            user = session.scalar(select(User).where(User.login == login, User.ativo.is_(True)))
            if user and self.hasher.verify(password, user.senha_hash):
                user.ultimo_login = datetime.now()
                session.flush()
                return user
            return None

    def list_users(self) -> list[User]:
        with self.database.session() as session:
            return list(session.scalars(select(User).order_by(User.nome)))

    def create_user(self, nome: str, login: str, password: str) -> User:
        nome, login, password = nome.strip(), login.strip(), password.strip()
        if not nome or not login or not password:
            raise ValueError("Informe nome, login e senha.")
        with self.database.session() as session:
            if session.scalar(select(User).where(User.login == login)) is not None:
                raise ValueError("Este login já está cadastrado.")
            user = User(nome=nome, login=login, senha_hash=self.hasher.hash(password), ativo=True)
            session.add(user); session.flush()
            return user

    def delete_user(self, user_id: int, current_user_id: int | None = None) -> None:
        if current_user_id == user_id:
            raise ValueError("O usuário conectado não pode ser excluído durante a sessão.")
        with self.database.session() as session:
            user = session.get(User, user_id)
            if user is None:
                return
            total = len(list(session.scalars(select(User))))
            if total <= 1:
                raise ValueError("O sistema precisa manter pelo menos um usuário autorizado.")
            session.delete(user)

    def update_user(self, user_id: int, nome: str, login: str, password: str = "") -> User:
        nome, login, password = nome.strip(), login.strip(), password.strip()
        if not nome or not login:
            raise ValueError("Informe nome e login.")
        with self.database.session() as session:
            user = session.get(User, user_id)
            if user is None:
                raise ValueError("Usuário não encontrado.")
            duplicate = session.scalar(select(User).where(User.login == login, User.id != user_id))
            if duplicate is not None:
                raise ValueError("Este login já está cadastrado.")
            user.nome, user.login = nome, login
            if password:
                user.senha_hash = self.hasher.hash(password)
            session.flush()
            return user

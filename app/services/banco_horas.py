"""Movimentações explícitas do banco de horas."""

from app.models import MovimentacaoBancoHoras


class BancoHorasService:
    """Registra créditos, débitos e compensações em minutos inteiros."""

    def registrar(self, session, funcionario_id: int, tipo: str, quantidade_minutos: int, descricao: str, usuario_id: int | None = None, jornada_id: int | None = None) -> MovimentacaoBancoHoras:
        if not descricao.strip():
            raise ValueError("A descrição da movimentação é obrigatória.")
        item = MovimentacaoBancoHoras(funcionario_id=funcionario_id, tipo=tipo, quantidade_minutos=int(quantidade_minutos), descricao=descricao.strip(), usuario_id=usuario_id, jornada_id=jornada_id)
        session.add(item)
        return item

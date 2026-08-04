"""Ponto de entrada da aplicação Controle de Ponto."""

from app.bootstrap import create_application


def main() -> int:
    """Inicializa a aplicação e retorna seu código de saída."""
    application = create_application()
    return application.run()


if __name__ == "__main__":
    raise SystemExit(main())

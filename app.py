"""Project launcher hint."""

from __future__ import annotations


def main() -> int:
    print("La interfaz principal ahora es la web en http://127.0.0.1:8000/app")
    print("Ejecuta: uvicorn api:app --reload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

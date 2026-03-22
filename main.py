from __future__ import annotations

from pathlib import Path

from gui.app import HVACApp
from services.calculation_service import CalculationService
from services.data_service import DataRepository


def main() -> None:
    data_dir = Path(__file__).resolve().parent / "data"
    repository = DataRepository(data_dir)
    calc_service = CalculationService(repository)
    app = HVACApp(repository, calc_service)
    app.run()


if __name__ == "__main__":
    main()

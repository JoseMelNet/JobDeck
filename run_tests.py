"""Single entrypoint for running the test suite."""

from __future__ import annotations

import unittest


def main() -> int:
    loader = unittest.defaultTestLoader
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

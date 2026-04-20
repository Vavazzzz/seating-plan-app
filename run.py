import sys
from pathlib import Path


def main():
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    from ui.main_window_refactored import main as _main
    _main()


if __name__ == "__main__":
    main()

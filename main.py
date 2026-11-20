"""CLI launcher for DataFixer application."""

import sys

from streamlit.web import cli as stcli


def main():
    """Launch DataFixer Streamlit app."""
    sys.argv = ["streamlit", "run", "app.py"]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()

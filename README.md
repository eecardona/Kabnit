# Kabnit

Kabnit is aimed to be a python application for running an inventory management software through a local postgres server. Meant to be open source and scalable for everyone from the hobbyist, to the housewife, to the professional on any os.

## Getting Started

### Dependencies

Kabnit prerequisites:
* **Python 3.13 or newer**.
* **Uv**

Python dependencies that will automatically install with Uv:

* **PyQt6** Licensed under GPL v3
  - https://www.riverbankcomputing.com/software/pyqt/
* **Psycopg** 
* **python-dotenv** 

#### PostgreSQL Server

If you have a postgresql server running this application you will just follow normal flow. Otherwise, reference our [wiki](https://github.com/eecardona/Kabnit/wiki/) if needed. 

We specify how to host a local postgresql server and use it [here](https://github.com/eecardona/Kabnit/wiki/How-to-install-a-PostgreSQL-server-on-your-pc).

### Installing

Install [uv](https://docs.astral.sh/uv/) if needed. Then, from the project directly, run:

```bash
uv sync
```

### How to start

* In your terminal, navigate to project directory, run:

```bash
source .venv/bin/activate
```

* This will start your virtual environment you can now run your program:

```bash
uv run python kabnit.py
```

## FAQ

* **I recieved an error related to Qt6**
You may need to install QT6 directly on your platform. On some ubuntu systems installing 
```
command to run if program contains helper info
```

## Authors

Just me for now

## Version History

NOT YET IMPLETEMENTED. SORRY!

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE] file for details.

## Acknowledgments

* My wonderful wife. She helps me in organization, being a thinking backboard, and I am sure a million different ways we don't notice in our daily life.

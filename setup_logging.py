import logging
from logging.handlers import RotatingFileHandler
import sys
import os

def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO

    # silenciar logs barulhentos
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("groq").setLevel(logging.WARNING)
    logging.getLogger("database").setLevel(logging.ERROR)

    ############ FORMATAÇÃO
    formatter = logging.Formatter(
        "\n\n"
        "──────── LOG ────────\n"
        "TIME  : %(asctime)s\n"
        "LEVEL : %(levelname)s\n"
        "LOGGER: %(name)s\n"
        "FILE  : %(filename)s | line: %(lineno)d\n"
        "FUNC  : %(funcName)s\n"
        "MSG   : %(message)s\n\n"
    )



    ########### CONSOLE LOGS
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(level)

    ########### FILE LOGS LEVEL ENVIRONMENT
    os.makedirs("logs", exist_ok=True)
    app_file = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10_000_000,
        backupCount=5,
        encoding="utf-8"
    )
    app_file.setLevel(level)
    app_file.setFormatter(formatter)

    # ============================
    # ERROR LOG (ERROR+)
    # ============================
    error_file = RotatingFileHandler(
        "logs/error.log",
        maxBytes=10_000_000,
        backupCount=10,
        encoding="utf-8"
    )
    error_file.setFormatter(formatter)
    error_file.setLevel(logging.ERROR)

    # ROOT LOGGER
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    root.addHandler(console)
    root.addHandler(app_file)
    root.addHandler(error_file)

import os
from loguru import logger
from posthog import Posthog
import highlight_io

from sweepai.config.server import POSTHOG_API_KEY, HIGHLIGHT_API_KEY

if POSTHOG_API_KEY is None:
    posthog = Posthog(
        project_api_key="none", disabled=True, host="https://app.posthog.com"
    )
    logger.warning(
        "Initialized an empty Posthog instance as POSTHOG_API_KEY is not present."
    )
else:
    posthog = Posthog(project_api_key=POSTHOG_API_KEY, host="https://app.posthog.com")

if HIGHLIGHT_API_KEY is not None:
    H = highlight_io.H(
        HIGHLIGHT_API_KEY,
        instrument_logging=False,
        service_name="Sweep Webhook",
        pid=str(os.getpid()),
    )

    logger.add(
        H.logging_handler,
        format="{message}",
        level="INFO",
        backtrace=True,
        serialize=True,
    )

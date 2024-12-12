# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import logging
import sys

import colorlog


class AppLogger:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._setup_logger()
            self._initialized = True

    def _setup_logger(self):
        self.logger = logging.getLogger("superbom")
        if not self.logger.handlers:
            # Prevent propagation to root logger
            self.logger.propagate = False

            self.logger.setLevel(logging.INFO)
            self.logger.handlers.clear()

            # color formatter
            formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )

            # Console Handler
            console = logging.StreamHandler(sys.stdout)
            console.setFormatter(formatter)
            self.logger.addHandler(console)

    def get_logger(self):
        return self.logger

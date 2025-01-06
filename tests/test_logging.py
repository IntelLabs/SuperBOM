# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import logging
import unittest
from io import StringIO

import colorlog

from superbom.utils.logger import AppLogger


class TestAppLogger(unittest.TestCase):
    def setUp(self):
        self.logger_instance = AppLogger()
        self.logger = self.logger_instance.get_logger()

    def test_singleton_instance(self):
        another_instance = AppLogger()
        self.assertIs(self.logger_instance, another_instance)

    def test_logger_initialization(self):
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertEqual(self.logger.name, "superbom")
        self.assertFalse(self.logger.propagate)
        self.assertEqual(self.logger.level, logging.INFO)

    def test_logger_handlers(self):
        handlers = self.logger.handlers
        self.assertEqual(len(handlers), 1)
        self.assertIsInstance(handlers[0], logging.StreamHandler)
        self.assertIsInstance(handlers[0].formatter, colorlog.ColoredFormatter)

    def test_logging_output(self):
        log_output = StringIO()
        handler = logging.StreamHandler(log_output)
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
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info("Test info message")
        self.logger.removeHandler(handler)

        log_contents = log_output.getvalue()
        self.assertIn("\x1b[32mINFO    \x1b[0m Test info message\x1b[0m", log_contents)


if __name__ == "__main__":
    unittest.main()

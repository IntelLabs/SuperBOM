# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache 2.0

import logging

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
df = pd.DataFrame({"Name": ["Alice", "Bob"], "Age": [30, 25]})

logging.info("Just the DataFrame object:")
logging.info(df)

logging.info("DataFrame as string:\n%s", df.to_string())

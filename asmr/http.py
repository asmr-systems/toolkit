""" HTTP utilities. """

import os
import logging
import pathlib

import requests

import asmr.logging

log = asmr.logging.get_logger('http')


def download_file(url: str, dst_dir: pathlib.Path) -> pathlib.Path:
    filepath = dst_dir / url.split('/')[-1]

    os.makedirs(dst_dir, exist_ok=True)

    with requests.get(url, stream=True) as rsp:
        rsp.raise_for_status()
        with filepath.open(mode='wb') as f:
            chunk_size = 8192 # bytes
            for chunk in rsp.iter_content(chunk_size=chunk_size):
                # TODO log progress
                f.write(chunk)

    return filepath

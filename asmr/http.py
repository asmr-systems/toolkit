""" HTTP utilities. """

import os
import logging
import pathlib
import sys

import requests

import asmr.fs
import asmr.logging

log = asmr.logging.get_logger()


def download_file(url: str, dst_dir: pathlib.Path, show_progress=True) -> pathlib.Path:
    filepath = dst_dir / url.split('/')[-1]

    os.makedirs(dst_dir, exist_ok=True)

    with requests.get(url, stream=True) as rsp:
        rsp.raise_for_status()
        with filepath.open(mode='wb') as f:
            total_bytes      = int(rsp.headers["Content-length"])
            total            = f"% {asmr.fs.sizeof_fmt(total_bytes)}"
            downloaded_bytes = 0
            chunk_size_bytes = 8192
            with log.progress(f"downloading {filepath.name}", end_suffix=total) as progress:
                for chunk in rsp.iter_content(chunk_size=chunk_size_bytes):
                    f.write(chunk)

                    downloaded_bytes+=chunk_size_bytes
                    percent  = downloaded_bytes/total_bytes
                    readable = asmr.fs.sizeof_fmt(downloaded_bytes)
                    suffix   = f"{(percent*100):.2f}% ({readable})"
                    progress(percent, suffix=suffix)

    return filepath

from __future__ import annotations

from typing import Union
import re
from contextlib import suppress
from datetime import date, datetime
from decimal import Decimal

import pdfplumber
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

from .pdf_utils import get_page_crop, get_table_settings, starts_with_date

app = FastAPI()


class ParsedRow(BaseModel):
    transaction_date: date
    card: Union[int, None]
    issuer: str
    amount: Decimal
    currency: str


@app.get("/ping")
async def pong() -> dict:
    return {"ping": "pong!"}


@app.post("/process-pdf")
def process_pdf(file: UploadFile) -> list[ParsedRow]:
    # figure out currency of the pdf
    with pdfplumber.open(file.file) as pdf:
        page = pdf.pages[0]
        text = page.extract_text_lines()

    currency = next(
        (
            i["text"].removeprefix("Valuta: ")
            for i in text
            if i["text"].startswith("Valuta: ")
        ),
        "RSD",
    )

    tmp_rows = []

    # extract table and concatenate rows -
    # only process non-empty rows and combine multi-line issuers
    with pdfplumber.open(file.file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # pre-check - page contains table header
            text = page.extract_text()
            if not all((
                text.find("Isplata") != -1,
                text.find("Uplata") != -1,
                text.find("Stanje") != -1
            )):
                continue

            # crop page and extract table
            page = page.crop(get_page_crop(page_num, page.width, page.height, currency))
            table = page.extract_table(table_settings=get_table_settings(currency))

            if not table:
                continue

            previous = False
            for row in table:
                # ignore empty row
                if all(cell == "" for cell in row):
                    continue
                # add proper row (starts with date)
                if row[0] and re.match(starts_with_date, row[0]):
                    tmp_rows.append(row)
                    previous = True
                    continue
                # add to the issuer if it is multi-line
                elif row[3] and previous:
                    tmp_rows[-1][3] += " " + row[3]
                    continue
                previous = False

    result = []

    for row in tmp_rows:
        with suppress(Exception):
            # parse rows
            result.append(
                ParsedRow(
                    transaction_date=datetime.strptime(row[0], "%d.%m.%Y").date(),
                    card=int(row[2]) if row[2] else None,
                    issuer=row[3],
                    amount=Decimal(
                        (Decimal(row[6].replace(",", "")) or Decimal(0))
                        - (Decimal(row[5].replace(",", "")) or Decimal(0))
                    ),
                    currency=currency,
                )
            )

    return result

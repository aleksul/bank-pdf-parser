from __future__ import annotations

import re


def get_page_crop(
    page_num: int, page_width: int, page_height: int, currency: str = "RSD"
) -> tuple[int, int, int, int]:
    if currency == "RSD":
        if page_num == 0:
            return (0, 335, page_width, page_height - 90)
        return (0, 50, page_width, page_height - 90)
    else:
        if page_num == 0:
            return (0, 365, page_width, page_height - 90)
        return (0, 50, page_width, page_height - 90)


def _get_table_columns(currency: str = "RSD") -> list[int]:
    if currency == "RSD":
        return [20, 85, 145, 200, 320, 428, 482, 532, 582]
    return [20, 65, 125, 180, 310, 440, 492, 542, 592]


def get_table_settings(currency: str = "RSD") -> dict:
    return {
        "vertical_strategy": "explicit",
        "horizontal_strategy": "text",
        "intersection_x_tolerance": 50,
        "explicit_vertical_lines": _get_table_columns(currency),
    }


starts_with_date = re.compile(r"^[0-9]{2}\.[0-9]{2}\.20[0-9]{2}")

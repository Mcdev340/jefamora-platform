"""Exports CSV réservés à l'administration."""

import csv
import io

from apps.analytics.selectors import platform_stats


def stats_as_csv():
    stats = platform_stats()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["indicateur", "valeur"])
    for key, value in stats.items():
        if isinstance(value, list):
            continue
        writer.writerow([key, value])
    return buffer.getvalue()

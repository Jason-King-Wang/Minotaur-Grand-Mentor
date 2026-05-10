from __future__ import annotations


class CatalystAdapter:
    def __init__(self, manual_catalysts=None):
        self.manual_catalysts = manual_catalysts or {}

    def load(self):
        return self.manual_catalysts

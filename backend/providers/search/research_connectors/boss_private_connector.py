from __future__ import annotations


class BossPrivateResearchConnector:
    """
    Placeholder for a private research connector.

    This connector is intentionally disabled in the open-source default flow.
    If it is ever implemented for local private research, it must remain:

    - explicitly opt-in
    - isolated from the public product path
    - non-essential for the core diagnosis engine
    - transparent about source provenance and legal risk
    """

    enabled_by_default = False

    def fetch(self) -> list[dict]:
        raise NotImplementedError(
            "Private research connectors are not enabled in the open-source default product."
        )

from analysis.skill_normalizer import normalize_skill

FINANCE_INFERENCE_MAP = {
    # Reporting
    "balance sheet": "financial reporting",
    "profit and loss": "financial reporting",
    "p&l": "financial reporting",
    "financial statements": "financial reporting",

    # Tax
    "gst": "tax compliance",
    "vat": "tax compliance",
    "income tax": "tax compliance",
    "tds": "tax compliance",

    # Accounting tools
    "tally": "accounting tools",
    "quickbooks": "accounting tools",
    "sap fico": "erp accounting",
    "excel": "financial analysis",
    "spreadsheets": "financial analysis",

    # Compliance & audit
    "audit": "compliance",
    "internal audit": "compliance",
    "statutory audit": "compliance",

    # Analysis
    "cash flow": "financial analysis",
    "budgeting": "financial planning",
    "forecasting": "financial planning",
}

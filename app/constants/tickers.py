"""
Lista de tickers reales para autocompletado en portafolios.

Responsabilidad:
- Mantener centralizados los tickers válidos.
- Facilitar mantenimiento y actualización sin tocar el formulario.
"""

# Acciones colombianas
TICKERS_COLOMBIA = [
    "ECOPETROL", "ISA", "GEB", "CIB", "PFBCOLOM",
    "AVIANCA", "CEMARGOS", "PFDAVVNDA", "MINEROS", "TERPEL"
]

# ETFs globales relevantes
TICKERS_ETF_GLOBAL = [
    "VOO", "CSPX", "SPY", "QQQ", "VTI",
    "EFA", "EEM", "IWM", "GLD", "TLT"
]

# Lista completa de 20 tickers reales
TICKERS_REALES = TICKERS_COLOMBIA + TICKERS_ETF_GLOBAL

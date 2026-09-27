from ingestion.parsers.alpha import AlphaBankParser
from ingestion.parsers.eurobank import EurobankParser
from ingestion.parsers.nbg import NbgParser

PARSERS = (NbgParser(), AlphaBankParser(), EurobankParser())

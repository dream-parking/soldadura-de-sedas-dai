from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models import Client, Quote


class AbstractRepository(ABC):
    """Interfaz base"""

    @abstractmethod
    def add(self, entity):
        raise NotImplementedError

    @abstractmethod
    def get(self, id: str):
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity):
        raise NotImplementedError


# Repositorio de Clientes
class SqlAlchemyClientRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, client: Client):
        self.session.add(client)

    def get(self, id: str) -> Optional[Client]:
        return self.session.query(Client).filter_by(client_id=id).first()

    def list(self) -> List[Client]:
        return self.session.query(Client).all()

    def update(self, client: Client):
        self.session.merge(client)

class FakeClientRepository(AbstractRepository):

    def __init__(self, clients: Optional[List[Client]] = None):
        self._clients = list(clients) if clients else []

    def add(self, client: Client):
        self._clients.append(client)

    def get(self, id: str) -> Optional[Client]:
        return next((c for c in self._clients if c.client_id == id), None)

    def list(self) -> List[Client]:
        return list(self._clients)

    def update(self, client: Client):
        for i, c in enumerate(self._clients):
            if c.client_id == client.client_id:
                self._clients[i] = client
                return
        self._clients.append(client)


# Repositorio de Cotizaciones
class SqlAlchemyQuoteRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, quote: Quote):
        self.session.add(quote)

    def get(self, id: str) -> Optional[Quote]:
        return self.session.query(Quote).filter_by(quote_id=id).first()

    def list(self) -> List[Quote]:
        return self.session.query(Quote).all()

    def update(self, quote: Quote):
        self.session.merge(quote)


class FakeQuoteRepository(AbstractRepository):

    def __init__(self, quotes: Optional[List[Quote]] = None):
        self._quotes = list(quotes) if quotes else []

    def add(self, quote: Quote):
        self._quotes.append(quote)

    def get(self, id: str) -> Optional[Quote]:
        return next((q for q in self._quotes if q.quote_id == id), None)

    def list(self) -> List[Quote]:
        return list(self._quotes)

    def update(self, quote: Quote):
        for i, q in enumerate(self._quotes):
            if q.quote_id == quote.quote_id:
                self._quotes[i] = quote
                return
        self._quotes.append(quote)
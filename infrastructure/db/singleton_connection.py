# infrastructure/db/singleton_connection.py
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.engine import Engine # type: ignore

class SingletonConnectionManager:
    _instance = None
    _engine: Engine = None

    def __new__(cls, user: str, password: str, host: str, port: int, db_name: str):
        if cls._instance is None:
            cls._instance = super(SingletonConnectionManager, cls).__new__(cls)
            cls._instance.user = user
            cls._instance.password = password
            cls._instance.host = host
            cls._instance.port = port
            cls._instance.db_name = db_name
        return cls._instance

    def get_engine(self) -> Engine:
        if self._engine is None:
            url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
            self._engine = create_engine(url)
        return self._engine

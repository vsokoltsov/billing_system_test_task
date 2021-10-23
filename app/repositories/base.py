from databases import Database


class BaseRepository:
    """Represents base repository class."""

    def __init__(self, db: Database):
        """Overwrites default constructor."""

        self._db = db

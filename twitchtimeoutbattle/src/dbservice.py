from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.entities.unoreverse import UnoReverse


class DBService:
    def __init__(self, db_path):
        self.engine = create_engine(db_path, echo=True)
        self.session = sessionmaker(bind=self.engine)()

    def get_uno_reverse_by_id(self, broadcaster_id: str, user_id: str) -> UnoReverse:
        return self.session.query(UnoReverse).filter_by(user_id=user_id, broadcaster_id=broadcaster_id).first()

    def get_uno_reverse_by_user_name(self, broadcaster_id: str, user_name: str) -> UnoReverse:
        return self.session.query(UnoReverse).filter_by(user_name=user_name, broadcaster_id=broadcaster_id).first()

    def add_uno_reverse(self, uno_reverse: UnoReverse):
        ur = self.session.add(uno_reverse)
        self.commit()
        return ur

    def update_uno_reverse(self, uno_reverse: UnoReverse):
        self.commit()

    def commit(self):
        self.session.commit()

from sqlalchemy.orm import Session, joinedload

class BaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def commit_and_refresh(self, object):
        self.db.commit()
        self.db.refresh(object)

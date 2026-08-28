from sqlalchemy.orm import DeclarativeBase


# every table class inherits from this, which is how SQLAlchemy tracks all of them together
class Base(DeclarativeBase):
    pass

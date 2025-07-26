from sqlalchemy import create_engine

def get_engine():
    return create_engine('postgresql://isabella:Jupiter164*@localhost:5432/pragma')
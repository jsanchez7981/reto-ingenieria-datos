from sqlalchemy import create_engine

def get_engine():
    return create_engine('postgresql://isabella:contraseña@localhost:5432/pragma')

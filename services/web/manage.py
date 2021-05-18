from flask.cli import FlaskGroup
from datetime import datetime

from project import app, db, Prices


cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    db.session.add(Prices(crypto="BTC", price=58202,
                   timestamp=datetime.now()))
    db.session.commit()


if __name__ == "__main__":
    cli()

from sqlalchemy.sql import ClauseElement
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError


def get_one_or_create(
        session, model, create_method=None,
        create_kwargs=None, **kwargs):
    try:
        return session.query(model).filter_by(**kwargs).one(), True
    except NoResultFound:
        params = dict(
            (k, v) for k, v in kwargs.iteritems()
            if not isinstance(v, ClauseElement)
        )
        params.update(create_kwargs or {})
        if create_method is not None:
            created = create_method(**params)
        else:
            created = model(**params)

        try:
            session.add(created)
            session.flush()
            return created, False
        except IntegrityError:
            session.rollback()
            return session.query(model).filter_by(**kwargs).one(), True

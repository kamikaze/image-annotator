from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, GUID
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Integer, SmallInteger
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.sql.ddl import CreateColumn

from dataset_image_annotator.db import Base


class UTCNow(expression.FunctionElement):
    type = DateTime()


@compiles(UTCNow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(CreateColumn, 'postgresql')
def use_identity(element, compiler, **kw):
    result = compiler.visit_create_column(element, **kw).replace('SERIAL', 'INT GENERATED BY DEFAULT AS IDENTITY')

    return result.replace('BIGSERIAL', 'BIGINT GENERATED BY DEFAULT AS IDENTITY')


class BaseDBModel:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=UTCNow())
    updated_at = Column(DateTime, onupdate=UTCNow())


class UserGroup(BaseDBModel, Base):
    __tablename__ = 'user_groups'

    name = Column(String, nullable=False)


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = 'users'

    group_id = Column(Integer, ForeignKey('user_groups.id'), nullable=True)


class ImageSample(BaseDBModel, Base):
    __tablename__ = 'image_samples'

    filename = Column(String, nullable=False)
    checksum = Column(String, nullable=False, unique=True)
    location = Column(String, nullable=False, unique=True)


class ImageSampleAnnotation(BaseDBModel, Base):
    __tablename__ = 'image_sample_annotations'

    user_id = Column(GUID, ForeignKey('users.id'), nullable=False)
    image_sample_id = Column(Integer, ForeignKey('image_samples.id'), nullable=False)
    type = Column(SmallInteger)
    make = Column(String(32))
    model = Column(String(32))
    body = Column(String(32))
    color = Column(String(32))
    votes = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint('user_id', 'image_sample_id', name='uq_image_sample_annotation_item'),
    )


class AnnotationVote(BaseDBModel, Base):
    __tablename__ = 'annotation_votes'

    user_id = Column(GUID, ForeignKey('users.id'), nullable=False)
    annotation_id = Column(Integer, ForeignKey('image_sample_annotations.id'), nullable=False)
    value = Column(SmallInteger, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint('user_id', 'annotation_id', name='uq_annotation_vote'),
    )

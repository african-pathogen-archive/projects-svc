import uuid
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Pathogen(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    common_name = db.Column(db.String(255), nullable=False)
    scientific_name = db.Column(db.String(255), nullable=False)
    schema = db.Column(db.String(255), nullable=True)
    schema_version = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    def as_dict(self):
        return {
            'id': str(self.id),
            'common_name': self.common_name,
            'scientific_name': self.scientific_name,
            'schema': self.schema,
            'schema_version': self.schema_version,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'deleted_at': self.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if self.deleted_at else None
        }

class Project(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False)
    pid = db.Column(db.String(255), nullable=False)
    pathogen_id = db.Column(UUID(as_uuid=True), db.ForeignKey('pathogen.id'), nullable=False)
    admin_group = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    def as_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'pid': self.pid,
            'pathogen_id': str(self.pathogen_id),
            'admin_group': self.admin_group,
            'description': self.description,
            'owner': self.owner,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'deleted_at': self.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if self.deleted_at else None
        }

class Study(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study = db.Column(db.String(255), nullable=False)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('project.id'), nullable=False)
    admin_group = db.Column(db.String(255), nullable=True)
    member_group = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    def as_dict(self):
        return {
            'id': str(self.id),
            'study': self.study,
            'project_id': str(self.project_id),
            'admin_group': self.admin_group,
            'member_group': self.member_group,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'deleted_at': self.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if self.deleted_at else None
        }   
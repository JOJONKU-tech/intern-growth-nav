from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)  # mentor, intern, hr
    department = Column(String, nullable=True)
    position = Column(String, nullable=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    start_date = Column(String, nullable=True)
    stage = Column(String, nullable=True)  # onboarding, growth, independent
    interns = relationship("User", backref="mentor", remote_side=[id], foreign_keys=[mentor_id])

class TrainingPlan(Base):
    __tablename__ = "training_plan"
    id = Column(Integer, primary_key=True)
    department = Column(String)
    stage = Column(String)
    milestone_name = Column(String)
    description = Column(Text)
    sort_order = Column(Integer)

class ProgressLog(Base):
    __tablename__ = "progress_log"
    id = Column(Integer, primary_key=True)
    intern_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("training_plan.id"))
    mentor_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")  # pending, completed, flagged
    mentor_feedback = Column(Text, nullable=True)
    created_at = Column(String)

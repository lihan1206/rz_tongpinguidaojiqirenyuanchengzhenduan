from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class MaintenanceTicket(Base):
    __tablename__ = "maintenance_tickets"

    id = Column(Integer, primary_key=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="待处理")
    assignee_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TicketLog(Base):
    __tablename__ = "ticket_logs"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("maintenance_tickets.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TicketAttachment(Base):
    __tablename__ = "ticket_attachments"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("maintenance_tickets.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(200), nullable=False)
    url = Column(String(400), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

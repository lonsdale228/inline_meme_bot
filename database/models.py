from typing import List
from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)

class Base(DeclarativeBase):
    """Base class for all models."""
    pass



class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Many-to-many: a user can belong to many groups
    groups: Mapped[List["Group"]] = relationship(
        secondary="user_group",
        back_populates="users"
    )

    # One-to-many: a user can be admin of many groups
    admin_of_groups: Mapped[List["Group"]] = relationship(
        back_populates="admin"
    )

    # One-to-one relationship to BotAdmin (optional / only if the user is a BotAdmin)
    bot_admin: Mapped["BotAdmin"] = relationship(
        back_populates="user",
        uselist=False
    )

    # One-to-many: a user can create many memes
    memes_created: Mapped[List["Meme"]] = relationship(
        "Meme",
        back_populates="creator",
        foreign_keys="[Meme.user_tg_id]"
    )

    def __repr__(self):
        return f"<User(id={self.id}, tg_id={self.tg_id})>"


class BotAdmin(Base):
    """
    Table for bot administrators. References User by tg_id.
    """
    __tablename__ = "bot_admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # ForeignKey points to user.tg_id, which is unique
    tg_id: Mapped[str] = mapped_column(
        String, ForeignKey("user.tg_id"), unique=True
    )

    # One-to-one relationship back to User
    user: Mapped[User] = relationship(
        "User",
        back_populates="bot_admin"
    )

    def __repr__(self):
        return f"<BotAdmin(id={self.id}, tg_id={self.tg_id})>"


class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    invite_link_id: Mapped[str] = mapped_column(String(255), nullable=True)

    # Admin column (references the User who is the admin)
    admin_id: Mapped[str] = mapped_column(ForeignKey("user.tg_id"), nullable=True)
    admin: Mapped[User] = relationship(
        "User",
        back_populates="admin_of_groups",
        # optional: if you want to load the admin user eagerly, you can add:
        # lazy="joined"
    )

    # Many-to-many: a group can have many users
    users: Mapped[List[User]] = relationship(
        secondary="user_group",
        back_populates="groups"
    )
    # Many-to-many: a group can have many memes
    memes: Mapped[List["Meme"]] = relationship(
        secondary="group_meme",
        back_populates="groups"
    )

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"


class Meme(Base):
    __tablename__ = "meme"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_id: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)

    # New column to represent the Telegram ID of the User who created the meme.
    # This references the unique tg_id field in User.
    user_tg_id: Mapped[str] = mapped_column(String, ForeignKey("user.tg_id"), nullable=False)

    # Relationship to the User who created the meme.
    creator: Mapped[User] = relationship(
        "User",
        back_populates="memes_created",
        foreign_keys="[Meme.user_tg_id]"
    )

    # Many-to-many: a meme can belong to many groups
    groups: Mapped[List[Group]] = relationship(
        secondary="group_meme",
        back_populates="memes"
    )

    def __repr__(self):
        return f"<Meme(id={self.id}, name={self.name}, url={self.url})>"


class UserGroup(Base):
    """
    Association table for many-to-many between User and Group.
    No uniqueness constraint on (user_id, group_id).
    """
    __tablename__ = "user_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.tg_id"), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), nullable=False)


class GroupMeme(Base):
    """
    Association table for many-to-many between Group and Meme.
    No uniqueness constraint on (group_id, meme_id).
    """
    __tablename__ = "group_meme"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), nullable=False)
    meme_id: Mapped[int] = mapped_column(ForeignKey("meme.id"), nullable=False)
from datetime import datetime

from sqlalchemy import UniqueConstraint, ForeignKey, Integer, DateTime, func

from sqlalchemy.orm import relationship, Mapped, mapped_column

from . import Base
from .accounts import User
from .movies import Movie


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False
    )
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship("User", back_populates="cart")

    __table_args__ = (UniqueConstraint("user_id"),)

    def __repr__(self) -> str:
        return f"<Cart(id: {self.id}, user_id: {self.user_id}, cart_items: {self.cart_items})>"


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("carts.id"), nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id"), nullable=False
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    cart: Mapped["Cart"] = relationship("Cart", back_populates="cart_items")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="cart_items")

    __table_args__ = (UniqueConstraint("cart_id", "movie_id"),)

    def __repr__(self):
        return f"<CartItem(id={self.id}, cart_id={self.cart_id}, movie_id={self.movie_id}, added_at={self.added_at})>"


class Purchased(Base):
    __tablename__ = "purchased"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id"), nullable=False
    )

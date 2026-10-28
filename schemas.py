from pydantic import BaseModel, EmailStr, Field


class ContactForm(BaseModel):
    """Модель формы обратной связи."""

    name: str = Field(
        min_length=2,
        max_length=80,
        description="Имя отправителя",
    )
    email: EmailStr = Field(
        description="Email для ответа",
    )
    text: str = Field(
        min_length=10,
        max_length=2000,
        description="Текст сообщения",
    )
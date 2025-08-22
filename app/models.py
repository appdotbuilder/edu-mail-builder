from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal


# Enums for template types and statuses
class TemplateType(str, Enum):
    COURSE_REMINDER = "course_reminder"
    COURSE_STARTS_TODAY = "course_starts_today"
    COURSE_WELCOME = "course_welcome"
    COURSE_COMPLETION = "course_completion"
    ASSIGNMENT_DUE = "assignment_due"
    GRADE_NOTIFICATION = "grade_notification"


class EmailStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentBlockType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    BUTTON = "button"
    DIVIDER = "divider"
    SPACER = "spacer"
    AI_GENERATED = "ai_generated"


# Persistent models (stored in database)
class Course(SQLModel, table=True):
    """Course entity for email context"""

    __tablename__ = "courses"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    instructor: str = Field(max_length=100)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    email_templates: List["EmailTemplate"] = Relationship(back_populates="course")


class EmailTemplate(SQLModel, table=True):
    """Main email template model"""

    __tablename__ = "email_templates"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=500)
    template_type: TemplateType = Field(default=TemplateType.COURSE_REMINDER)
    status: EmailStatus = Field(default=EmailStatus.DRAFT)

    # Email metadata
    subject_line: str = Field(max_length=200)
    preview_text: str = Field(default="", max_length=150)

    # Layout configuration
    layout_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Course association
    course_id: Optional[int] = Field(default=None, foreign_key="courses.id")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(default=None)

    # Relationships
    course: Optional[Course] = Relationship(back_populates="email_templates")
    content_blocks: List["ContentBlock"] = Relationship(back_populates="template", cascade_delete=True)
    ai_generations: List["AIGeneration"] = Relationship(back_populates="template", cascade_delete=True)


class ContentBlock(SQLModel, table=True):
    """Individual content blocks within email templates"""

    __tablename__ = "content_blocks"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="email_templates.id")

    # Block configuration
    block_type: ContentBlockType = Field(default=ContentBlockType.TEXT)
    order_index: int = Field(default=0)

    # Content data
    content: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Styling and layout
    style_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # AI generation tracking
    ai_generated: bool = Field(default=False)
    ai_generation_id: Optional[int] = Field(default=None, foreign_key="ai_generations.id")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    template: EmailTemplate = Relationship(back_populates="content_blocks")
    ai_generation: Optional["AIGeneration"] = Relationship(back_populates="content_blocks")


class AIGeneration(SQLModel, table=True):
    """Track AI-generated content for templates"""

    __tablename__ = "ai_generations"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="email_templates.id")

    # AI generation parameters
    prompt: str = Field(max_length=1000)
    model_used: str = Field(max_length=50)
    temperature: Decimal = Field(default=Decimal("0.7"))

    # Generated content
    generated_content: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Success tracking
    success: bool = Field(default=True)
    error_message: Optional[str] = Field(default=None, max_length=500)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    template: EmailTemplate = Relationship(back_populates="ai_generations")
    content_blocks: List[ContentBlock] = Relationship(back_populates="ai_generation")


class MediaAsset(SQLModel, table=True):
    """Media assets (images, files) used in email templates"""

    __tablename__ = "media_assets"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size: int = Field(default=0)  # Size in bytes
    mime_type: str = Field(max_length=100)

    # Image-specific metadata
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    alt_text: str = Field(default="", max_length=200)

    # Usage tracking
    usage_count: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LayoutPreset(SQLModel, table=True):
    """Predefined layout configurations for templates"""

    __tablename__ = "layout_presets"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=300)

    # Layout configuration
    layout_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Template type association
    template_type: Optional[TemplateType] = Field(default=None)

    # Usage tracking
    is_default: bool = Field(default=False)
    usage_count: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class CourseCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    instructor: str = Field(max_length=100)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)


class CourseUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    instructor: Optional[str] = Field(default=None, max_length=100)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)


class EmailTemplateCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=500)
    template_type: TemplateType = Field(default=TemplateType.COURSE_REMINDER)
    subject_line: str = Field(max_length=200)
    preview_text: str = Field(default="", max_length=150)
    layout_config: Dict[str, Any] = Field(default={})
    course_id: Optional[int] = Field(default=None)


class EmailTemplateUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    template_type: Optional[TemplateType] = Field(default=None)
    status: Optional[EmailStatus] = Field(default=None)
    subject_line: Optional[str] = Field(default=None, max_length=200)
    preview_text: Optional[str] = Field(default=None, max_length=150)
    layout_config: Optional[Dict[str, Any]] = Field(default=None)
    course_id: Optional[int] = Field(default=None)


class ContentBlockCreate(SQLModel, table=False):
    template_id: int
    block_type: ContentBlockType = Field(default=ContentBlockType.TEXT)
    order_index: int = Field(default=0)
    content: Dict[str, Any] = Field(default={})
    style_config: Dict[str, Any] = Field(default={})


class ContentBlockUpdate(SQLModel, table=False):
    block_type: Optional[ContentBlockType] = Field(default=None)
    order_index: Optional[int] = Field(default=None)
    content: Optional[Dict[str, Any]] = Field(default=None)
    style_config: Optional[Dict[str, Any]] = Field(default=None)


class AIGenerationRequest(SQLModel, table=False):
    template_id: int
    prompt: str = Field(max_length=1000)
    model_used: str = Field(default="gpt-3.5-turbo", max_length=50)
    temperature: Decimal = Field(default=Decimal("0.7"))
    content_type: ContentBlockType = Field(default=ContentBlockType.AI_GENERATED)


class MediaAssetCreate(SQLModel, table=False):
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size: int = Field(default=0)
    mime_type: str = Field(max_length=100)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    alt_text: str = Field(default="", max_length=200)


class LayoutPresetCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=300)
    layout_config: Dict[str, Any] = Field(default={})
    template_type: Optional[TemplateType] = Field(default=None)
    is_default: bool = Field(default=False)

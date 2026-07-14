from io import BytesIO
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from fastapi import UploadFile
from exceptions.validation_exception import (
    EmptyFileException,
    InvalidFileException,
    InvalidTagException,
)
from validators.file_validator import (validate_file_size,validate_pdf_file,)
from validators.query_validator import (validate_query,)
from validators.tag_validator import (validate_tag,)
from validators.upload_validator import (validate_upload,)
from configuration.config import (MAX_FILE_SIZE,MAX_QUERY_LENGTH,)

# ==========================================================
# Query Validator Tests
# ==========================================================

def test_validate_query_success():
    validate_query("What is Artificial Intelligence?")

def test_validate_query_empty():
    with pytest.raises(HTTPException):
        validate_query("")

def test_validate_query_too_long():
    query = "A" * (MAX_QUERY_LENGTH + 1)
    with pytest.raises(HTTPException):
        validate_query(query)

# ==========================================================
# Tag Validator Tests
# ==========================================================

def test_validate_tag_none():
    validate_tag(None)

def test_validate_tag_success():
    validate_tag("machine_learning")

def test_validate_tag_empty():
    with pytest.raises(InvalidTagException):
        validate_tag("")

def test_validate_tag_too_long():
    tag = "A" * 101
    with pytest.raises(InvalidTagException):
        validate_tag(tag)

# ==========================================================
# File Validator Tests
# ==========================================================

from io import BytesIO
class FakeUploadFile:

    def __init__(
        self,
        filename="sample.pdf",
        content=b"dummy",
        content_type="application/pdf",
    ):

        self.filename = filename
        self.content_type = content_type
        self.file = BytesIO(content)

def test_validate_pdf_success():
    file = FakeUploadFile()

    validate_pdf_file(file)

def test_validate_pdf_wrong_extension():
    file = FakeUploadFile(filename="sample.txt")
    with pytest.raises(InvalidFileException):
        validate_pdf_file(file)

def test_validate_pdf_empty():
    file = FakeUploadFile(content=b"")
    with pytest.raises(EmptyFileException):
        validate_pdf_file(file)

def test_validate_file_size():
    with pytest.raises(InvalidFileException):
        validate_file_size(MAX_FILE_SIZE + 1)

# ==========================================================
# Upload Validator Tests
# ==========================================================

def test_validate_upload_empty():
    with pytest.raises(EmptyFileException):
        validate_upload([])

@patch("validators.upload_validator.validate_pdf_file")
def test_validate_upload_success(
    mock_validate_pdf,
):

    file = FakeUploadFile()
    validate_upload([file])
    mock_validate_pdf.assert_called_once()
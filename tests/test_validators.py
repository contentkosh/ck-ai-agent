from io import BytesIO
from unittest.mock import patch
import pytest
from exceptions.validation_exception import (
    EmptyFileException,
    InvalidFileException,
    InvalidTagException,
    EmptyQueryException,
    QueryTooLongException,
)
from validators.file_validator import (
    validate_file_size,
    validate_pdf_file,
    validate_saved_file,
)
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
    with pytest.raises(EmptyQueryException):
        validate_query("")

def test_validate_query_too_long():
    query = "A" * (MAX_QUERY_LENGTH + 1)
    with pytest.raises(QueryTooLongException):
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

class FakeUploadFile:

    def __init__(
        self,
        filename="sample.pdf",
        content=b"%PDF-1.4 dummy pdf content",
        content_type="application/pdf",
    ):

        self.filename = filename
        self.content_type = content_type
        self.file = BytesIO(content)

def test_validate_pdf_success():
    file = FakeUploadFile()
    validate_pdf_file(file)

def test_validate_pdf_none():
    """
    Verify validation fails when the uploaded file is None.
    """
    with pytest.raises(EmptyFileException):
        validate_pdf_file(None)

def test_validate_pdf_no_filename():
    """
    Verify validation fails when no filename is provided.
    """
    file = FakeUploadFile()
    file.filename = None

    with pytest.raises(InvalidFileException):
        validate_pdf_file(file)

def test_validate_pdf_invalid_content_type():
    """
    Verify validation fails when the uploaded content type
    is not application/pdf.
    """
    file = FakeUploadFile(
        content_type="text/plain",
    )

    with pytest.raises(InvalidFileException):
        validate_pdf_file(file)

def test_validate_pdf_wrong_extension():
    file = FakeUploadFile(filename="sample.txt")
    with pytest.raises(InvalidFileException):
        validate_pdf_file(file)

def test_validate_pdf_empty():
    file = FakeUploadFile(content=b"")
    with pytest.raises(EmptyFileException):
        validate_pdf_file(file)

def test_validate_pdf_invalid_signature():
    file = FakeUploadFile(content=b"not a real pdf")
    with pytest.raises(InvalidFileException):
        validate_pdf_file(file)

def test_validate_file_size():
    with pytest.raises(InvalidFileException):
        validate_file_size(MAX_FILE_SIZE + 1)

def test_validate_saved_file_not_found():
    """
    Verify validation fails when the saved PDF
    does not exist on disk.
    """
    with pytest.raises(InvalidFileException):
        validate_saved_file("missing_document.pdf",)

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

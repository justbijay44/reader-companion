from app.ingestion.loader import is_pdf


def test_is_pdf_true(tmp_path):
    file = tmp_path / "fake.pdf"
    file.write_bytes(b"%PDF-1.4\n...")

    assert is_pdf(str(file))

def test_is_pdf_false(tmp_path):
    file = tmp_path / "fake.pdf"
    file.write_bytes(b"<svg></svg>")

    assert not is_pdf(str(file))



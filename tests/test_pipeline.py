from app.ingestion.pipeline import file_hash

def test_file_hash_consistency(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("hello world")

    hash1 = file_hash(str(file))
    hash2 = file_hash(str(file))

    assert hash1 == hash2
    assert len(hash1) == 64

def test_file_hash_differs_for_different_content(tmp_path):
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    file1.write_text("hello")
    file2.write_text("world")

    assert file_hash(str(file1)) != file_hash(str(file2))
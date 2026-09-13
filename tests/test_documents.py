import io
from tests.conftest import auth_header


def test_document_ocr_and_review_workflow(client, seed_test_context):
    admin = seed_test_context["admin"]
    mine_a = seed_test_context["mine_a"]
    headers = auth_header(admin)

    # 1. Reject invalid file type
    fake_exe = io.BytesIO(b"MZ\x90\x00executable binary")
    res_bad = client.post(
        "/api/v1/documents/ocr",
        data={"mine_id": mine_a.id, "category": "MINE_PLAN"},
        files={"file": ("malicious.exe", fake_exe, "application/octet-stream")},
        headers=headers,
    )
    assert res_bad.status_code == 400
    assert "Unsupported file type" in res_bad.json()["detail"]

    # 2. Upload valid simulated document (PNG image bytes)
    # 1x1 white PNG byte stream
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\r\xef\x8aL\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    res_ok = client.post(
        "/api/v1/documents/ocr",
        data={"mine_id": mine_a.id, "category": "DGMS_CLEARANCE"},
        files={"file": ("dgms_clearance_2026.png", io.BytesIO(png_bytes), "image/png")},
        headers=headers,
    )
    assert res_ok.status_code == 201
    doc_data = res_ok.json()
    doc_id = doc_data["id"]
    assert doc_data["file_name"] == "dgms_clearance_2026.png"
    assert doc_data["ocr_status"] == "UNVERIFIED"
    assert "ocr_extracted_text" in doc_data

    # 3. Check OCR status
    status_res = client.get(f"/api/v1/documents/{doc_id}/status", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["ocr_status"] == "UNVERIFIED"
    assert status_res.json()["is_verified"] is False

    # 4. Human-in-the-loop review and certification
    review_payload = {
        "verified_text": "DGMS Approval No. 2026/CZ/1049: Environmental and Highwall radar compliance certified.",
        "approve": True,
    }
    review_res = client.patch(f"/api/v1/documents/{doc_id}/review", json=review_payload, headers=headers)
    assert review_res.status_code == 200
    assert review_res.json()["ocr_status"] == "VERIFIED"
    assert review_res.json()["ocr_extracted_text"] == review_payload["verified_text"]
    assert review_res.json()["verified_by_id"] == admin.id

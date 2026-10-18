def test_relative_paths_resolve_from_repo_root() -> None:
    from app.core.config import REPO_ROOT, Settings

    s = Settings(model_bundle_dir="./ml/artifacts/bundles", upload_dir="backend/uploads")
    assert s.model_bundle_dir == (REPO_ROOT / "ml" / "artifacts" / "bundles").resolve()
    assert s.upload_dir == (REPO_ROOT / "backend" / "uploads").resolve()

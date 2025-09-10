from sqlalchemy import text
from loggers import missing_zip_logger



def ensure_zip_code_exists(engine, zip_code, row=None):
    zip_code = str(zip_code)
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT 1 FROM zip_code_reference WHERE geolocation_zip_code_prefix = :zip"),
            {"zip": zip_code}
        ).fetchone()
        if not result:
            conn.execute(
                text("""
                    INSERT INTO zip_code_reference (
                        geolocation_zip_code_prefix, geolocation_lat, geolocation_lng
                    ) VALUES (:zip, NULL, NULL)
                """),
                {"zip": zip_code}
            )
            missing_zip_logger.info(f"➕ Added missing zip code: {zip_code} | Customer row: {row}")



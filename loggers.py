import logging

# Logger for dropped duplicates
duplicate_logger = logging.getLogger("duplicate_key_drops")
duplicate_logger.setLevel(logging.INFO)
dupe_handler = logging.FileHandler("duplicate_key_drops.log")
dupe_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
duplicate_logger.addHandler(dupe_handler)

# Logger for missing zip codes
missing_zip_logger = logging.getLogger("missing_zip_codes")
missing_zip_logger.setLevel(logging.INFO)
zip_handler = logging.FileHandler("missing_zip_codes.log")
zip_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
missing_zip_logger.addHandler(zip_handler)

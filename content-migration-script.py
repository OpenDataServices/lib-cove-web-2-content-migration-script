import sqlite3
import os.path
import datetime
import uuid

def run(database_location, media_directory):
    database_connection = sqlite3.connect(database_location)
    database_connection.row_factory = sqlite3.Row 
    database_cursor = database_connection.cursor()

    ############################### For every old data ......
    database_cursor.execute("SELECT * FROM input_supplieddata")
    for original_data_row in database_cursor.fetchall():
        id_with_dashes = str(uuid.UUID(original_data_row['id']))
        expired = None
        format = "unknown"
        content_type = None
        if original_data_row['original_file'].lower().endswith(".json"):
            format = "json"
            content_type = "application/json"
        elif original_data_row['original_file'].lower().endswith(".xlsx"):
            format = "spreadsheet"
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        size = None
        charset = None

        ############################### Check files on disk
        if original_data_row['original_file'] and os.path.exists(os.path.join(media_directory, original_data_row['original_file'])):
            # We still have files!
            original_file_full_path = os.path.join(media_directory, original_data_row['original_file'])
            size = os.path.getsize(original_file_full_path)
            os.makedirs(
                os.path.join(
                    media_directory,
                    id_with_dashes,
                    "supplied_data",
                    id_with_dashes
                )
            )
            os.rename(
                original_file_full_path,
                os.path.join(
                    media_directory,
                    id_with_dashes,
                    "supplied_data",
                    id_with_dashes,
                    original_data_row['original_file'].split("/").pop(),
                )
            )

        else:
            # The data has expired
            # (Or, the data has a source URL but no original_file value. We assume this is an error and just expire those)
            expired = datetime.datetime.now().isoformat()

        ############################### Write new database content
        database_cursor.execute(
            """INSERT INTO libcoveweb2_supplieddata 
            (id, created, expired,   format, meta) 
            VALUES (?, ?, ?, ?, ?)""",
            [
                original_data_row['id'],
                original_data_row['created'],
                expired,
                format,
                "{}",
            ]
        )

        database_cursor.execute(
            """INSERT INTO libcoveweb2_supplieddatafile 
            (id, supplied_data_id,   filename, source_url, source_method, size, content_type, charset, meta) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                original_data_row['id'],
                original_data_row['id'],
                original_data_row['original_file'].split("/").pop(),
                original_data_row['source_url'],
                "url" if original_data_row['source_url'] else "upload",
                size,
                content_type,
                charset,
                "{}",
            ]
        )

        database_connection.commit()

        ############################### Delete old cached output files for this
        for old_file in [
            "unflattened.json",
            "conversion_warning_messages.json",
            "heading_source_map.json",
            "cell_source_map.json",
            "validation_errors-3.json",
        ]:
            old_data_file_full_path = os.path.join(
                media_directory,
                original_data_row['id'],
                old_file,
            )
            if os.path.exists(old_data_file_full_path):
                os.remove(old_data_file_full_path)


if __name__ == "__main__":
    run(
        database_location="db.sqlite3",
        media_directory="media"
    )


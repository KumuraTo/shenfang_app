1.  import salon_db_20250610_1238.sql
    mysql -u root -p
    CREATE DATABASE salon_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    exit
    mysql -u root -p salon_db < salon_db.sql

2.  modify DB account & password at:
    db_config.json

3.  run ~/dist/salon_app.exe

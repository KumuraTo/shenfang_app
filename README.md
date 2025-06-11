## Instruction

import SQL script:
```bash
mysql -u root -p
CREATE DATABASE salon_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit

mysql -u root -p salon_db < salon_db.sql
```

modify DB account & password:
```bash
{
    "host": "localhost",
    "user": "root",
    "password": "type_your_password_here",
    "db": "salon_db",
    "charset": "utf8mb4"
}
```

run ~/salon_app.exe

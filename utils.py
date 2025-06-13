import csv
import pandas as pd
import hashlib
from datetime import datetime

def export_to_csv(data, filename):
    if not data:
        print(f"[CSV] Empty data: {filename}")
        return

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"[CSV] Saved: {filename}")


def export_to_xlsx(data, filename):
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        for sheet_name, d in data.items():
            if d:
                df = pd.DataFrame(d)
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    print(f"[XLSX] Saved: {filename}")


def export_to_sql(data, table_name, filename):
    if not data:
        print(f"[SQL] Empty data: {table_name}")
        return

    with open(filename, 'w', encoding='utf-8') as f:
        # CREATE TABLE (oddiy holda)
        fields = data[0].keys()
        create_stmt = f"CREATE TABLE {table_name} (\n"
        create_stmt += ",\n".join([f"  {field} TEXT" for field in fields])
        create_stmt += "\n);\n\n"
        f.write(create_stmt)

        # INSERT INTO
        for row in data:
            columns = ', '.join(row.keys())
            values = ', '.join([f"'{str(v)}'" for v in row.values()])
            f.write(f"INSERT INTO {table_name} ({columns}) VALUES ({values});\n")
    print(f"[SQL] Saved: {filename}")


def export_all(users, assignments, grades):
    # 1. CSV
    export_to_csv(users, "data/users.csv")
    export_to_csv(assignments, "data/assignments.csv")
    export_to_csv(grades, "data/grades.csv")

    # 2. XLSX
    export_to_xlsx({
        "Users": users,
        "Assignments": assignments,
        "Grades": grades
    }, "data/platform_data.xlsx")

    # 3. SQL
    export_to_sql(users, "users", "data/users.sql")
    export_to_sql(assignments, "assignments", "data/assignments.sql")
    export_to_sql(grades, "grades", "data/grades.sql")


def validate_data(data):
    for row in data:
        if not all(row.values()):
            raise ValueError("There is an empty space.")
        

def hash_password(password) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed) -> bool:
    return hash_password(password) == hashed

def register_user(user_class, _id, full_name, email, password, **kwargs):
    password_hash = hash_password(password)
    return user_class(_id=_id, full_name=full_name, email=email,
                      password_hash=password_hash, **kwargs)

def authenticate_user(user_class, email, password):
    for user in user_class._users:
        if user._email == email and check_password(password, user._password_hash):
            return user
    return None

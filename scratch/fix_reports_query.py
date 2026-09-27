import os

target = r"C:\PROJECTS\Fullstack PBX\PBX\src\api\v1\reports.py"

with open(target, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("c.caller_id_number", "c.caller_number as caller_id_number")
c = c.replace("c.caller_id_name", "c.caller_name as caller_id_name")

with open(target, "w", encoding="utf-8") as f:
    f.write(c)

print("reports.py column names fixed.")

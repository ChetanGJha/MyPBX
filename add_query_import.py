import os

path = r'c:\PROJECTS\Fullstack PBX\PBX\src\api\v1\users.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'from fastapi import APIRouter, Depends, HTTPException, status',
    'from fastapi import APIRouter, Depends, HTTPException, status, Query'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Added Query to fastapi imports in users.py')

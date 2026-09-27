import sys, os, asyncio
sys.path.append(r'c:\PROJECTS\Fullstack PBX\PBX')
from src.core.database import execute_query

async def inspect_db():
    u_cols = await execute_query("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'")
    print('User columns:', [c['column_name'] for c in u_cols])
    users = await execute_query('SELECT * FROM users LIMIT 10')
    print('Users:')
    for u in users:
        d = dict(u)
        d.pop('hashed_password', None)
        d.pop('password_hash', None)
        print('  ', d)
    
    audio = await execute_query('SELECT * FROM audio_files')
    print('Audio files count:', len(audio))
    for a in audio:
        print('  ', dict(a))

if __name__ == '__main__':
    asyncio.run(inspect_db())

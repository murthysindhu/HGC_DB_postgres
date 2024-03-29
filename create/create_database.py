'''
SQL Tables should only have to be made once. After that any modifications to the table should be locked with a password.
Tables that we need based on the OGP measurements so far:
'''

import asyncio
import asyncpg
import sshtunnel

async def create_db():
    print("Creating a new database...")
    # Database connection parameters for new database
    db_params = {
        'database': (open('../dbase_info/dbfname.txt','r').read()).split('\n')[0].split(' ')[0],
        'user': 'postgres',   
        'password': input('Set superuser password: '),
        'host': 'localhost',  
        'port': '5432'        
    }

    # Connect to the default PostgreSQL database
    default_conn = await asyncpg.connect(user='postgres', password='hgcal', host='localhost', port=5432)

    # Create a new database
    db_name = db_params['database']
    print(f'Database name: {db_name}')
    create_db_query = f"CREATE DATABASE {db_name};"
    try:
        await default_conn.execute(create_db_query)
        print(f"Database '{db_name}' successfully created.")
    except asyncpg.exceptions.DuplicateDatabaseError:
        print(f"Database '{db_name}' already exists. New database has NOT been created.")

    await default_conn.close()

    # Connect to the newly created database
    conn = await asyncpg.connect(**db_params)
    print(f"Connected to database '{db_name}' successfully.\n")

    # Create user roles and assign privileges
    async def create_role(role_name, user_type):
        # Create the new role (user) if it doesn't exist
        try:
            user_password = input('Set {} password: '.format(user_type))
            create_role_query = f"CREATE ROLE {role_name} LOGIN PASSWORD '{user_password}';"
            await conn.execute(create_role_query)
            print(f"Role '{role_name}' for '{user_type}' created.")
        except asyncpg.exceptions.DuplicateObjectError:
            print(f"Role '{role_name}' already exists. Continuing...")
        
        try:
            await conn.execute(f"GRANT CONNECT ON DATABASE {db_name} TO {role_name};")
            await conn.execute(f"GRANT USAGE ON SCHEMA public TO {role_name};")
        except asyncpg.exceptions.InsufficientPrivilegeError:
            print(f"Permissions for '{role_name}' already exist.\n")

    role_names_list = ['ogp_user', 'gantry_user', 'viewer', 'teststand_user', 'shipper']
    role_types_list = ['OGP computer user', 'Gantry computer user', 'table viewer', 'Test-stand user', 'Shipping user']
    for role_name, role_type in zip(role_names_list, role_types_list):
        await create_role(role_name, role_type)

    await conn.close()

    print("Database creation successful!!!\n")

# if __name__ == "__main__":
asyncio.run(create_db())

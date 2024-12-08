import os
import asyncpg
from datetime import datetime
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from server.models.wallet_transaction import TransactionType
from server.models import Base
import pandas as pd
import os
from .models import (
    Address,
    Category,
    Item,
    OrderSlot,
    Supermarket,
    User,
    Wallet,
    StockLevel,
    SupermarketCategory,
    WalletTransaction
) 

# Load environment variables
load_dotenv()

# Database credentials and URL
DB_USERNAME = os.getenv('DATABASE_USER')
DB_PASSWORD = os.getenv('DATABASE_PASSWORD')
DB_HOST = os.getenv('DATABASE_HOST')
DB_PORT = os.getenv('DATABASE_PORT')
DB_NAME = os.getenv('DATABASE_NAME')
DATABASE_URL = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create asynchronous engine and session maker
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def setup_database():
    # Connect to the default 'postgres' database to manage databases
    admin_conn = await asyncpg.connect(user=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database="postgres")
    try:
        exists = await admin_conn.fetchval("SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname=$1)", DB_NAME)
        if not exists:
            await admin_conn.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database {DB_NAME} created.")
        else:
            print(f"Database {DB_NAME} already exists.")
    finally:
        await admin_conn.close()

    # Initialize tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Mapping of filenames to models
MODEL_MAPPING = {
    "addresses.csv": Address,
    "categories.csv": Category,
    "items.csv": Item,
    "order_slots.csv": OrderSlot,
    "stock_levels.csv": StockLevel,
    "supermarkets.csv": Supermarket,
    "users.csv": User,
    "wallet.csv": Wallet,
    "supermarket_categories.csv" : SupermarketCategory,
    "wallet_transactions.csv" : WalletTransaction
}

async def populate_addresses(session: AsyncSession, file_path: str):
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        address = Address(building_name=row["building_name"])
        session.add(address)
    await session.commit()
    print("Addresses populated successfully.")


async def populate_categories(session: AsyncSession, file_path: str):
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        category = Category(name=row["name"])
        session.add(category)
    await session.commit()
    print("Categories populated successfully.")


async def populate_supermarkets(session: AsyncSession, file_path: str):
    # Ensure the first row is used as headers and columns are correctly aligned
    df = pd.read_csv(file_path, header=0, index_col=None)  # Prevent using any column as the index
    #print("CSV Columns:", df.columns)
    #print("CSV Data Preview:", df.head())

    for _, row in df.iterrows():
        print(f"Processing row: {row}")  # Debugging log

        # Correctly map CSV columns to model fields
        supermarket = Supermarket(
            name=row["name"],             
            address=row["address"],       
            phone_number=row["phone_number"],
            photo_url=row.get("photo_url"),
            delivery_fee=row['delivery_fee']
        )
        session.add(supermarket)

    await session.commit()
    print("Supermarkets populated successfully.")


async def populate_items(session: AsyncSession, file_path: str):
    df = pd.read_csv(file_path)

    # Directly use IDs from CSV
    for _, row in df.iterrows():
        item = Item(
            name=row["name"],
            photo_url=row["photo_url"],
            price=row["price"],
            description=row["description"],
            category_id=row["category_id"], 
            supermarket_id=row["supermarket_id"]
        )
        session.add(item)

    await session.commit()
    print("Items populated successfully.")



async def populate_order_slots(session: AsyncSession, file_path: str):
    df = pd.read_csv(file_path)
    supermarkets = await session.execute(select(Supermarket))
    supermarket_map = {supermarket.name: supermarket.id for supermarket in supermarkets.scalars()}

    for _, row in df.iterrows():
        order_slot = OrderSlot(
            delivery_time=row["delivery_time"],
            supermarket_id=row["supermarket_id"]
        )
        session.add(order_slot)
    await session.commit()
    print("Order Slots populated successfully.")


async def populate_users(session: AsyncSession, file_path: str):
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        user = User(name=row["name"], default_address_id=row['default_address_id'])
        session.add(user)
    await session.commit()
    print("Users populated successfully.")


async def populate_wallets(session: AsyncSession, file_path: str):
    df = pd.read_csv(file_path)

    for _, row in df.iterrows():
        wallet = Wallet(user_id=row["user_id"])
        session.add(wallet)
    await session.commit()
    print("Wallets populated successfully.")


async def populate_stock_levels(session: AsyncSession, file_path: str):
    df = pd.read_csv(file_path)

    for _, row in df.iterrows():
        stock_level = StockLevel(
            item_id=row["item_id"],
            supermarket_id=row["supermarket_id"],
            quantity=row["quantity"],
        )
        session.add(stock_level)
    await session.commit()
    print("Stock Levels populated successfully.")


async def populate_supermarket_categories(session: AsyncSession, file_path: str):
    df = pd.read_csv(file_path)

    # Validate numeric values
    invalid_rows = []

    for _, row in df.iterrows():
        supermarket_id = row["supermarket_id"]
        category_id = row["category_id"]

        # Check for null or invalid values
        if not pd.notna(supermarket_id) or not pd.notna(category_id):
            invalid_rows.append(row)
            continue

        # Ensure values are integers
        try:
            supermarket_id = int(supermarket_id)
            category_id = int(category_id)
        except ValueError:
            invalid_rows.append(row)
            continue

        # Create SupermarketCategory entry
        supermarket_category = SupermarketCategory(
            supermarket_id=supermarket_id,
            category_id=category_id,
        )
        session.add(supermarket_category)

    # Commit valid rows
    await session.commit()
    print("Supermarket Categories populated successfully.")

    # Log invalid rows
    if invalid_rows:
        print("The following rows were skipped due to invalid data:")
        print(pd.DataFrame(invalid_rows))

async def populate_wallet_transactions(session: AsyncSession, file_path: str):
    df = pd.read_csv(file_path)

    for _, row in df.iterrows():
        # Validate transaction_type to ensure correct values
        if row["transaction_type"] not in ["credit", "debit"]:
            print(f"Invalid transaction type in row: {row}")
            continue

        created_at = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")


        # Map transaction_type string to TransactionType enum
        try:
            transaction_type = TransactionType[row["transaction_type"].upper()]
        except KeyError:
            print(f"Invalid transaction type in row: {row}")
            continue

        # Create WalletTransaction object
        transaction = WalletTransaction(
            user_id=row["user_id"],
            wallet_id=row["wallet_id"],
            amount=row["amount"],
            transaction_type=transaction_type, 
            created_at=created_at
        )
        session.add(transaction)

    # Commit the transactions
    await session.commit()
    print("Wallet Transactions populated successfully.")

async def populate_database():
    async with SessionLocal() as session:
        data_folder = "./server/data/"

        # File-to-function mapper
        FUNCTION_MAPPING = {
            "addresses.csv": populate_addresses,
            "categories.csv": populate_categories,
            "supermarkets.csv": populate_supermarkets,
            "items.csv": populate_items,
            "order_slots.csv": populate_order_slots,
            "users.csv": populate_users,
            "wallet.csv": populate_wallets,
            "wallet_transactions.csv": populate_wallet_transactions, 
            "stock_levels.csv": populate_stock_levels,
            "supermarket_categories.csv": populate_supermarket_categories,
        }

        try:
            for file_name, populate_function in FUNCTION_MAPPING.items():
                file_path = os.path.join(data_folder, file_name)
                if os.path.exists(file_path):
                    await populate_function(session, file_path)
                else:
                    print(f"File {file_name} not found, skipping.")
            print("Database population completed successfully.")
        except Exception as e:
            await session.rollback()
            print(f"Error populating database: {e}")

async def drop_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("All tables dropped successfully.")
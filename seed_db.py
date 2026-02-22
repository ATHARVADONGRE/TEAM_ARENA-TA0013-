"""Quick seed script"""
from app import create_app
from demo_data import seed_demo_data

app = create_app()
with app.app_context():
    print("Seeding database...")
    seed_demo_data()
    print("Done!")

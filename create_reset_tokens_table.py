from main import app, db
from models import PasswordReset

def create_reset_tokens_table():
    """Create the password_reset_tokens table"""
    with app.app_context():
        try:
            # Create the table
            db.create_all()
            print("✅ Password reset tokens table created successfully!")
            
            # Verify the table exists
            result = db.engine.execute("SELECT * FROM password_reset_tokens LIMIT 1")
            print("✅ Table verification successful!")
            
        except Exception as e:
            print(f"❌ Error creating table: {str(e)}")

if __name__ == "__main__":
    create_reset_tokens_table() 
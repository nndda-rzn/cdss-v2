"""Script to reset active HiResCAM configuration in database to match defaults."""
import sys
from pathlib import Path

# Add backend directory to python path
sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.db.models.system_config import SystemConfig
from app.extensions import db
from app.services.hirescam.config import HiResCAMConfig
from app.services.hirescam.config_store import CONFIG_KEY, save_config


def main():
    app = create_app()
    with app.app_context():
        # Retrieve active config row
        row = db.session.query(SystemConfig).filter(SystemConfig.key == CONFIG_KEY).first()
        if row is not None:
            print("Found active hirescam_config in DB. Deleting to reset to defaults...")
            db.session.delete(row)
        
        # Save default configuration explicitly
        default_config = HiResCAMConfig()
        save_config(db.session, default_config, user_id=None)
        db.session.commit()
        print("Successfully reset DB hirescam_config to Kaggle-aligned defaults!")

if __name__ == "__main__":
    main()

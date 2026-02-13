import os
import firebase_admin
from firebase_admin import credentials, firestore

_db = None
_firebase_enabled = False


def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    global _db, _firebase_enabled
    if _db is not None:
        return _db
    
    if _firebase_enabled is False:
        # Already tried and failed
        return None

    # Check if already initialized
    if not firebase_admin._apps:
        try:
            # Use service account key if available, otherwise use project ID
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
            
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                _db = firestore.client()
                _firebase_enabled = True
                print("[INFO] Firebase initialized with service account")
                return _db
            else:
                # Try using project ID from environment
                project_id = os.getenv("FIREBASE_PROJECT_ID")
                if project_id:
                    firebase_admin.initialize_app(options={
                        'projectId': project_id,
                    })
                    _db = firestore.client()
                    _firebase_enabled = True
                    print(f"[INFO] Firebase initialized with project ID: {project_id}")
                    return _db
                else:
                    print("[WARNING] Firebase not configured. Set FIREBASE_PROJECT_ID or FIREBASE_SERVICE_ACCOUNT_KEY in .env")
                    print("[INFO] System will work WITHOUT Firebase persistence")
                    _firebase_enabled = False
                    return None
                    
        except Exception as e:
            print(f"[ERROR] Firebase initialization failed: {e}")
            print("[INFO] System will work WITHOUT Firebase persistence")
            _firebase_enabled = False
            return None
    else:
        try:
            _db = firestore.client()
            _firebase_enabled = True
            return _db
        except Exception as e:
            print(f"[ERROR] Failed to get Firestore client: {e}")
            _firebase_enabled = False
            return None


def get_firestore():
    """Get Firestore client instance."""
    if _db is None:
        return initialize_firebase()
    return _db


def is_firebase_enabled():
    """Check if Firebase is properly configured."""
    return _firebase_enabled

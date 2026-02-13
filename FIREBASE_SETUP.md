# Firebase Setup Instructions

## Quick Setup (for Hackathon Demo)

### Option 1: Using Project ID (Fastest - No Auth)

Add to `backend/.env`:
```
FIREBASE_PROJECT_ID=smart-irrigation-system-f87ad
```

**Note**: This uses the existing Firebase project ID from the frontend config. You may need to enable Firestore in the Firebase Console.

### Option 2: Using Service Account (Production)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: `smart-irrigation-system-f87ad`
3. Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Download the JSON file
6. Save it as `backend/serviceAccountKey.json`

Add to `backend/.env`:
```
FIREBASE_SERVICE_ACCOUNT_KEY=backend/serviceAccountKey.json
```

**Security**: Add `serviceAccountKey.json` to `.gitignore`!

## Enable Firestore

1. Open [Firebase Console](https://console.firebase.google.com/)
2. Go to Firestore Database
3. Click "Create Database"
4. Choose "Start in production mode" (or test mode for demo)
5. Select region (asia-south1 recommended for India)

## Collections Created Automatically

When you create a crop plan, these collections will be auto-created:
- `crop_plans`
- `crop_calendar`
- `irrigation_schedule`
- `irrigation_logs`

No manual setup required!

## Testing Without Firebase

The system will still work without Firebase - it will just skip storage and show warnings in backend logs. Frontend features work independently.

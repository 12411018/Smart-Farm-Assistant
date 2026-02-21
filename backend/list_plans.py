from database import SessionLocal
from models import CropPlan

session = SessionLocal()
for plan in session.query(CropPlan).all():
    print(plan.user_id, plan.crop_name, plan.id)
session.close()

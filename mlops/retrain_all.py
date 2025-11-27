from mlops.train_irrigation import train_irrigation
from mlops.train_plant_health import train_plant_health

def retrain_all():
    print("\n===============================")
    print(" 🔁 Retraining BOTH models")
    print("===============================\n")

    train_irrigation()
    train_plant_health()

    print("\n🎉 All models retrained successfully!")

if __name__ == "__main__":
    retrain_all()

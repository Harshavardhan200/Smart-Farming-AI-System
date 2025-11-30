from mlops.train_irrigation import train_irrigation
from mlops.train_plant_health import train_plant_health
from mlops.metrics import load_last_metrics, save_metrics
from mlops.utils import set_current_from_version_dir
from mlops.config import IRRIGATION_MODEL_DIR, PLANT_MODEL_DIR


def retrain_all():
    print("\n===============================")
    print(" 🔁 NIGHTLY RETRAIN START ")
    print("===============================\n")

    last = load_last_metrics()
    prev_irr = last.get("irrigation_acc", 0.0)
    prev_plant = last.get("plant_acc", 0.0)

    print(f"📌 Previous Irrigation Acc: {prev_irr}")
    print(f"📌 Previous Plant Acc: {prev_plant}")

    # -------------------------------------------------
    # Always train and ALWAYS create version folder
    # -------------------------------------------------
    irr_acc, irr_version_dir = train_irrigation()
    plant_acc, plant_version_dir = train_plant_health()

    print(f"\n🌱 New Irrigation Acc: {irr_acc}")
    print(f"🌿 New Plant Acc: {plant_acc}")

    print(f"📦 Irrigation version saved at: {irr_version_dir}")
    print(f"📦 Plant version saved at: {plant_version_dir}")

    # -------------------------------------------------
    # Promote to current/ ONLY if accuracy improves
    # -------------------------------------------------
    new_best_irr = prev_irr
    new_best_plant = prev_plant

    # Irrigation promotion
    if irr_acc > prev_irr:
        print("✅ Irrigation model improved → updating current/")
        set_current_from_version_dir(IRRIGATION_MODEL_DIR, irr_version_dir)
        new_best_irr = irr_acc
    else:
        print("⚠ Irrigation model did NOT improve → current model remains unchanged.")

    # Plant-health promotion
    if plant_acc > prev_plant:
        print("✅ Plant-health model improved → updating current/")
        set_current_from_version_dir(PLANT_MODEL_DIR, plant_version_dir)
        new_best_plant = plant_acc
    else:
        print("⚠ Plant-health model did NOT improve → current model remains unchanged.")

    # -------------------------------------------------
    # Update metrics ONLY if improvements
    # -------------------------------------------------
    if (new_best_irr > prev_irr) or (new_best_plant > prev_plant):
        save_metrics(new_best_irr, new_best_plant)
        print("\n✔ Metrics updated with improved accuracies.")
    else:
        print("\nℹ No accuracy improvement → metrics not updated.")

    print("\n===============================")
    print(" ✅ NIGHTLY RETRAIN COMPLETE ")
    print("===============================\n")

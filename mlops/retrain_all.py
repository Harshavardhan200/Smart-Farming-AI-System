from mlops.train_irrigation import train_irrigation
from mlops.train_plant_health import train_plant_health
from mlops.metrics import load_last_metrics, save_metrics
from mlops.utils import (
    set_current_from_version_dir,
    cleanup_old_versions,
    write_nightly_report,
)
from mlops.config import IRRIGATION_MODEL_DIR, PLANT_MODEL_DIR
import os
# Ensure directories always exist
os.makedirs("reports", exist_ok=True)
os.makedirs("mlops", exist_ok=True)

def retrain_all():
    print("\n===============================")
    print(" 🔁 NIGHTLY RETRAIN START ")
    print("===============================\n")

    # Load previous recorded accuracies
    last = load_last_metrics()
    prev_irr = last.get("irrigation_acc", 0.0)
    prev_plant = last.get("plant_acc", 0.0)

    print(f"📌 Previous Irrigation Acc: {prev_irr}")
    print(f"📌 Previous Plant Acc: {prev_plant}")

    # Always train and always save version
    irr_acc, irr_version_dir = train_irrigation()
    plant_acc, plant_version_dir = train_plant_health()

    print(f"\n🌱 New Irrigation Acc: {irr_acc}")
    print(f"🌿 New Plant Acc: {plant_acc}")

    print(f"📦 Irrigation version saved: {irr_version_dir}")
    print(f"📦 Plant version saved: {plant_version_dir}")

    # Track if currents updated
    irr_updated = False
    plant_updated = False

    # Update current/ only if improved
    if irr_acc > prev_irr:
        set_current_from_version_dir(IRRIGATION_MODEL_DIR, irr_version_dir)
        irr_updated = True
        print("✅ Irrigation current model updated.")
    else:
        print("⚠ Irrigation not improved → current unchanged.")

    if plant_acc > prev_plant:
        set_current_from_version_dir(PLANT_MODEL_DIR, plant_version_dir)
        plant_updated = True
        print("✅ Plant current model updated.")
    else:
        print("⚠ Plant not improved → current unchanged.")

    # Save improved metrics
    if irr_updated or plant_updated:
        save_metrics(
            irr_acc if irr_updated else prev_irr,
            plant_acc if plant_updated else prev_plant
        )
        print("✔ Metrics updated.")
    else:
        print("ℹ No accuracy improvement → metrics unchanged.")

    # Auto-delete old versions
    cleanup_old_versions(IRRIGATION_MODEL_DIR, keep_last=30)
    cleanup_old_versions(PLANT_MODEL_DIR, keep_last=30)

    # Write nightly markdown report
    write_nightly_report(
        prev_irr, irr_acc, irr_version_dir, irr_updated,
        prev_plant, plant_acc, plant_version_dir, plant_updated
    )

    print("\n===============================")
    print(" ✅ NIGHTLY RETRAIN COMPLETE ")
    print("===============================\n")
retrain_all()

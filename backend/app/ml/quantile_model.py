import os

import pandas as pd
from sklearn.linear_model import QuantileRegressor


# ---------------------------------------------------------
# DATASET PATH
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "aluminum_training_data.csv"
)


# ---------------------------------------------------------
# LOAD TRAINING DATA
# ---------------------------------------------------------

data = pd.read_csv(DATA_FILE)


# ---------------------------------------------------------
# CREATE ONE QUANTILE REGRESSION MODEL FOR EACH
# MATERIAL + PROCESS COMBINATION
# ---------------------------------------------------------

models = {}

required_columns = {
    "material_type",
    "quantity_kg",
    "process",
    "actual_yield_kg",
}

missing_columns = required_columns - set(data.columns)

if missing_columns:
    raise ValueError(
        f"Training dataset is missing columns: {missing_columns}"
    )


grouped_data = data.groupby(
    ["material_type", "process"]
)


for (material_type, process), group in grouped_data:

    X = group[["quantity_kg"]]
    y = group["actual_yield_kg"]

    models[(material_type, process)] = {}

    # -----------------------------------------------------
    # LOWER QUANTILE - 10%
    # -----------------------------------------------------

    lower_model = QuantileRegressor(
        quantile=0.10,
        alpha=0.0,
        solver="highs",
    )

    lower_model.fit(X, y)

    models[(material_type, process)]["lower"] = lower_model

    # -----------------------------------------------------
    # MEDIAN / EXPECTED QUANTILE - 50%
    # -----------------------------------------------------

    median_model = QuantileRegressor(
        quantile=0.50,
        alpha=0.0,
        solver="highs",
    )

    median_model.fit(X, y)

    models[(material_type, process)]["median"] = median_model

    # -----------------------------------------------------
    # UPPER QUANTILE - 90%
    # -----------------------------------------------------

    upper_model = QuantileRegressor(
        quantile=0.90,
        alpha=0.0,
        solver="highs",
    )

    upper_model.fit(X, y)

    models[(material_type, process)]["upper"] = upper_model


# ---------------------------------------------------------
# PREDICTION FUNCTION
# ---------------------------------------------------------

def predict_yield(
    material_type,
    quantity_kg,
    process,
):
    """
    Predict aluminum yield using Quantile Regression.

    Returns:

        lower_yield
        expected_yield
        upper_yield
    """

    key = (material_type, process)

    # Check whether this material/process combination
    # exists in the training data.
    if key not in models:

        raise ValueError(
            f"No trained model available for "
            f"material '{material_type}' and "
            f"process '{process}'."
        )

    # Quantity must be positive.
    if quantity_kg <= 0:

        raise ValueError(
            "Quantity must be greater than zero."
        )

    # Create input DataFrame
    input_data = pd.DataFrame(
        {
            "quantity_kg": [quantity_kg]
        }
    )

    material_models = models[key]

    # -----------------------------------------------------
    # MAKE THREE PREDICTIONS
    # -----------------------------------------------------

    lower_prediction = material_models["lower"].predict(
        input_data
    )[0]

    expected_prediction = material_models["median"].predict(
        input_data
    )[0]

    upper_prediction = material_models["upper"].predict(
        input_data
    )[0]

    # -----------------------------------------------------
    # SAFETY CHECKS
    # -----------------------------------------------------

    # Yield cannot be negative.
    lower_prediction = max(
        0,
        lower_prediction
    )

    expected_prediction = max(
        0,
        expected_prediction
    )

    upper_prediction = max(
        0,
        upper_prediction
    )

    # Aluminum yield cannot be greater than the
    # amount of input material.
    lower_prediction = min(
        lower_prediction,
        quantity_kg
    )

    expected_prediction = min(
        expected_prediction,
        quantity_kg
    )

    upper_prediction = min(
        upper_prediction,
        quantity_kg
    )

    # -----------------------------------------------------
    # ENSURE QUANTILE ORDER
    # -----------------------------------------------------

    predictions = sorted(
        [
            lower_prediction,
            expected_prediction,
            upper_prediction,
        ]
    )

    lower_prediction = predictions[0]
    expected_prediction = predictions[1]
    upper_prediction = predictions[2]

    # -----------------------------------------------------
    # RETURN RESULTS
    # -----------------------------------------------------

    return {
        "lower_yield": round(
            float(lower_prediction),
            2
        ),

        "expected_yield": round(
            float(expected_prediction),
            2
        ),

        "upper_yield": round(
            float(upper_prediction),
            2
        ),
    }
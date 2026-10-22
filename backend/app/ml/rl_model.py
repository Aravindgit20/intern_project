
import json
import os
import random
import tempfile

from django.db import transaction


# =========================================================
# REINFORCEMENT LEARNING - Q-LEARNING
# =========================================================

Q_TABLE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "q_table.json",
)

ACTIONS = [
    "standard_processing",
    "yield_optimization",
    "waste_reduction",
]

LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EXPLORATION_RATE = 0.1


# =========================================================
# LOAD Q-TABLE
# =========================================================

def load_q_table():
    if not os.path.exists(Q_TABLE_FILE):
        return {}

    try:
        with open(Q_TABLE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return {}

        # Ensure all states contain all supported actions.
        for state in data:
            if not isinstance(data[state], dict):
                data[state] = {}

            for action in ACTIONS:
                data[state].setdefault(action, 0.0)

        return data

    except (json.JSONDecodeError, OSError):
        return {}


# =========================================================
# SAVE Q-TABLE
# =========================================================

def save_q_table(q_table):
    directory = os.path.dirname(Q_TABLE_FILE)
    os.makedirs(directory, exist_ok=True)

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            delete=False,
            suffix=".tmp",
        ) as file:
            json.dump(q_table, file, indent=4)
            temporary_path = file.name

        # Replace the old file only after the new file is written.
        os.replace(temporary_path, Q_TABLE_FILE)

    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)


# =========================================================
# CREATE STATE
# =========================================================

def create_state(
    material_type,
    predicted_yield,
    waste_quantity=None,
):
    material_type = str(material_type).lower().strip()

    predicted_yield = max(
        0.0,
        float(predicted_yield or 0),
    )

    if predicted_yield < 20:
        yield_level = "low"
    elif predicted_yield < 50:
        yield_level = "medium"
    else:
        yield_level = "high"

    # Waste is unknown before processing starts.
    if waste_quantity is None:
        waste_level = "unknown"
    else:
        waste_quantity = max(
            0.0,
            float(waste_quantity),
        )

        if waste_quantity <= 10:
            waste_level = "low"
        elif waste_quantity <= 30:
            waste_level = "medium"
        else:
            waste_level = "high"

    return (
        f"{material_type}_"
        f"{yield_level}_"
        f"{waste_level}"
    )


# =========================================================
# ENSURE STATE EXISTS
# =========================================================

def ensure_state(q_table, state):
    if state not in q_table:
        q_table[state] = {}

    if not isinstance(q_table[state], dict):
        q_table[state] = {}

    for action in ACTIONS:
        q_table[state].setdefault(action, 0.0)


# =========================================================
# GET Q-VALUES
# =========================================================

def get_q_values(state):
    q_table = load_q_table()

    ensure_state(q_table, state)

    save_q_table(q_table)

    return q_table[state]


# =========================================================
# SELECT ACTION - EPSILON-GREEDY
# =========================================================

def choose_action(
    state,
    explore=True,
    epsilon=EXPLORATION_RATE,
):
    q_table = load_q_table()

    ensure_state(q_table, state)

    if explore and random.random() < epsilon:
        # Exploration: try a random action.
        action = random.choice(ACTIONS)

    else:
        # Exploitation: select the action with the highest Q-value.
        best_value = max(
            q_table[state].values()
        )

        best_actions = [
            action
            for action in ACTIONS
            if q_table[state][action] == best_value
        ]

        # Random tie-breaking when actions have equal values.
        action = random.choice(best_actions)

    save_q_table(q_table)

    return action


# =========================================================
# PREPARE PROCESSING
#
# Call when the Scrap Team starts processing.
# Save the returned state and action on RawMaterial.
# =========================================================

def prepare_processing(
    material_type,
    predicted_yield,
):
    state = create_state(
        material_type=material_type,
        predicted_yield=predicted_yield,
        waste_quantity=None,
    )

    action = choose_action(
        state=state,
        explore=True,
    )

    return {
        "state": state,
        "action": action,
    }


# =========================================================
# CALCULATE REWARD
#
# Higher recovery and prediction accuracy are rewarded.
# Greater waste is penalized.
#
# These are demo reward rules, not industrial standards.
# =========================================================

def calculate_reward(
    predicted_yield,
    actual_yield,
    waste_quantity,
):
    predicted_yield = float(predicted_yield or 0)
    actual_yield = float(actual_yield or 0)
    waste_quantity = float(waste_quantity or 0)

    if (
        predicted_yield < 0
        or actual_yield < 0
        or waste_quantity < 0
    ):
        raise ValueError(
            "Yield and waste values cannot be negative."
        )

    if actual_yield <= 0:
        return -10.0

    if predicted_yield > 0:
        prediction_error = abs(
            predicted_yield - actual_yield
        )

        accuracy_score = max(
            -1.0,
            1.0 - prediction_error / predicted_yield,
        )

    else:
        accuracy_score = -1.0

    yield_reward = actual_yield / 10.0
    waste_penalty = waste_quantity / 10.0

    reward = (
        yield_reward
        + accuracy_score * 5.0
        - waste_penalty
    )

    return round(reward, 2)


# =========================================================
# UPDATE Q-VALUE
#
# Q(s,a) = Q(s,a) + alpha *
#          [reward + gamma * max Q(next_state) - Q(s,a)]
#
# Completed processing is a terminal transition, so done=True
# means there is no future-state bootstrap in that update.
# =========================================================

def update_q_value(
    state,
    action,
    reward,
    next_state=None,
    done=True,
    learning_rate=LEARNING_RATE,
    discount_factor=DISCOUNT_FACTOR,
):
    if action not in ACTIONS:
        raise ValueError(
            f"Unknown processing action: {action}"
        )

    q_table = load_q_table()

    ensure_state(q_table, state)

    if next_state is not None:
        ensure_state(q_table, next_state)

    current_q = float(
        q_table[state][action]
    )

    if done or next_state is None:
        max_future_q = 0.0
    else:
        max_future_q = max(
            q_table[next_state].values()
        )

    new_q = current_q + learning_rate * (
        float(reward)
        + discount_factor * max_future_q
        - current_q
    )

    q_table[state][action] = round(
        new_q,
        4,
    )

    save_q_table(q_table)

    return q_table[state][action]


# =========================================================
# PROCESS FEEDBACK
#
# Call only after all stages for a material are completed.
# Pass the action and state saved when processing started.
#
# When material is supplied:
# - Protects against duplicate RLFeedback records.
# - Saves feedback to the database.
# - Marks RawMaterial.rl_processed = True.
# =========================================================

def process_feedback(
    material_type,
    predicted_yield,
    actual_yield,
    waste_quantity,
    state=None,
    action=None,
    material=None,
):
    from processing.models import (
        RLFeedback,
        RawMaterial,
    )

    predicted_yield = float(predicted_yield)
    actual_yield = float(actual_yield)
    waste_quantity = float(waste_quantity)

    if predicted_yield < 0:
        raise ValueError(
            "Predicted yield cannot be negative."
        )

    if actual_yield < 0 or waste_quantity < 0:
        raise ValueError(
            "Actual yield and waste cannot be negative."
        )

    # Fallback for callers that do not provide a saved state.
    if state is None:
        state = create_state(
            material_type=material_type,
            predicted_yield=predicted_yield,
            waste_quantity=None,
        )

    if action is None:
        action = choose_action(
            state=state,
            explore=False,
        )

    if action not in ACTIONS:
        raise ValueError(
            f"Unknown processing action: {action}"
        )

    next_state = create_state(
        material_type=material_type,
        predicted_yield=actual_yield,
        waste_quantity=waste_quantity,
    )

    reward = calculate_reward(
        predicted_yield=predicted_yield,
        actual_yield=actual_yield,
        waste_quantity=waste_quantity,
    )

    # -----------------------------------------------------
    # DATABASE-BACKED FEEDBACK
    # -----------------------------------------------------

    if material is not None:

        with transaction.atomic():

            locked_material = (
                RawMaterial.objects
                .select_for_update()
                .get(pk=material.pk)
            )

            existing = (
                RLFeedback.objects
                .filter(material=locked_material)
                .order_by("-created_at")
                .first()
            )

            # Do not create duplicate feedback.
            if (
                locked_material.rl_processed
                or existing is not None
            ):

                return {
                    "state": (
                        existing.rl_state
                        if existing
                        else locked_material.rl_state
                    ),
                    "next_state": next_state,
                    "action": (
                        existing.rl_action
                        if existing
                        else locked_material.rl_action
                    ),
                    "reward": (
                        existing.reward
                        if existing
                        else reward
                    ),
                    "updated_q_value": (
                        existing.q_value
                        if existing
                        else None
                    ),
                    "already_processed": True,
                }

            # Use the persisted decision if the caller omitted it.
            state_to_save = (
                state
                or locked_material.rl_state
            )

            action_to_save = (
                action
                or locked_material.rl_action
            )

            if action_to_save not in ACTIONS:
                raise ValueError(
                    f"Unknown processing action: {action_to_save}"
                )

            updated_q_value = update_q_value(
                state=state_to_save,
                action=action_to_save,
                reward=reward,
                next_state=next_state,
                done=True,
            )

            RLFeedback.objects.create(
                material=locked_material,
                predicted_yield=predicted_yield,
                actual_yield=actual_yield,
                waste_quantity=waste_quantity,
                rl_state=state_to_save,
                rl_action=action_to_save,
                reward=reward,
                q_value=updated_q_value,
            )

            locked_material.actual_yield = actual_yield
            locked_material.waste_quantity = waste_quantity
            locked_material.rl_state = state_to_save
            locked_material.rl_action = action_to_save
            locked_material.rl_processed = True

            locked_material.save(
                update_fields=[
                    "actual_yield",
                    "waste_quantity",
                    "rl_state",
                    "rl_action",
                    "rl_processed",
                ]
            )

            return {
                "state": state_to_save,
                "next_state": next_state,
                "action": action_to_save,
                "reward": reward,
                "updated_q_value": updated_q_value,
                "already_processed": False,
            }

    # -----------------------------------------------------
    # FALLBACK: NO RAWMATERIAL INSTANCE PROVIDED
    #
    # This calculates feedback and updates the Q-table,
    # but cannot create an RLFeedback linked to a material.
    # -----------------------------------------------------

    updated_q_value = update_q_value(
        state=state,
        action=action,
        reward=reward,
        next_state=next_state,
        done=True,
    )

    return {
        "state": state,
        "next_state": next_state,
        "action": action,
        "reward": reward,
        "updated_q_value": updated_q_value,
        "already_processed": False,
    }

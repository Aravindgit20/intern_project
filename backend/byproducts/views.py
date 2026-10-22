
from django.shortcuts import redirect
from django.db import transaction

from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ByProduct

from processing.models import (
    RawMaterial,
    RLFeedback,
)

from processing.services import generate_byproducts

from app.ml.rl_model import (
    prepare_processing,
    process_feedback,
)


# =============================================================
# SIMULATED PROCESSING RESULT
# Demo assumptions only; not industrial measurements.
# =============================================================

def calculate_simulated_result(material, action=None):

    material_type = material.material_type.lower()

    if material_type == "bauxite":

        recovery_factor = 0.95

        if action == "yield_optimization":
            recovery_factor = 0.97

        elif action == "waste_reduction":
            recovery_factor = 0.93

    elif material_type == "scrap_aluminum":

        recovery_factor = 0.97

        if action == "yield_optimization":
            recovery_factor = 0.985

        elif action == "waste_reduction":
            recovery_factor = 0.95

    else:
        recovery_factor = 0.95

    predicted_yield = float(
        material.predicted_yield or 0
    )

    input_quantity = float(
        material.quantity or 0
    )

    actual_yield = round(
        predicted_yield * recovery_factor,
        2
    )

    # Count the final by-product quantities without overlap.
    byproduct_total = sum(
        float(item.quantity or 0)
        for item in ByProduct.objects.filter(
            raw_material=material
        )
    )

    waste_quantity = round(
        input_quantity - actual_yield - byproduct_total,
        2
    )

    if actual_yield < 0 or waste_quantity < 0:
        raise ValueError(
            "The simulated outputs exceed the input quantity. "
            "Check the yield prediction and by-product quantities."
        )

    return actual_yield, waste_quantity


# =============================================================
# HELPERS
# =============================================================

def get_stage_name(byproduct_type):

    if byproduct_type == "Aluminum Dross / Residue":
        return (
            "Stage 1 - "
            "Aluminum Recycling / Refining"
        )

    if byproduct_type == "Manganese Alloy":
        return (
            "Stage 2 - "
            "Manganese Recovery / Alloying"
        )

    if byproduct_type == "Red Mud":
        return (
            "Bayer Process - "
            "Alumina Extraction"
        )

    return None


def get_latest_feedback(material):

    return (
        RLFeedback.objects
        .filter(material=material)
        .order_by("-created_at")
        .first()
    )


def prepare_material_for_processing(material):

    if material.rl_state and material.rl_action:
        return

    decision = prepare_processing(
        material_type=material.material_type,
        predicted_yield=material.predicted_yield,
    )

    material.rl_state = decision["state"]
    material.rl_action = decision["action"]

    material.save(
        update_fields=[
            "rl_state",
            "rl_action",
        ]
    )


# =============================================================
# SCRAP DASHBOARD
# =============================================================

def scrap_dashboard(request):

    if not request.user.is_authenticated:
        return redirect("/login/")

    if request.user.role != "scrap_team":
        return redirect("/")

    return redirect("/scrap/")


# =============================================================
# API: SCRAP TEAM BY-PRODUCTS
# =============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_scrap_byproducts(request):

    if request.user.role != "scrap_team":
        return Response(
            {"error": "Access denied."},
            status=403,
        )

    materials = (
        RawMaterial.objects
        .select_related("agent")
        .order_by("-submitted_at")
    )

    data = []

    for material in materials:

        material_byproducts = list(
            ByProduct.objects
            .filter(raw_material=material)
            .order_by("id")
        )

        feedback = get_latest_feedback(material)

        # Material has not started processing.
        if not material_byproducts:

            if material.material_type.lower() == "bauxite":
                pending_type = "Red Mud"
                stage = (
                    "Bayer Process - "
                    "Alumina Extraction"
                )
            else:
                pending_type = "Aluminum Dross / Residue"
                stage = (
                    "Stage 1 - "
                    "Aluminum Recycling / Refining"
                )

            data.append({
                "id": None,
                "material_id": material.id,
                "byproduct_id": None,
                "byproduct_type": pending_type,
                "quantity": None,
                "status": "pending",
                "product_id": material.product_id,
                "raw_material": (
                    material.get_material_type_display()
                ),
                "stage": stage,
                "lower_yield": material.lower_yield,
                "predicted_yield": material.predicted_yield,
                "upper_yield": material.upper_yield,
                "actual_yield": material.actual_yield,
                "waste_quantity": material.waste_quantity,
                "rl_processed": material.rl_processed,
                "rl_state": material.rl_state,
                "rl_action": material.rl_action,
                "reward": (
                    feedback.reward if feedback else None
                ),
                "q_value": (
                    feedback.q_value if feedback else None
                ),
                "potential_applications": [],
                "processing_started": False,
            })

            continue

        # Material has started processing.
        for byproduct in material_byproducts:

            potential_applications = []

            if byproduct.status == "completed":
                potential_applications = (
                    byproduct.potential_applications or []
                )

            data.append({
                "id": byproduct.id,
                "material_id": material.id,
                "byproduct_id": byproduct.id,
                "byproduct_type": byproduct.byproduct_type,
                "quantity": byproduct.quantity,
                "status": byproduct.status,
                "product_id": material.product_id,
                "raw_material": (
                    material.get_material_type_display()
                ),
                "stage": get_stage_name(
                    byproduct.byproduct_type
                ),
                "lower_yield": material.lower_yield,
                "predicted_yield": material.predicted_yield,
                "upper_yield": material.upper_yield,
                "actual_yield": material.actual_yield,
                "waste_quantity": material.waste_quantity,
                "rl_processed": material.rl_processed,
                "rl_state": material.rl_state,
                "rl_action": material.rl_action,
                "reward": (
                    feedback.reward if feedback else None
                ),
                "q_value": (
                    feedback.q_value if feedback else None
                ),
                "potential_applications": (
                    potential_applications
                ),
                "processing_started": True,
            })

    return Response(data)


# =============================================================
# API: UPDATE BY-PRODUCT STATUS
# =============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_update_byproduct(request):

    if request.user.role != "scrap_team":
        return Response(
            {"error": "Access denied."},
            status=403,
        )

    byproduct_id = request.data.get("byproduct_id")
    material_id = request.data.get("material_id")
    new_status = request.data.get("status")

    if new_status not in ["in_progress", "completed"]:
        return Response(
            {"error": "Invalid status."},
            status=400,
        )

    # ---------------------------------------------------------
    # START PROCESSING FOR A NEW MATERIAL
    # ---------------------------------------------------------

    if (
        not byproduct_id
        and material_id
        and new_status == "in_progress"
    ):

        try:

            with transaction.atomic():

                material = (
                    RawMaterial.objects
                    .select_for_update()
                    .get(id=material_id)
                )

                if ByProduct.objects.filter(
                    raw_material=material
                ).exists():

                    return Response(
                        {
                            "error": (
                                "Processing has already been started."
                            )
                        },
                        status=400,
                    )

                if material.predicted_yield is None:
                    return Response(
                        {
                            "error": (
                                "Yield prediction is not available."
                            )
                        },
                        status=400,
                    )

                prepare_material_for_processing(material)

                created_byproducts = generate_byproducts(
                    material
                )

                if not created_byproducts:
                    return Response(
                        {
                            "error": (
                                "Unable to generate by-products."
                            )
                        },
                        status=400,
                    )

                if material.material_type.lower() == "bauxite":

                    first_byproduct = next(
                        (
                            item
                            for item in created_byproducts
                            if item.byproduct_type == "Red Mud"
                        ),
                        None,
                    )

                    success_message = (
                        "Bauxite processing started successfully."
                    )

                elif (
                    material.material_type.lower()
                    == "scrap_aluminum"
                ):

                    first_byproduct = next(
                        (
                            item
                            for item in created_byproducts
                            if item.byproduct_type
                            == "Aluminum Dross / Residue"
                        ),
                        None,
                    )

                    success_message = (
                        "Stage 1 processing started successfully."
                    )

                else:
                    return Response(
                        {"error": "Unsupported material type."},
                        status=400,
                    )

                if first_byproduct is None:
                    raise ValueError(
                        "The first processing stage was not generated."
                    )

                first_byproduct.status = "in_progress"
                first_byproduct.save(
                    update_fields=["status"]
                )

                return Response({
                    "message": success_message,
                    "status": first_byproduct.status,
                    "byproduct_id": first_byproduct.id,
                    "material_id": material.id,
                    "product_id": material.product_id,
                    "byproduct_type": first_byproduct.byproduct_type,
                    "quantity": first_byproduct.quantity,
                    "rl_state": material.rl_state,
                    "rl_action": material.rl_action,
                    "rl_processed": material.rl_processed,
                })

        except RawMaterial.DoesNotExist:
            return Response(
                {"error": "Raw material not found."},
                status=404,
            )

        except (ValueError, TypeError, KeyError) as error:
            return Response(
                {"error": str(error)},
                status=400,
            )

    # ---------------------------------------------------------
    # UPDATE AN EXISTING BY-PRODUCT
    # ---------------------------------------------------------

    if not byproduct_id:
        return Response(
            {"error": "A valid byproduct_id is required."},
            status=400,
        )

    try:

        with transaction.atomic():

            byproduct = (
                ByProduct.objects
                .select_for_update()
                .select_related("raw_material")
                .get(id=byproduct_id)
            )

            material = (
                RawMaterial.objects
                .select_for_update()
                .get(pk=byproduct.raw_material_id)
            )

            if byproduct.status == "completed":
                return Response(
                    {
                        "error": (
                            "This by-product is already completed."
                        )
                    },
                    status=400,
                )

            # Stage 2 requires Stage 1 to be completed.
            if byproduct.byproduct_type == "Manganese Alloy":

                dross = (
                    ByProduct.objects
                    .filter(
                        raw_material=material,
                        byproduct_type=(
                            "Aluminum Dross / Residue"
                        ),
                    )
                    .first()
                )

                if dross is None or dross.status != "completed":
                    return Response(
                        {
                            "error": (
                                "Complete Aluminum Dross / Residue "
                                "processing before starting Manganese "
                                "Alloy processing."
                            )
                        },
                        status=400,
                    )

            # START PROCESSING
            if new_status == "in_progress":

                if byproduct.status == "in_progress":
                    return Response(
                        {
                            "error": (
                                "This by-product is already in progress."
                            )
                        },
                        status=400,
                    )

                if material.predicted_yield is None:
                    return Response(
                        {
                            "error": (
                                "Yield prediction is not available."
                            )
                        },
                        status=400,
                    )

                prepare_material_for_processing(material)

                byproduct.status = "in_progress"
                byproduct.save(
                    update_fields=["status"]
                )

                return Response({
                    "message": "Processing started successfully.",
                    "status": byproduct.status,
                    "byproduct_id": byproduct.id,
                    "material_id": material.id,
                    "product_id": material.product_id,
                    "rl_state": material.rl_state,
                    "rl_action": material.rl_action,
                })

            # COMPLETE PROCESSING
            if byproduct.status != "in_progress":
                return Response(
                    {
                        "error": (
                            "Start processing before completing "
                            "this by-product."
                        )
                    },
                    status=400,
                )

            if material.predicted_yield is None:
                return Response(
                    {
                        "error": (
                            "Yield prediction is not available."
                        )
                    },
                    status=400,
                )

            byproduct.status = "completed"
            byproduct.save(
                update_fields=["status"]
            )

            unfinished_stages = (
                ByProduct.objects
                .filter(raw_material=material)
                .exclude(status="completed")
                .exists()
            )

            if unfinished_stages:
                return Response({
                    "message": (
                        f"{byproduct.byproduct_type} stage completed. "
                        "Complete the remaining stages to record "
                        "final processing results."
                    ),
                    "status": byproduct.status,
                    "byproduct_id": byproduct.id,
                    "material_id": material.id,
                    "product_id": material.product_id,
                    "predicted_yield": material.predicted_yield,
                    "actual_yield": None,
                    "waste_quantity": None,
                    "rl_processed": material.rl_processed,
                    "rl_state": material.rl_state,
                    "rl_action": material.rl_action,
                    "reward": None,
                    "q_value": None,
                    "potential_applications": (
                        byproduct.potential_applications or []
                    ),
                    "all_stages_completed": False,
                })

            # -------------------------------------------------
            # ALL STAGES COMPLETE
            # Adjust dross so manganese alloy is not counted twice.
            # -------------------------------------------------

            if (
                material.material_type.lower() == "scrap_aluminum"
                and byproduct.byproduct_type == "Manganese Alloy"
            ):

                dross = (
                    ByProduct.objects
                    .select_for_update()
                    .filter(
                        raw_material=material,
                        byproduct_type="Aluminum Dross / Residue",
                    )
                    .first()
                )

                if dross is None:
                    raise ValueError(
                        "The Stage 1 dross record was not found."
                    )

                manganese_quantity = float(
                    byproduct.quantity or 0
                )

                remaining_dross = round(
                    float(dross.quantity or 0)
                    - manganese_quantity,
                    2
                )

                if remaining_dross < 0:
                    raise ValueError(
                        "Recovered alloy exceeds the available "
                        "dross quantity."
                    )

                dross.quantity = remaining_dross
                dross.save(
                    update_fields=["quantity"]
                )

            actual_yield, waste_quantity = (
                calculate_simulated_result(
                    material,
                    action=material.rl_action,
                )
            )

            feedback = get_latest_feedback(material)

            # Record feedback once.
            if not material.rl_processed and feedback is None:

                process_feedback(
                    material_type=material.material_type,
                    predicted_yield=material.predicted_yield,
                    actual_yield=actual_yield,
                    waste_quantity=waste_quantity,
                    state=material.rl_state,
                    action=material.rl_action,
                    material=material,
                )

                feedback = get_latest_feedback(material)

                if feedback is None:
                    raise RuntimeError(
                        "RL feedback was not saved successfully."
                    )

            elif feedback is not None:

                actual_yield = feedback.actual_yield
                waste_quantity = feedback.waste_quantity

                if not material.rl_processed:

                    material.actual_yield = actual_yield
                    material.waste_quantity = waste_quantity
                    material.rl_state = feedback.rl_state
                    material.rl_action = feedback.rl_action
                    material.rl_processed = True

                    material.save(
                        update_fields=[
                            "actual_yield",
                            "waste_quantity",
                            "rl_state",
                            "rl_action",
                            "rl_processed",
                        ]
                    )

            else:
                raise RuntimeError(
                    "Material is marked as RL-processed, "
                    "but no RL feedback record exists."
                )

            material.refresh_from_db()
            feedback = get_latest_feedback(material)

            return Response({
                "message": (
                    "All processing stages completed successfully. "
                    "Final results and RL feedback recorded."
                ),
                "status": byproduct.status,
                "byproduct_id": byproduct.id,
                "material_id": material.id,
                "product_id": material.product_id,
                "predicted_yield": material.predicted_yield,
                "actual_yield": material.actual_yield,
                "waste_quantity": material.waste_quantity,
                "rl_processed": material.rl_processed,
                "rl_state": (
                    feedback.rl_state
                    if feedback else material.rl_state
                ),
                "rl_action": (
                    feedback.rl_action
                    if feedback else material.rl_action
                ),
                "reward": (
                    feedback.reward if feedback else None
                ),
                "q_value": (
                    feedback.q_value if feedback else None
                ),
                "potential_applications": (
                    byproduct.potential_applications or []
                ),
                "all_stages_completed": True,
            })

    except ByProduct.DoesNotExist:
        return Response(
            {"error": "By-product not found."},
            status=404,
        )

    except RawMaterial.DoesNotExist:
        return Response(
            {"error": "Raw material not found."},
            status=404,
        )

    except (ValueError, TypeError, KeyError) as error:
        return Response(
            {
                "error": (
                    "Unable to complete processing: "
                    f"{str(error)}"
                )
            },
            status=400,
        )

    except RuntimeError as error:
        return Response(
            {
                "error": (
                    "Processing could not be finalized: "
                    f"{str(error)}"
                )
            },
            status=500,
        )

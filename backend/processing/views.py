
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .forms import RawMaterialForm
from .models import RawMaterial
from .serializers import RawMaterialSerializer

from app.ml.quantile_model import predict_yield


# =============================================================
# HELPER: SET PROCESS STAGE
# =============================================================

def get_process_details(material):
    material_type = material.material_type.lower()

    if material_type == "bauxite":
        material.process_stage = (
            "Bayer Process - Alumina Extraction"
        )
        prediction_process = "Bayer Process"

    elif material_type == "scrap_aluminum":
        material.process_stage = (
            "Aluminum Recycling / Refining"
        )
        prediction_process = "Scrap Recovery"

    else:
        prediction_process = material.process_stage

    return prediction_process


# =============================================================
# PREDICT MATERIAL
#
# Called when an Agent submits a raw material.
#
# This function:
#   1. Predicts lower, expected, and upper yield.
#   2. Saves the prediction.
#   3. Resets previous processing results.
#
# It does NOT:
#   - Generate by-products.
#   - Calculate actual yield or waste.
#   - Select an RL action.
#   - Create RL feedback.
# =============================================================

def predict_material(material):
    prediction_process = get_process_details(material)

    prediction = predict_yield(
        material.material_type,
        material.quantity,
        prediction_process,
    )

    material.lower_yield = round(
        float(prediction["lower_yield"]),
        2,
    )

    material.predicted_yield = round(
        float(prediction["expected_yield"]),
        2,
    )

    material.upper_yield = round(
        float(prediction["upper_yield"]),
        2,
    )

    # Processing has not started yet.
    material.actual_yield = None
    material.waste_quantity = None
    material.rl_processed = False

    # RL state/action are chosen when the Scrap Team
    # actually starts processing.
    material.rl_state = None
    material.rl_action = None

    material.save()

    return material


# =============================================================
# PROCESS MATERIAL
#
# Compatibility helper for existing project code.
#
# This function does not start Scrap Team processing.
# It does not generate by-products or process RL feedback.
# =============================================================

def process_material(
    material,
    actual_yield=None,
    waste_quantity=None,
):
    prediction_process = get_process_details(material)

    # Predict only if prediction values are missing.
    if (
        material.lower_yield is None
        or material.predicted_yield is None
        or material.upper_yield is None
    ):
        prediction = predict_yield(
            material.material_type,
            material.quantity,
            prediction_process,
        )

        material.lower_yield = round(
            float(prediction["lower_yield"]),
            2,
        )

        material.predicted_yield = round(
            float(prediction["expected_yield"]),
            2,
        )

        material.upper_yield = round(
            float(prediction["upper_yield"]),
            2,
        )

    if actual_yield is not None:
        actual_value = float(actual_yield)

        if actual_value < 0:
            raise ValueError(
                "Actual yield cannot be negative."
            )

        material.actual_yield = round(
            actual_value,
            2,
        )

    if waste_quantity is not None:
        waste_value = float(waste_quantity)

        if waste_value < 0:
            raise ValueError(
                "Waste quantity cannot be negative."
            )

        material.waste_quantity = round(
            waste_value,
            2,
        )

    material.save()

    return material


# =============================================================
# SUBMIT MATERIAL - DJANGO PAGE
# =============================================================

@login_required
def submit_material(request):
    if request.method == "POST":
        form = RawMaterialForm(request.POST)

        if form.is_valid():
            material = form.save(commit=False)
            material.agent = request.user

            predict_material(material)

            return redirect("my_submissions")

    else:
        form = RawMaterialForm()

    return render(
        request,
        "submit_material.html",
        {
            "form": form,
        },
    )


# =============================================================
# MY SUBMISSIONS - DJANGO PAGE
# =============================================================

@login_required
def my_submissions(request):
    materials = (
        RawMaterial.objects
        .filter(agent=request.user)
        .order_by("-submitted_at")
    )

    return render(
        request,
        "my_submissions.html",
        {
            "materials": materials,
        },
    )


# =============================================================
# API - MY SUBMISSIONS
# =============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_my_submissions(request):
    materials = (
        RawMaterial.objects
        .filter(agent=request.user)
        .order_by("-submitted_at")
    )

    serializer = RawMaterialSerializer(
        materials,
        many=True,
    )

    return Response(serializer.data)


# =============================================================
# API - SUBMIT MATERIAL
# =============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_submit_material(request):
    form = RawMaterialForm(request.data)

    if not form.is_valid():
        return Response(
            form.errors,
            status=400,
        )

    material = form.save(commit=False)
    material.agent = request.user

    # Agent submission only performs Quantile Regression.
    # Scrap Team processing starts separately.
    predict_material(material)

    serializer = RawMaterialSerializer(material)

    return Response(
        serializer.data,
        status=201,
    )

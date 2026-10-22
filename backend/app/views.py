
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import RegisterForm

from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required

from app.models import User

from processing.forms import RawMaterialForm
from processing.models import RawMaterial
from processing.views import predict_material

from byproducts.models import ByProduct

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# =============================================================
# HOMEPAGE
# =============================================================

def homepage(request):

    return render(
        request,
        'homepage.html'
    )


# =============================================================
# REACT SCRAP DASHBOARD
# =============================================================

@ensure_csrf_cookie
def react_scrap(request):

    return render(
        request,
        'index.html'
    )


# =============================================================
# REGISTRATION
# =============================================================

def register_view(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(
                commit=False
            )

            user.set_password(
                form.cleaned_data['password']
            )

            user.is_approved = False

            user.save()

            return redirect(
                'registration_success'
            )

    else:

        form = RegisterForm()

    return render(
        request,
        'registeration.html',
        {
            'form': form
        }
    )


# =============================================================
# REGISTRATION SUCCESS
# =============================================================

def registration_success(request):

    return render(
        request,
        'registersuccess.html'
    )


# =============================================================
# LOGIN
# =============================================================

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:

            messages.error(
                request,
                'Invalid username or password.'
            )

            return render(
                request,
                'userlogin.html'
            )

        if not user.is_approved:

            messages.error(
                request,
                'Your account is pending admin approval.'
            )

            return render(
                request,
                'userlogin.html'
            )

        login(
            request,
            user
        )

        # =====================================================
        # ADMIN
        # =====================================================

        if user.role == 'admin':

            return redirect(
                'admin_dashboard'
            )

        # =====================================================
        # AGENT → REACT
        # =====================================================

        elif user.role == 'agent':

            return redirect(
                '/react-agent/'
            )

        # =====================================================
        # SCRAP TEAM → REACT
        # =====================================================

        elif user.role == 'scrap_team':

            return redirect(
                '/react-scrap/'
            )

        # =====================================================
        # INVALID ROLE
        # =====================================================

        else:

            logout(request)

            messages.error(
                request,
                'Invalid user role.'
            )

            return render(
                request,
                'userlogin.html'
            )

    return render(
        request,
        'userlogin.html'
    )


# =============================================================
# CURRENT USER API
# =============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_current_user(request):

    return Response({

        'id':
            request.user.id,

        'username':
            request.user.username,

        'role':
            request.user.role,

    })


# =============================================================
# OLD DJANGO AGENT DASHBOARD
#
# IMPORTANT:
# This old page now follows the same workflow:
#
# Agent submits
#      ↓
# Prediction only
#      ↓
# No by-products generated here
#      ↓
# Scrap Team processes later
# =============================================================

@login_required
def agent_dashboard(request):

    if request.user.role != 'agent':

        return redirect(
            'home'
        )

    if request.method == 'POST':

        form = RawMaterialForm(
            request.POST
        )

        if form.is_valid():

            material = form.save(
                commit=False
            )

            material.agent = request.user

            # -------------------------------------------------
            # Prediction only.
            #
            # This does NOT generate by-products.
            # -------------------------------------------------

            predict_material(
                material
            )

            return redirect(
                'agent_dashboard'
            )

    else:

        form = RawMaterialForm()

    materials = (
        RawMaterial.objects
        .filter(
            agent=request.user
        )
        .order_by(
            '-submitted_at'
        )
    )

    return render(
        request,
        'agent_dashboard.html',
        {
            'form': form,
            'materials': materials
        }
    )


# =============================================================
# SCRAP TEAM DASHBOARD
#
# Old Django URL redirects to React.
# =============================================================

@login_required
def scrap_dashboard(request):

    if request.user.role != 'scrap_team':

        return redirect(
            'home'
        )

    return redirect(
        '/react-scrap/'
    )


# =============================================================
# ADMIN DASHBOARD
# =============================================================

@login_required
def admin_dashboard(request):

    if request.user.role != 'admin':

        return redirect(
            'home'
        )

    pending_users = User.objects.filter(
        is_approved=False,
        role__in=[
            'agent',
            'scrap_team'
        ]
    )

    context = {

        'pending_users':
            pending_users,

        'pending_count':
            pending_users.count(),

        'total_submissions':
            RawMaterial.objects.count(),

        'total_byproducts':
            ByProduct.objects.count(),

        'pending_byproducts':
            ByProduct.objects.filter(
                status='pending'
            ).count(),

        'completed_byproducts':
            ByProduct.objects.filter(
                status='completed'
            ).count(),

    }

    return render(
        request,
        'admin_dashboard.html',
        context
    )


# =============================================================
# LOGOUT
# =============================================================

def logout_view(request):

    logout(request)

    return redirect(
        'login'
    )


# =============================================================
# MANAGE USERS
# =============================================================

@login_required
def manage_users(request):

    if request.user.role != 'admin':

        return redirect(
            'home'
        )

    users = (
        User.objects
        .filter(
            role__in=[
                'agent',
                'scrap_team'
            ]
        )
        .order_by(
            'id'
        )
    )

    return render(
        request,
        'manage_users.html',
        {
            'users': users
        }
    )


# =============================================================
# APPROVE USER
# =============================================================

@login_required
def approve_user(request, user_id):

    if request.user.role != 'admin':

        return redirect(
            'home'
        )

    if request.method == 'POST':

        try:

            user = User.objects.get(
                id=user_id,
                role__in=[
                    'agent',
                    'scrap_team'
                ]
            )

            user.is_approved = True

            user.save(
                update_fields=[
                    'is_approved'
                ]
            )

        except User.DoesNotExist:

            pass

    return redirect(
        'manage_users'
    )


# =============================================================
# DELETE USER
# =============================================================

@login_required
def delete_user(request, user_id):

    if request.user.role != 'admin':

        return redirect(
            'home'
        )

    if request.method == 'POST':

        try:

            user = User.objects.get(
                id=user_id,
                role__in=[
                    'agent',
                    'scrap_team'
                ]
            )

            user.delete()

        except User.DoesNotExist:

            pass

    return redirect(
        'manage_users'
    )


# =============================================================
# MANAGE OPERATIONS
# =============================================================

@login_required
def manage_operations(request):

    if request.user.role != 'admin':

        return redirect(
            'home'
        )

    materials = (
        RawMaterial.objects
        .all()
        .order_by(
            '-submitted_at'
        )
    )

    byproducts = (
        ByProduct.objects
        .select_related(
            'raw_material'
        )
        .order_by(
            '-created_at'
        )
    )

    return render(
        request,
        'manage_operations.html',
        {
            'materials': materials,
            'byproducts': byproducts
        }
    )


# =============================================================
# DELETE MATERIAL
# =============================================================

@login_required
def delete_material(request, material_id):

    if request.user.role != 'admin':

        return redirect(
            'home'
        )

    if request.method == 'POST':

        try:

            material = RawMaterial.objects.get(
                id=material_id
            )

            material.delete()

        except RawMaterial.DoesNotExist:

            pass

    return redirect(
        'manage_operations'
    )


# =============================================================
# DELETE BY-PRODUCT
# =============================================================

@login_required
def delete_byproduct(request, byproduct_id):

    if request.user.role != 'admin':

        return redirect(
            'home'
        )

    if request.method == 'POST':

        try:

            byproduct = ByProduct.objects.get(
                id=byproduct_id
            )

            byproduct.delete()

        except ByProduct.DoesNotExist:

            pass

    return redirect(
        'manage_operations'
    )

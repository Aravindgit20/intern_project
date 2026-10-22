
from byproducts.models import ByProduct


# =============================================================
# POTENTIAL APPLICATIONS
# =============================================================

def get_potential_applications(byproduct_type):

    applications = {
        'Red Mud': [
            'Cement and concrete materials',
            'Bricks and construction materials',
            'Ceramic applications',
            'Metal recovery',
        ],

        'Aluminum Dross / Residue': [
            'Aluminum recovery',
            'Metal recovery',
            'Secondary material processing',
        ],

        'Manganese Alloy': [
            'Steel production',
            'Alloy production',
            'Metallurgical applications',
        ],
    }

    return applications.get(
        byproduct_type,
        ['Further treatment and resource recovery']
    )


# =============================================================
# GENERATE BY-PRODUCTS
# =============================================================

def generate_byproducts(material):

    byproducts_created = []

    material_type = material.material_type.lower()

    # ---------------------------------------------------------
    # BAUXITE: RED MUD
    # ---------------------------------------------------------

    if material_type == 'bauxite':

        red_mud_quantity = round(
            material.quantity * 0.30,
            2
        )

        red_mud = ByProduct.objects.create(
            raw_material=material,
            byproduct_type='Red Mud',
            quantity=red_mud_quantity,
            status='pending',
            potential_applications=get_potential_applications(
                'Red Mud'
            )
        )

        byproducts_created.append(red_mud)

    # ---------------------------------------------------------
    # SCRAP ALUMINUM: TWO STAGES
    # ---------------------------------------------------------

    elif material_type == 'scrap_aluminum':

        # Stage 1: Aluminum Dross / Residue
        dross_quantity = round(
            material.quantity * 0.15,
            2
        )

        dross = ByProduct.objects.create(
            raw_material=material,
            byproduct_type='Aluminum Dross / Residue',
            quantity=dross_quantity,
            status='pending',
            potential_applications=get_potential_applications(
                'Aluminum Dross / Residue'
            )
        )

        byproducts_created.append(dross)

        # Stage 2: Manganese Alloy recovered from Stage 1 residue
        manganese_quantity = round(
            dross_quantity * 0.10,
            2
        )

        manganese = ByProduct.objects.create(
            raw_material=material,
            byproduct_type='Manganese Alloy',
            quantity=manganese_quantity,
            status='pending',
            potential_applications=get_potential_applications(
                'Manganese Alloy'
            )
        )

        byproducts_created.append(manganese)

    return byproducts_created

def format_org_unit(org_unit_path):
    if not org_unit_path:
         return "N/A"

    return org_unit_path.split("/")[-1]
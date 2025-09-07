from ppqm import chembridge


def generate_orca_input(sdf_str: str) -> str:
    """
    Generate Orca input file from SDF string.
    """
    molobj = chembridge.sdfstr_to_molobj(sdf_str)

    if not molobj:
        return ""

    charge = chembridge.get_charge(molobj)
    atoms, coords, _ = chembridge.get_axyzc(molobj, atomfmt=str)

    # For now, we'll assume multiplicity 1. This could be improved later.
    multiplicity = 1

    header = "! PM3 Opt\n"
    header += f"* xyz {charge} {multiplicity}\n"

    coord_lines = []
    for atom, coord in zip(atoms, coords):
        coord_lines.append(f"  {atom}   {coord[0]:.6f}   {coord[1]:.6f}   {coord[2]:.6f}")

    coord_block = "\n".join(coord_lines)

    return header + coord_block + "\n*"

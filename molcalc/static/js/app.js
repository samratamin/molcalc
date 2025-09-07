async function smilesToSdf(smi)
{
    await window.rdkitLoadingPromise;
    var mol = window.RDKit.get_mol(smi);
    mol.add_hs();
    mol.get_new_coords(true);
    mol.remove_hs();
    var mol3d = mol.get_molblock();
    return mol3d;
}

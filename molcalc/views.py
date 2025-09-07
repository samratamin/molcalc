import datetime
import hashlib
import logging
import re

import numpy as np
from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
)
from rdkit import Chem
from rdkit.Chem import AllChem

from molcalc import constants, models, pipelines
from molcalc.extensions import db
from molcalc_lib import gamess_results
from ppqm import chembridge

_logger = logging.getLogger("molcalc:views")

main_bp = Blueprint("main", __name__)


@main_bp.app_errorhandler(404)
def not_found(error):
    return render_template("page_404.html"), 404


@main_bp.route("/")
def editor():
    """

    Standard view for MolCalc. Static HTML.

    """
    return render_template("page_editor.html")


@main_bp.route("/calculations/<hashkey>")
def view_calculation(hashkey):
    """

    View for looking up calculations.

    """

    # Look up the key
    calculation = (
        db.session.query(models.GamessCalculation)
        .filter_by(hashkey=hashkey)
        .first()
    )

    if calculation is None:
        abort(404)

    if hashkey == "404":
        abort(404)

    data = gamess_results.view_gamess_calculation(calculation)

    return render_template("page_calculation.html", **data)


@main_bp.route("/calculations")
def view_calculations():
    """

    Statistic about current calculations? Iono, maybe not.
    Kind of destroyed the IO / browser last time


    """
    abort(404)
    return {}


@main_bp.route("/about")
def about():
    """

    static about page

    """
    return render_template("page_about.html")


@main_bp.route("/help")
def page_help():
    """

    static help page

    """
    return render_template("page_help.html")


@main_bp.route("/ajax/sdf", methods=["POST"])
def ajax_sdf_to_smiles():
    """

    sdf to smiles convertion

    """

    if not request.form:
        return jsonify(
            {
                "error": "Error 55 - Missing key",
                "message": "Error. Missing information.",
            }
        )

    try:
        sdf = request.form["sdf"].encode("utf-8")
    except Exception:
        return jsonify(
            {
                "error": "Error 60 - get error",
                "message": "Error. Missing information.",
            }
        )

    # Get smiles
    smiles, status = chembridge.sdf_to_smiles(sdf)
    if smiles is None:

        status = status.split("]")
        status = status[-1]

        return jsonify({"error": "Error 69 - rdkit error", "message": status})

    msg = {"smiles": smiles}

    return jsonify(msg)


@main_bp.route("/ajax/smiles", methods=["POST"])
def ajax_smiles_to_sdf():
    """

    convert SMILES to SDF format

    """

    if not request.form:
        return jsonify(
            {
                "error": "Error 53 - Missing key",
                "message": "Error. Missing information.",
            }
        )

    try:
        smiles = request.form["smiles"].encode("utf-8")
    except Exception as e:
        return jsonify(
            {
                "error": "Error 58 - get error",
                "message": "Error. Missing information.",
                "exception": f"{e}",
            }
        )

    sdfstr = chembridge.smiles_to_sdfstr(smiles)
    msg = {"sdf": sdfstr}

    return jsonify(msg)


@main_bp.route("/ajax/submitquantum", methods=["POST"])
def ajax_submitquantum():
    """

    Setup quantum calculation

    """

    settings = current_app.config

    # Check if user is someone who is a know misuser
    user_ip = request.remote_addr
    if (
        constants.COLUMN_BLOCK_IP in settings
        and user_ip in settings[constants.COLUMN_BLOCK_IP]
    ):
        return jsonify(
            {
                "error": "Error 194 - blocked ip",
                "message": "IP address has been blocked for missue",
            }
        )

    if not request.form:
        return jsonify(
            {
                "error": "Error 128 - empty post",
                "message": "Error. Empty post.",
            }
        )

    if "sdf" not in request.form:
        return jsonify(
            {
                "error": "Error 132 - sdf key error",
                "message": "Error. Missing information.",
            }
        )

    # Get coordinates from request
    sdfstr = request.form["sdf"].encode("utf-8")

    # Is this 2D or 3D?
    add_hydrogens = request.form.get("add_hydrogens", "1")
    add_hydrogens = add_hydrogens == "1"

    # Get rdkit
    molobj = chembridge.sdfstr_to_molobj(sdfstr)

    if molobj is None:
        return jsonify({"error": "Error 141 - rdkit error", "message": "RDKit error"})

    try:
        molobj.GetConformer()
    except ValueError:
        # Error
        return jsonify(
            {
                "error": "Error 141 - rdkit error",
                "message": (
                    "Error. Server was unable to generate "
                    "conformations for this molecule"
                ),
            }
        )

    # If hydrogens not added, assume graph and optimize with forcefield
    atoms = chembridge.molobj_to_atoms(molobj)

    if 1 not in atoms and add_hydrogens:
        molobj = Chem.AddHs(molobj)
        AllChem.EmbedMultipleConfs(molobj, numConfs=1)
        chembridge.molobj_optimize(molobj)

    atoms = chembridge.molobj_to_atoms(molobj)

    # TODO Check lengths of atoms
    # TODO Define max in settings
    max_atoms = 10
    (heavy_atoms,) = np.where(atoms != 1)
    if len(heavy_atoms) > max_atoms:
        return jsonify(
            {
                "error": "Error 194 - max atoms error",
                "message": "Stop Casper. Max ten heavy atoms.",
            }
        )

    # Fix sdfstr
    sdfstr = sdfstr.decode("utf8")
    for _ in range(3):
        i = sdfstr.index("\n")
        sdfstr = sdfstr[i + 1 :]
    sdfstr = "\n" * 3 + sdfstr

    # hash on sdf (conformer)
    hshobj = hashlib.md5(sdfstr.encode())
    hashkey = hshobj.hexdigest()

    # Check if hash/calculation already exists in db
    calculation = (
        db.session.query(models.GamessCalculation)
        .filter_by(hashkey=hashkey)
        .first()
    )

    # If calculation already exists, return
    if calculation is not None:
        msg = {"hashkey": hashkey}
        calculation.created = datetime.datetime.now()
        db.session.commit()
        _logger.info(f"{hashkey} exists")
        return jsonify(msg)

    # The calculation is valid and does not exists, pass to pipeline
    _logger.info(f"{hashkey} create")

    molecule_info = {"sdfstr": sdfstr, "molobj": molobj, "hashkey": hashkey}

    try:
        msg, new_calculation = pipelines.calculation_pipeline(
            molecule_info, settings
        )

    except Exception:

        sdfstr = chembridge.molobj_to_sdfstr(molobj)
        _logger.error(f"{hashkey} PipelineError", exc_info=True)
        _logger.error(sdfstr)

        return jsonify(
            {
                "error": "293",
                "message": "Internal server server. Uncaught exception",
            }
        )

    # Add calculation to the database
    if new_calculation is not None:
        db.session.add(new_calculation)
        db.session.commit()

    return jsonify(msg)

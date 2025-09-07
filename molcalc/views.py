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

from molcalc import constants, models, orca, pipelines
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
    Generate an Orca input file and return it to the user.
    """
    if "sdf" not in request.form:
        return jsonify(
            {
                "error": "Error 132 - sdf key error",
                "message": "Error. Missing information.",
            }
        )

    sdf_str = request.form["sdf"]

    # Generate Orca input
    orca_input = orca.generate_orca_input(sdf_str)

    if not orca_input:
        return jsonify(
            {
                "error": "Error 200 - Orca input generation failed",
                "message": "Error. Could not generate Orca input.",
            }
        )

    return jsonify({"orca_input": orca_input})

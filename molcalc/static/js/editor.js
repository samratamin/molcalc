$(document).ready(function()
{

// global
const $loading = $('<div class="meter"><span style="width: 100%"></span></div>');

// Editor specific wrapper functions

function getEditorDimensions()
{
    var $content = $('.mc-content');
    var width = $content.innerWidth();
    var height = $content.innerHeight();
    return [width, height];
}

// View checking

function getView()
{
    rel = $('.toolset.tool-choice .button.active').attr("rel");
    return rel;
}

function setCurrentSDF(sdf)
{
    var view = getView();
    if (view == "2d")
    {
        mol = chemdoodleSetMol(sketcher, sdf);
    }
    else
    {
        jsmolSetMol(myJmol1, sdf);
        // jsmolCmd(myJmol1, "minimize addHydrogens"); // This command can cause JSmol to freeze on some molecules.
    }
    return false;
}

function getCurrentSDF(includeHydrogen=false)
{
    var view = getView();
    var mol;

    if (view == "2d")
    {
        mol = chemdoodleGetMol(sketcher);
    }
    else
    {
        mol = jsmolGetMol(myJmol1, includeHydogen=includeHydrogen);
    }

    return mol;
}


// Production ///////////////////////////////////////////////////



// Chemdoodle
$('.toolset.chemdoodle a.button.chemdoodle').click(function () {
    chemdoodleEditorBtn($(this));
    return false;
});

waitForElement("#sketcherSingle", function() {
    setTimeout(function() {
        chemdoodleResize(sketcher, getEditorDimensions()); // Resize
    }, 100);
});


// Jsmol
var $jsmolMinimizeBtn = $('.action.minimize .button');
$jsmolMinimizeBtn.click(function()
{
    jsmolCmd(myJmol1, 'minimize');
    return false;
});

var $jsmolMinimizeBtn = $('.action.undo .button');
$jsmolMinimizeBtn.click(function()
{
    jsmolCmd(myJmol1, 'undo');
    return false;
});

var $jsmolAtomBtns = $('.action.atom .button');
$jsmolAtomBtns.click(function ()
{

    var cmd = $(this).attr('rel');
    $('.toolset.jsmol .action.atom .button.active').removeClass("active");

    switch(cmd)
    {
        case 'off':
            jsmolCmd(myJmol1, 'set atomPicking off');
            break;
        case 'dra':

            jsmolCmd(myJmol1, 'set atomPicking on');
            jsmolCmd(myJmol1, 'set picking dragMinimize'); // on off
            $(this).addClass('active');
            break;
        default:
            jsmolCmd(myJmol1, 'set atomPicking on');
            jsmolCmd(myJmol1, 'set picking dragMinimize');
            jsmolCmd(myJmol1, 'set picking assignAtom_'+cmd);
            $(this).addClass('active');
    }

    return false;
});

$jsmolBondBtns = $('.toolset.jsmol .action.bond .button')
$jsmolBondBtns.click(function()
{
    var bond = $(this).attr('rel');
    $(".toolset.jsmol .action.bond .button.active").removeClass('active');

    if(bond == 'n')
    {
        jsmolCmd(myJmol1, 'set bondpicking false;');
    }
    else
    {
        jsmolCmd(myJmol1, 'set picking assignBond_'+bond+';');
        $(this).addClass('active');
    }

    return false;
});


// Resize editors on window resize
function onWindowResize()
{
    $(window).on('resize', function()
    {
        chemdoodleResize(sketcher, getEditorDimensions());
    });
}

// Refresh before play
onWindowResize();


// Switch between 3D and 2D
// $('#editor-jsmol').hide();
// $('.toolset.jsmol').hide();
$('#editor-chemdoodle').hide();
$('.toolset.chemdoodle').hide();

swithBtns = $('.toolset.tool-choice .button').click(function () {

    $that = $(this);

    if($that.hasClass("active"))
    {
        return false;
    }

    var cont = $that.attr("rel");

    if(cont == "3d")
    {
        var sdf = chemdoodleGetMol(sketcher);

        jsmolSetMol(myJmol1, sdf);
        jsmolCmd(myJmol1, "minimize addHydrogens");

        $('#editor-chemdoodle').hide();
        $('.toolset.chemdoodle').hide();
        $('#editor-jsmol').show();
        $('.toolset.jsmol').show();
    }
    else if (cont == "2d")
    {
        var sdf = jsmolGetMol(myJmol1);

        chemdoodleSetMol(sketcher, sdf);
        chemdoodleResize(sketcher, getEditorDimensions());

        $('#editor-jsmol').hide();
        $('.toolset.jsmol').hide();
        $('#editor-chemdoodle').show();
        $('.toolset.chemdoodle').show();
    }

    swithBtns.removeClass("active");
    $that.addClass("active");

    return false;

});

// Load molecules
$('.toolset .load_methane').click(function () {

    // Structure defined in html template
    setCurrentSDF(sdfMethane);
    return false;
});
$('.toolset .load_benzene').click(function () {

    setCurrentSDF(sdfBenzene);
    return false;
});
$('.toolset .load_water').click(function () {

    setCurrentSDF(sdfWaterdimer);
    return false;
});


// Move to quantum
$('.button.quantum').click(function () {

    var promptQuantum = new $.Prompt();
    promptQuantum.setMessage('Ready to calculate <strong>quantum chemical properties</strong> for the molecule?');
    promptQuantum.addResponseBtn('Indeed', function()
    {
        var $loading = $('<div class="meter"><span style="width: 100%"></span></div>');
        var promptCalculation = new $.Prompt();
        promptCalculation.setMessage($loading);
        promptCalculation.setType("transparent");
        promptCalculation.show();
        promptQuantum.cancel();

        var mol = getCurrentSDF(include_hydrogen=true);
        var currentView = getView();
        var addHydrogens = 1
        if (ciEquals(currentView, "3d")){
            addHydrogens = 0
        }

        var sdf_data = {sdf:mol, add_hydrogens:addHydrogens, current_view:currentView}

        request("/ajax/submitquantum", sdf_data, function (data)
        {
            promptCalculation.cancel();
            if (data.orca_input) {
                var blob = new Blob([data.orca_input], {type: "text/plain;charset=utf-8"});
                var link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = 'molcalc.inp';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                var promptError = new $.Prompt();
                promptError.setMessage(data.message || "An unknown error occurred.");
                promptError.addCancelBtn("OK");
                promptError.show();
            }
        }, function() {
            promptCalculation.cancel();
            var promptError = new $.Prompt();
            promptError.setMessage("The request to the server failed.");
            promptError.addCancelBtn("OK");
            promptError.show();
        }, timeout=60000);
    });
    promptQuantum.addCancelBtn("Not yet");
    promptQuantum.show();

    return false;
});


// Get name
$('.button.getName').click(async function () {

    // Setup loading
    var $loading = $('<div class="meter"><span style="width: 100%"></span></div>');
    var promptWait = new $.Prompt();
    promptWait.setMessage($loading);
    promptWait.setType("transparent");
    promptWait.show();

    try {
        // prepare smiles
        var mol = getCurrentSDF();
        var search = await sdfToSmiles(mol);

        requestCactus(search, 'iupac_name', function(data)
        {
            name = data;
            name = name.toLowerCase();

            var promptCactus = new $.Prompt();
            promptCactus.setMessage(name);
            promptCactus.addCancelBtn("Thanks");
            promptCactus.show();

            promptWait.cancel();

        }, function(status)
        {
            promptWait.cancel();
        });

    } catch (error) {
        console.error('Error converting molecule to SMILES:', error);
        promptWait.cancel();
    }

    // var promptWait = new $.Prompt();
    // promptWait.setMessage($loading);
    // promptWait.show();
    //
    // request("/ajax/sdf", {"sdf": mol}, function (data)
    // {
    //     promptWait.cancel();
    //     var promptCalculation = new $.Prompt();
    //
    //     if(data["error"]) {
    //
    //         promptCalculation.setMessage(data["message"]);
    //
    //     } else {
    //
    //         // contact cactus
    //         promptCalculation.setMessage($loading);
    //         promptCalculation.setType("transparent");
    //
    //         // prepare smiles
    //         search = data["smiles"];
    //
    //         requestCactus(search, 'iupac_name', function(data)
    //         {
    //
    //             name = data;
    //             name = name.toLowerCase();
    //
    //             var promptCactus = new $.Prompt();
    //             promptCactus.setMessage(name);
    //             promptCactus.addCancelBtn("Thanks");
    //             promptCactus.show();
    //
    //             promptCalculation.cancel();
    //
    //
    //         }, function(status)
    //         {
    //             promptCalculation.cancel();
    //         });
    //
    //     } // data
    //
    //     promptCalculation.show();
    //
    // }, function() {
    //     promptWait.cancel();
    // });

    return false;
});




// // Searchbar
var $searchFrm = $(".mc-editor-searchbar form");
var $searchBar = $(".mc-editor-searchbar");
var $searchBtn = $(".mc-editor-searchbar a");
var $searchInp = $(".mc-editor-searchbar input");
var $searchBarCloseBtn = $(".mc-editor-searchbar .searchbar-close");
var $searchBarBtn = $(".mc-mobile-search a");


function changeInputStatus(input, stats) {

    input.removeClass();
    // input.addClass(stats); // This line is commented out to avoid a bug in JSmol that overrides jQuery's addClass method.

    if(stats == "loading") {
        input.prop('disabled', true);
    }
    else{
        input.prop('disabled', false);
    }

}

$searchInp.on('blur', function() {

    $searchBar.removeClass("active");

});

$searchInp.on('focus', function() {

});

$searchBarBtn.click(function () {

    $searchBar.addClass("active");

    setTimeout(function() {
        $searchBar.find("input:first").focus();
        return false;
    }, 100);


    return false;

});

$searchBarCloseBtn.click(function() {
    $('.mc-header').focus();
    return false;
});

$searchFrm.submit(function(event) {

    event.preventDefault();

    changeInputStatus($searchInp, "loading");

    var promptWait = new $.Prompt();
    promptWait.setMessage($loading);
    promptWait.setType("transparent");
    promptWait.show();

    var search = $searchInp.val();

    if (!search || 0 === search.length)
    {
        changeInputStatus($searchInp, "empty");
        $searchInp.focus();
        return false;
    }

    requestCactus(search, 'smiles', async function(data)
    {
        try {
            // Wait for RDKit to be initialized
            await window.rdkitLoadingPromise;

            // Convert to sdf
            var sdfstr = await smilesToSdf(data);
            setCurrentSDF(sdfstr);

            promptWait.cancel();
            onWindowResize();

            // reset search on success
            $searchInp.focus();
            // $searchInp.val(""); // Casper didn't like this behavior
            changeInputStatus($searchInp, 'success');

        } catch (error) {
            console.error('Error during molecule conversion:', error);
            changeInputStatus($searchInp, 'failed');
            promptWait.cancel();
        }

    }, function(status)
    {
        changeInputStatus($searchInp, 'failed');
        promptWait.cancel();
    });

    return false;
});


// End
});


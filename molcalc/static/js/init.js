window.rdkitLoadingPromise = window.initRDKitModule({
    locateFile: () => '/static/rdkit/rdkit.wasm'
})
.then(function (RDKit) {
    console.log("RDKit version: " + RDKit.version());
    window.RDKit = RDKit;
    return RDKit;
})
.catch(() => {
    // handle loading errors here...
});

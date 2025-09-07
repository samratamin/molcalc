// Check if RDKit module loader is available
if (typeof window.initRDKitModule === 'function') {
    window.rdkitLoadingPromise = window.initRDKitModule({
        locateFile: () => '/static/rdkit/rdkit.wasm'
    })
    .then(function (RDKit) {
        console.log("RDKit version: " + RDKit.version());
        window.RDKit = RDKit;
        return RDKit;
    })
    .catch((error) => {
        console.error("Failed to load RDKit:", error);
        // Return a rejected promise to maintain the error state
        throw error;
    });
} else {
    console.error("RDKit module loader not found. Make sure rdkit.js is loaded.");
    window.rdkitLoadingPromise = Promise.reject(new Error("RDKit module loader not available"));
}

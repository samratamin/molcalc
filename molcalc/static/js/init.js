window.rdkitLoadingPromise = new Promise((resolve, reject) => {
  if (typeof window !== 'undefined' && window.initRDKitModule) {
    window.initRDKitModule()
      .then(RDKit => {
        window.RDKit = RDKit;
        console.log('RDKit initialized successfully');
        resolve(RDKit);
      })
      .catch(error => {
        console.error('Error initializing RDKit:', error);
        reject(error);
      });
  } else {
    const error = new Error('initRDKitModule is not defined on the window object.');
    console.error(error);
    reject(error);
  }
});

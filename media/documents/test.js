function attendre(ms) {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve("Fini !");
      }, ms);
    });
  }
  
  attendre(2000).then(message => console.log(message));
  
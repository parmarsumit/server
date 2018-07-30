var TributeController = artifacts.require("./TributeController.sol");

module.exports = function(deployer) {
  deployer.deploy(TributeController)
  .then(() => TributeController.deployed())
  .then(function(_instance){
    var fs = require('fs');
    var json_data = JSON.stringify({'address':_instance.address});
    /// add network id
    /// 
    fs.writeFile("build/contracts/deployed.json", json_data, function(err) {
        if (err) {
            console.log(err);
        }
    });
  }
  );
};

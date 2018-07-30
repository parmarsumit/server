
var network_by_id = {
  1: 'Mainnet',
  3: 'Ropsten',
  4: 'Rinkeby',
  42: 'Kovan',
}

function setupWeb3(){
    ///
    if (window.web3) {
      //https://guillaumeduveau.com/fr/blockchain/ethereum/metamask-web3
      // Then replace the old injected version by the latest build of Web3.js version 1.0.0
      window.web3old = window.web3;
      window.web3 = new Web3(window.web3.currentProvider);
    } else {
      var infura_url = 'https://ropsten.infura.io/izzDOxMZA5pJYbl8naUF';
      window.web3 = new Web3(new Web3.providers.HttpProvider(infura_url));
    }
    checkingNetwork();
}

function checkingNetwork(){
    // first of all
    // check that we are on the right network
    //
    var networkId;
    var tributeControllerNetwork = $('#app').data('network');

    window.web3.eth.net.getId().then(function(nid){
      networkId = nid;

      $('#eth_network').text(network_by_id[networkId]);

      if ( networkId && tributeControllerNetwork == networkId ){
        var defaultAccount = $('#content-main').data('account');
        var currentBalance = 0;
        web3.eth.getBalance(defaultAccount).then(function(balance){
          currentBalance = Number.parseFloat(web3.utils.fromWei(balance)).toPrecision(4);
          console.log('Balance:', currentBalance, balance);
          $('#eth_balance').text(currentBalance);
        });

      } else {

        //
        window.popReload('/web3.html', '#modalpanel');

        /// open warning message box about the initial setup for web3
        // how do we setup web3 provider ?
        window.popReload('/web3.html', '#modalpanel');
        //alert('You have to select network '+network_by_id[tributeControllerNetwork] );
      }
    });

}

module.exports = setupWeb3;

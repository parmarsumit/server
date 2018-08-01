
// the address that will send the test transaction
const addressFrom = '0x1889EF49cDBaad420EB4D6f04066CA4093088Bbd'
const privKey = 'PRIVATE_KEY'

// the destination address
const addressTo = '0x1463500476a3ADDa33ef1dF530063fE126203186'

// Signs the given transaction data and sends it. Abstracts some of the details
// of buffering and serializing the transaction for web3.
function sendSigned(txData, cb) {
  const privateKey = new Buffer(config.privKey, 'hex')
  const transaction = new Tx(txData)
  transaction.sign(privateKey)
  const serializedTx = transaction.serialize().toString('hex')
  web3.eth.sendSignedTransaction('0x' + serializedTx, cb)
}

// get the number of transactions sent so far so we can create a fresh nonce
web3.eth.getTransactionCount(defaultAccount).then(function(txCount){

  // construct the transaction data
  const txData = {
    nonce: web3.utils.toHex(txCount),
    gasLimit: web3.utils.toHex(25000),
    gasPrice: web3.utils.toHex(10e9), // 10 Gwei
    to: addressTo,
    from: addressFrom,
    value: web3.utils.toHex(web3.utils.toWei(123, 'wei'))
  }

  // fire away!
  sendSigned(txData, function(err, result) {
    if (err) return console.log('error', err)
    console.log('sent', result)
  })

})
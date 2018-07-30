#!/bin/bash
# https://medium.com/mercuryprotocol/how-to-create-your-own-private-ethereum-blockchain-dad6af82fc9f
# http://solidity.readthedocs.io/en/v0.4.20/introduction-to-smart-contracts.html
# https://web3py.readthedocs.io/en/stable/contracts.html
set -e
geth --datadir /srv/chain init /srv/Genesis.json
geth --datadir /srv/chain --networkid 1314 --mine --rpc
echo "OK"

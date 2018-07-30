pragma solidity ^0.4.24;

import './TributeToken.sol';

contract TributeController {
  using SafeMath for uint256;

  address[] public tokens;

  mapping(address => bool) public token;
  mapping(address => uint256) public fees;

  event CreatedToken(address token); // maybe listen for events

  constructor() public {
  }

  function createProject(string name, string symbol, uint256 supply) public returns(TributeToken new_token){
    new_token = new TributeToken(msg.sender, name, symbol, 2, supply);
    emit CreatedToken(new_token);
    token[new_token] = true;
    tokens.push(new_token);
  }

  modifier isToken() {
    require(token[msg.sender]);
    _;
  }

  function recordFees(uint256 amount) isToken public returns(uint256){
    fees[msg.sender].add(amount);
    return fees[msg.sender];
  }

}

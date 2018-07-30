pragma solidity ^0.4.24;

import 'openzeppelin-solidity/contracts/token/ERC20/BasicToken.sol';
import 'openzeppelin-solidity/contracts/token/ERC20/DetailedERC20.sol';
import "openzeppelin-solidity/contracts/math/SafeMath.sol";

import './TributeController.sol';

contract TributeToken is BasicToken {
  using SafeMath for uint256;

  address controller;

  string public name;
  string public symbol;
  uint8 public decimals;

  ///
  uint256 public totalRewards = 0;
  uint256 public totalRedeemed = 0;

  ///
  uint256 public feesNumerator = 5;
  uint256 public feesDenominator = 100;

  ///
  uint256 public totalFundedValue = 0;
  uint256 public totalRedeemedValue = 0;

  mapping(address => bool) public owners;
  mapping(address => bool) public funders;

  constructor(address initiator, string _name, string _symbol, uint8 _decimals, uint256 supply) public {
    name = _name;
    symbol = _symbol;
    decimals = _decimals;

    totalSupply_ = supply;

    balances[initiator] = 0;
    owners[initiator] = true;

    controller = msg.sender;
  }

  modifier isOwned() {
    require(owners[msg.sender]);
    _;
  }

  function issueTokens(uint256 amount) isOwned public returns(bool success){
    totalSupply_ = totalSupply_.add(amount);
    success = true;
  }

  function fundProject() isOwned public payable returns(bool success){
    totalFundedValue = totalFundedValue.add(msg.value);
    funders[msg.sender] = true;
    success = true;
  }

  function addOwner(address addrs) isOwned public returns(bool success){
    require(!owners[addrs]);
    require(addrs!=controller);
    owners[addrs] = true;
    success = true;
  }

  function revokeOwner(address addrs) isOwned public returns(bool success){
    require(!owners[addrs]);
    require(addrs!=controller);
    owners[addrs] = false;
    success = true;
  }

  /// reward someone
  function rewardContribution(address contributor, uint256 amount) isOwned public returns(bool success){
    require(contributor!=controller);
    require(contributor!=msg.sender);

    /// require the totalSupply_ >= totalRewards+amount+fees
    uint256 fees = (amount * feesNumerator) / feesDenominator;

    require(totalRewards.add(amount).add(fees) <= totalSupply_);

    balances[contributor] = balances[contributor].add(amount);
    balances[controller] = balances[controller].add(fees);

    totalRewards = totalRewards.add(fees);
    totalRewards = totalRewards.add(amount);

    TributeController coop = TributeController(controller);
    coop.recordFees(fees);

    success = true;
  }

  /// value in eth for amount of token
  function getEthValue(uint256 amount) public returns (uint256 tokenValue){
    uint256 remainingFund = totalFundedValue.sub(totalRedeemedValue);
    tokenValue = remainingFund / totalSupply_;
  }

  /// redeem hold token value
  function redeemRewarded(uint256 amount) public returns(bool success){
    require(amount > 0);
    require(balances[msg.sender] > 0);
    require(balances[msg.sender] >= amount);

    // calculate amount in eth
    uint256 redeemValue = getEthValue(amount);

    // burn tokens
    totalSupply_ = totalSupply_.sub(amount);
    totalRedeemedValue = totalRedeemed.add(redeemValue);

    // transfer eth to sender
    msg.sender.transfer(redeemValue);
  }


}

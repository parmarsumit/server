/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./src/index.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./src/actions/addOwner.js":
/*!*********************************!*\
  !*** ./src/actions/addOwner.js ***!
  \*********************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\r\n\r\n$('#app').on('app.switched', function(event){\r\n\r\n  if (event.action == 'signOwnership'){\r\n\r\n    $('#app form').off('submit');\r\n\r\n    $('#id_address').val( $('#target_actor').data('address') );\r\n\r\n    $('#signOwnership_form').submit( function(event){\r\n        event.preventDefault();\r\n\r\n        var ownerAddress = $('#id_address').val();\r\n        var options = {};\r\n        window.wrapTokenTransaction('#signOwnership_form', 'addOwner', [ownerAddress], options);\r\n        return false;\r\n    });\r\n  }\r\n\r\n});\r\n\n\n//# sourceURL=webpack:///./src/actions/addOwner.js?");

/***/ }),

/***/ "./src/actions/createEthereumAccount.js":
/*!**********************************************!*\
  !*** ./src/actions/createEthereumAccount.js ***!
  \**********************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\r\n$('#app').on('app.switched', function(event){\r\n\r\n  if (event.action == 'createEthereumAccount'){\r\n\r\n    $('#app form').off('submit');\r\n\r\n    console.log('Hello !')\r\n\r\n    $('#createEthereumAccount_form').submit( function(event){\r\n\r\n\r\n        var password = $('#account_password').val();\r\n        var confirm = $('#account_confirm').val();\r\n\r\n        if (password && password==confirm){\r\n\r\n          var createdAccountAddress = '';\r\n          var createdAccountKeystore = '';\r\n\r\n          var account = web3.eth.accounts.create();\r\n          createdAccountAddress = account.address.toString();\r\n\r\n          createdAccountKeystore = account.encrypt(password);\r\n\r\n          $('#id_address').val(createdAccountAddress);\r\n          $('#id_keystore').val( JSON.stringify(createdAccountKeystore) );\r\n\r\n          ///\r\n          var signatureData = {\r\n            akey: $('#content').data('actor')\r\n          }\r\n          var signature = account.sign(JSON.stringify(signatureData));\r\n          \r\n          $('#id_tx').val(JSON.stringify(signature));\r\n\r\n          console.log('Submitting ...');\r\n          window.submitAForm(event);\r\n          return false;\r\n\r\n        } else {\r\n\r\n          alert('Paswwords does not match');\r\n\r\n        }\r\n        return false;\r\n    });\r\n\r\n  }\r\n\r\n});\r\n\n\n//# sourceURL=webpack:///./src/actions/createEthereumAccount.js?");

/***/ }),

/***/ "./src/actions/createProject.js":
/*!**************************************!*\
  !*** ./src/actions/createProject.js ***!
  \**************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\r\n$('#app').on('app.switched', function(event){\r\n\r\n  if (event.action == 'createProject'){\r\n\r\n    $('#app form').off('submit');\r\n\r\n    $('#createProject_form').submit( function(event){\r\n        event.preventDefault();\r\n\r\n        var tokenName = $('#id_title').val();\r\n        var tokenSymbol = $('#id_symbol').val();\r\n        var tokenSupply = $('#id_amount').val().toString();\r\n\r\n        var options = {}\r\n        //if (ethAmount > 0){\r\n        //  options.value = window.web3.utils.toWei(ethAmount, \"ether\");\r\n        //}\r\n\r\n        var createdTokenCallback = function(receipt){\r\n          //\r\n          $('#id_address').val(receipt.events.CreatedToken.returnValues.token);\r\n          $('#id_tx').val(receipt.transactionHash);\r\n\r\n          console.log(receipt.events.CreatedToken.returnValues.token);\r\n          console.log(receipt.transactionHash);\r\n\r\n          // send the final\r\n          $('#app form').off('submit');\r\n          $('#createProject_form').submit(window.submitAForm);\r\n          $('#createProject_form').submit();\r\n        }\r\n\r\n        window.wrapControllerTransaction('#createProject_form',\r\n                                          'createProject',\r\n                                          [tokenName, tokenSymbol, tokenSupply],\r\n                                          options,\r\n                                          createdTokenCallback);\r\n\r\n        return false;\r\n    });\r\n  }\r\n});\r\n\r\n\r\n$('#app').on('app.switched', function(event){\r\n  // activate if action is createProject\r\n  if ( event.action == 'ZcreateProject'){\r\n\r\n    $('#app form').off('submit');\r\n    $('#createProject_form').submit( function(event){\r\n\r\n        event.preventDefault();\r\n\r\n        // we need to check if user can do web3\r\n\r\n\r\n        var notyf = new Noty({theme: 'relax',\r\n          type: 'success',\r\n          timeout: mtimeout,\r\n          layout: 'topRight',\r\n          text: 'Waiting for transaction ...',\r\n          callbacks: {\r\n            onTemplate: function() {\r\n                this.barDom.innerHTML = '<div class=\"noty_body\">' + this.options.text + '<div>';\r\n                // Important: .noty_body class is required for setText API method.\r\n            },\r\n            onShow: function() {\r\n                $('.noty_body a').click(loadNext);\r\n            },\r\n          }\r\n        }).show();\r\n\r\n        var tokenName = $('#id_title').val();\r\n        var tokenSymbol = $('#id_symbol').val();\r\n        var tokenSupply = $('#id_amount').val();\r\n\r\n        var userAccount = $('#content-main').data('account');\r\n\r\n        // move panel content to another box\r\n        // waiting for the transaction to execute\r\n\r\n        window.tributeControllerContract.methods.createProject(tokenName, tokenSymbol, tokenSupply)\r\n        .send()\r\n        .on('transactionHash', function(hash){\r\n            console.log(hash);\r\n            //$('#id_tx').val(hash);\r\n        })\r\n        .on('confirmation', function(confirmationNumber, receipt){\r\n            //console.log('confirmationNumber');\r\n            //console.log(confirmationNumber);\r\n        })\r\n        .on('receipt', function(receipt){\r\n\r\n          console.log('receipt')\r\n          console.log(receipt);\r\n\r\n          $('#id_address').val(receipt.events.CreatedToken.returnValues.token);\r\n          $('#id_tx').val(receipt.transactionHash);\r\n\r\n          console.log(receipt.events.CreatedToken.returnValues.token);\r\n          console.log(receipt.transactionHash);\r\n\r\n          // send the final\r\n          $('#app form').off('submit');\r\n          $('#createProject_form').submit(window.submitAForm);\r\n          $('#createProject_form').submit();\r\n\r\n        })\r\n        .on('error', console.error);\r\n\r\n        return false;\r\n      });\r\n    }\r\n\r\n});\r\n\n\n//# sourceURL=webpack:///./src/actions/createProject.js?");

/***/ }),

/***/ "./src/actions/deployContract.js":
/*!***************************************!*\
  !*** ./src/actions/deployContract.js ***!
  \***************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\r\n$('#app').on('app.switched', function(event){\r\nif (event.action == 'deployContract'){\r\n\r\n  $('#app form').off('submit');\r\n\r\n  console.log('Unbound ...');\r\n\r\n  $('#deployContract_form').submit( function(event){\r\n\r\n      event.preventDefault();\r\n\r\n      var contractCompiled = JSON.parse( $('#id_contract').val() );\r\n      var contractCode = contractCompiled.bytecode;\r\n      var abi = contractCompiled.abi;\r\n\r\n      window.tributeControllerContract.deploy({\r\n        data: contractCode,\r\n        arguments: []\r\n      })\r\n      .send()\r\n      .on('transactionHash', function(hash){\r\n          console.log(hash);\r\n          //$('#id_tx').val(hash);\r\n      })\r\n      .on('confirmation', function(confirmationNumber, receipt){\r\n          //console.log('confirmationNumber');\r\n          //console.log(confirmationNumber);\r\n      })\r\n      .on('receipt', function(receipt){\r\n\r\n        console.log('receipt')\r\n        console.log(receipt);\r\n        $('#id_address').val(receipt.contractAddress);\r\n        $('#id_tx').val(receipt.transactionHash);\r\n        $('#id_network').val($('#app').data('network'));\r\n        // send the final\r\n        $('#app form').off('submit');\r\n        $('#deployContract_form').submit(window.submitAForm);\r\n        $('#deployContract_form').submit();\r\n      })\r\n      .on('error', console.error);\r\n\r\n      return false;\r\n  });\r\n\r\n\r\n}\r\n});\r\n\n\n//# sourceURL=webpack:///./src/actions/deployContract.js?");

/***/ }),

/***/ "./src/actions/fundProject.js":
/*!************************************!*\
  !*** ./src/actions/fundProject.js ***!
  \************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("\r\n$('#app').on('app.switched', function(event){\r\n\r\n  if (event.action == 'fundProject'){\r\n\r\n\r\n    $('#app form').off('submit');\r\n    $('#fundProject_form').submit( function(event){\r\n        event.preventDefault();\r\n\r\n        var ethAmount = $('#id_amount').val();\r\n        var options = {}\r\n        if (ethAmount > 0){\r\n          options.value = window.web3.utils.toWei(ethAmount, \"ether\");\r\n        }\r\n        window.wrapTokenTransaction('#fundProject_form', 'fundProject', [], options);\r\n        return false;\r\n    });\r\n    __webpack_require__(/*! ../components/web3.js */ \"./src/components/web3.js\")();\r\n\r\n  }\r\n\r\n});\r\n\n\n//# sourceURL=webpack:///./src/actions/fundProject.js?");

/***/ }),

/***/ "./src/actions/index.js":
/*!******************************!*\
  !*** ./src/actions/index.js ***!
  \******************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\r\n\r\n$('#app').on('app.switched', function(event){\r\n\r\n  if (event.action == 'index' || event.action == 'view'){\r\n\r\n    if ($('#welcome_updateProfile').length ){\r\n      // provide the update profile form\r\n      var actor = $('#content-main').data('actor');\r\n      var profileUpdateUrl = '/'+actor+'/updateProfile/';\r\n      console.log(profileUpdateUrl);\r\n      var data = {\r\n        redirect:window.location.href,\r\n        embed:true,\r\n      }\r\n      // send it\r\n      $.ajax({\r\n          url: profileUpdateUrl,\r\n          data:data,\r\n          method: 'GET',\r\n          type: 'GET', // For jQuery < 1.9\r\n          statusCode: {\r\n            402: function(response){\r\n              alert('Error creating profile');\r\n            },\r\n            403: function(response){\r\n              alert('Error creating profile');\r\n            },\r\n            401: function(response){\r\n              alert('Error creating profile');\r\n            },\r\n            404: function(response){\r\n              alert('Error creating profile');\r\n              //parseCreated(response.responseText);\r\n            },\r\n            415: function(response){\r\n              console.log(response);\r\n            },\r\n          },\r\n          success: function(data){\r\n              window.parseResponse(profileUpdateUrl, '#updateProfile_form', data);\r\n          },\r\n\r\n        beforeSend:function(){\r\n        }\r\n      });\r\n\r\n    }\r\n\r\n  }\r\n});\r\n\n\n//# sourceURL=webpack:///./src/actions/index.js?");

/***/ }),

/***/ "./src/actions/inviteOwner.js":
/*!************************************!*\
  !*** ./src/actions/inviteOwner.js ***!
  \************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\r\n$('#app').on('app.switched', function(event){\r\n\r\n  if (event.action == 'inviteOwner' || event.action == 'inviteVisitor'){\r\n    //\r\n    var ref_form = event.action+'_form';\r\n\r\n    if ( $('#id_target').val() )\r\n    {\r\n      var email = $('#id_target').val();\r\n      if ( validateEmail(email) && $('#id_target_field').hasClass('error') ){\r\n          //$('#inviteOwner_form').css({height:'0px'});\r\n          $('#'+ref_form).find('fieldset').attr('disabled', true);\r\n          createProfile(ref_form);\r\n      }\r\n    }\r\n  }\r\n});\r\n\r\nfunction validateEmail(email) {\r\n    var re = /^(([^<>()\\[\\]\\\\.,;:\\s@\"]+(\\.[^<>()\\[\\]\\\\.,;:\\s@\"]+)*)|(\".+\"))@((\\[[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\])|(([a-zA-Z\\-0-9]+\\.)+[a-zA-Z]{2,}))$/;\r\n    return re.test(String(email).toLowerCase());\r\n}\r\n\r\nfunction createProfile(ref_form){\r\n\r\n  // get form parameters\r\n  var email_key = document.getElementById(ref_form).elements['target'].value;\r\n  var data = {};\r\n  data.email = email_key;\r\n\r\n  var name = email_key.substring(0, email_key.lastIndexOf(\"@\"));\r\n  data.title = name;\r\n\r\n  data.csrfmiddlewaretoken = document.getElementById(ref_form).elements['csrfmiddlewaretoken'].value;\r\n\r\n  console.log(data);\r\n\r\n  //\r\n  var action_url = '/'+$('#content-main').data('actor')+'/createProfile/';\r\n\r\n  // send it\r\n  $.ajax({\r\n      url: action_url,\r\n      data: data,\r\n      method: 'POST',\r\n      type: 'POST', // For jQuery < 1.9\r\n      statusCode: {\r\n        402: function(response){\r\n          alert('Error creating profile');\r\n        },\r\n        403: function(response){\r\n          alert('Error creating profile');\r\n        },\r\n        401: function(response){\r\n          alert('Error creating profile');\r\n        },\r\n        404: function(response){\r\n          alert('Error creating profile');\r\n          //parseCreated(response.responseText);\r\n        },\r\n        415: function(response){\r\n          console.log(response);\r\n        },\r\n      },\r\n      success: function(data){\r\n          $('#'+ref_form).find('fieldset').attr('disabled', false);\r\n          $('#'+ref_form).submit();\r\n      },\r\n\r\n    beforeSend:function(){\r\n      //$('#'+from_form).find('fieldset').attr('disabled', true);\r\n    }\r\n  });\r\n}\r\n\n\n//# sourceURL=webpack:///./src/actions/inviteOwner.js?");

/***/ }),

/***/ "./src/actions/issueNewTokens.js":
/*!***************************************!*\
  !*** ./src/actions/issueNewTokens.js ***!
  \***************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("\r\n$('#app').on('app.switched', function(event){\r\n\r\n  if (event.action == 'issueNewTokens'){\r\n\r\n    $('#app form').off('submit');\r\n    $('#issueNewTokens_form').submit( function(event){\r\n        event.preventDefault();\r\n\r\n        var tokenAmount = $('#id_amount').val();\r\n        var options = {}\r\n        window.wrapTokenTransaction('#issueNewTokens_form', 'issueTokens', [tokenAmount], options);\r\n        return false;\r\n    });\r\n    __webpack_require__(/*! ../components/web3.js */ \"./src/components/web3.js\")();\r\n  }\r\n\r\n});\r\n\n\n//# sourceURL=webpack:///./src/actions/issueNewTokens.js?");

/***/ }),

/***/ "./src/actions/redeemToken.js":
/*!************************************!*\
  !*** ./src/actions/redeemToken.js ***!
  \************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\n\n//# sourceURL=webpack:///./src/actions/redeemToken.js?");

/***/ }),

/***/ "./src/actions/revokeOwner.js":
/*!************************************!*\
  !*** ./src/actions/revokeOwner.js ***!
  \************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\n\n//# sourceURL=webpack:///./src/actions/revokeOwner.js?");

/***/ }),

/***/ "./src/actions/rewardContributor.js":
/*!******************************************!*\
  !*** ./src/actions/rewardContributor.js ***!
  \******************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\r\n\r\n$('#app').on('app.switched', function(event){\r\n  if (event.action == 'signReward'){\r\n    //\r\n    \r\n  }\r\n});\r\n\r\n\r\n$('#app').on('app.switched', function(event){\r\n\r\n  if (event.action == 'index'){\r\n\r\n    // check if there is a approve button\r\n    // we will load form in the background\r\n    // and trigger web3 transaction\r\n\r\n  } else if (event.action == 'Zapprove'){\r\n    $('#app form').off('submit');\r\n\r\n    $('#approve_form').submit( function(event){\r\n\r\n        event.preventDefault();\r\n\r\n        var userAccount = $('#content-main').data('account');\r\n        var tokenAddress = $('#content-main').data('address');\r\n\r\n        var cAddress = $('#contributor').data('address');\r\n        var cValue = $('#contribution').data('value');\r\n\r\n        $.getJSON(\"/static/contracts/TributeToken.json?\"+Math.random(), function(json) {\r\n\r\n          var tributeTokenInterface = json;\r\n\r\n          var code = tributeTokenInterface.bytecode;\r\n          var abi = tributeTokenInterface.abi;\r\n\r\n          tributeTokenContract = new window.web3.eth.Contract(abi, tokenAddress);\r\n          tributeTokenContract.options.from = userAccount;\r\n\r\n          tributeTokenContract.methods.rewardContributor(cAddress, cValue)\r\n          .send({value:window.web3.utils.toWei(ethAmount, \"ether\")})\r\n          .on('transactionHash', function(hash){\r\n              console.log(hash);\r\n              //$('#id_tx').val(hash);\r\n          })\r\n          .on('confirmation', function(confirmationNumber, receipt){\r\n              //console.log('confirmationNumber');\r\n              //console.log(confirmationNumber);\r\n          })\r\n          .on('receipt', function(receipt){\r\n\r\n            $('#id_tx').val(receipt.transactionHash);\r\n\r\n            // send the final\r\n            $('#app form').off('submit');\r\n            $('#fundProject_form').submit(window.submitAForm);\r\n            $('#fundProject_form').submit();\r\n          })\r\n          .on('error', console.error);\r\n        });\r\n        return false;\r\n      });\r\n    }\r\n\r\n});\r\n\n\n//# sourceURL=webpack:///./src/actions/rewardContributor.js?");

/***/ }),

/***/ "./src/actions/validateEthereumAddress.js":
/*!************************************************!*\
  !*** ./src/actions/validateEthereumAddress.js ***!
  \************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\r\n$('#app').on('app.switched', function(event){\r\n\r\n  if (event.action == 'validateEthereumAddress'){\r\n    //\r\n    var userAccount = $('#content-main').data('account');\r\n\r\n    $('#app form').off('submit');\r\n\r\n    /// check if user is connected to a provider\r\n    if (userAccount){\r\n      console.log('Actual account ', userAccount);\r\n    } else {\r\n      // call metamask\r\n      window.web3.eth.getAccounts().then(function(accounts){\r\n        defaultAccount = accounts[0];\r\n        $('#id_address').val(defaultAccount);\r\n      });\r\n    }\r\n\r\n    /**\r\n    $('#validateEthereumAddress_form').submit( function(event){\r\n        /// ask for signature before the user can register it's address\r\n        var address = $('#id_address').val();\r\n        var message = 'By signing this message, i prove that i\\'m the owner of the account and associate it with my Tribute id '+$('#content-main').data('actor');\r\n        var signature = web3.eth.sign(message, address, function(signHash){\r\n          // okay we got the signature\r\n          console.log(signHash);\r\n          $('#id_tx').val(signHash);\r\n        });\r\n        return false;\r\n    });\r\n    **/\r\n\r\n  }\r\n\r\n});\r\n\n\n//# sourceURL=webpack:///./src/actions/validateEthereumAddress.js?");

/***/ }),

/***/ "./src/actions/view.js":
/*!*****************************!*\
  !*** ./src/actions/view.js ***!
  \*****************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\r\n\r\n\r\n$('#app').on('app.switched', function(event){\r\n\r\n  if (event.action == 'view'){\r\n    //\r\n    //\r\n    $.getJSON(\"/static/contracts/TributeToken.json?\"+Math.random(), function(json) {\r\n\r\n      var userAccount = $('#content-main').data('account');\r\n      var tributeTokenAddress = $('#content-main').data('address');\r\n\r\n      var tributeTokenContract = new window.web3.eth.Contract(json.abi, tributeTokenAddress);\r\n      tributeTokenContract.options.from = userAccount;\r\n      tributeTokenContract.methods.totalSupply()\r\n      .call()\r\n      .then(function(result){\r\n          console.log(result)\r\n      });\r\n\r\n    });\r\n  }\r\n});\r\n\n\n//# sourceURL=webpack:///./src/actions/view.js?");

/***/ }),

/***/ "./src/components/app.js":
/*!*******************************!*\
  !*** ./src/components/app.js ***!
  \*******************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\r\nvar loadNext;\r\n\r\nfunction addParameterToURL(url, param){\r\n    //_url = location.href;\r\n    _url = url;\r\n    _url += (_url.split('?')[1] ? '&':'?') + param;\r\n    return _url;\r\n}\r\n\r\nfunction loadNext(e){\r\n\r\n  var url = $(e.currentTarget).attr('href');\r\n  var target = \"#content\";\r\n  if (!url || url == ''){\r\n    return true;\r\n  } else if (url.split('#').length > 1 ){\r\n    return true;\r\n  } else if ( $(e.currentTarget).attr('target') ){\r\n    return true;\r\n  }\r\n  else if ( $(e.currentTarget).hasClass('subpanel') ) {\r\n    target = '#sidepanel';\r\n  }\r\n  else if ( $(e.currentTarget).hasClass('modalpanel') ) {\r\n    target = '#modalpanel';\r\n  }\r\n  else if ( $(e.currentTarget).hasClass('btn-primary') ) {\r\n  //  target = '#modalpanel';\r\n  }\r\n  if ( $(e.currentTarget).data('action') && $(e.currentTarget).data('uid') ){\r\n    var action = $(e.currentTarget).data('action');\r\n    var uid = $(e.currentTarget).data('uid');\r\n\r\n    var payload = {context:window.context, action:action, path:$(e.currentTarget).attr('href'), 'ext':'.html'}\r\n    console.log('Sending ', payload);\r\n\r\n    var app_event = new CustomEvent('ws-send', {'detail':payload});\r\n    document.body.dispatchEvent(app_event);\r\n  } else {\r\n    loadUrl(url, target);\r\n  }\r\n  return false;\r\n}\r\n\r\nwindow.popReload = function(url, target){\r\n  //window.location.replace(url);\r\n  //return;\r\n  if (url){\r\n    if (!target){\r\n      loadUrl(url, \"#content\");\r\n    } else {\r\n      loadUrl(url, target);\r\n    }\r\n  } else {\r\n    loadUrl(window.location.href, \"#content\");\r\n  }\r\n\r\n\r\n};\r\n\r\nfunction extractHostname(url) {\r\n    var hostname;\r\n    //find & remove protocol (http, ftp, etc.) and get hostname\r\n\r\n    if (url.indexOf(\"://\") > -1) {\r\n        hostname = url.split('/')[2];\r\n    }\r\n    else {\r\n        hostname = url.split('/')[0];\r\n    }\r\n\r\n    //find & remove port number\r\n    hostname = hostname.split(':')[0];\r\n    //find & remove \"?\"\r\n    hostname = hostname.split('?')[0];\r\n\r\n    return hostname;\r\n}\r\n\r\n\r\nfunction loadUrl(url, target){\r\n\r\n  // check if url is on same domain\r\n  var urlDomain =  extractHostname(url);\r\n  if (urlDomain && document.domain != urlDomain){\r\n    window.open(url, urlDomain);\r\n    return false;\r\n  }\r\n\r\n  //$('.modal').modal('hide');\r\n  $('.popover').remove();\r\n  //$('.modal').modal('hide');\r\n  $('.tooltip').remove();\r\n\r\n  $.ajax({\r\n      url: url,\r\n      method: 'GET',\r\n      type: 'GET', // For jQuery < 1.9\r\n      statusCode: {\r\n        402: function(response){\r\n          parseResponse(url, target, response.responseText);\r\n        },\r\n        403: function(response){\r\n          parseResponse(url, target, response.responseText);\r\n        },\r\n        401: function(response){\r\n          parseResponse(url, target, response.responseText);\r\n        },\r\n        404: function(response){\r\n          parseResponse(url, target, response.responseText);\r\n        },\r\n        500: function(response){\r\n          parseResponse(url, target, response.responseText);\r\n        },\r\n      },\r\n      success: function(data){\r\n          parseResponse(url, target, data);\r\n      }\r\n  });\r\n\r\n};\r\n\r\nfunction parseResponse(url, target, data){\r\n\r\n  var content = $(data).find('#content-main');\r\n  var redirect = content.data('redirect');\r\n\r\n  var action = content.data('action');\r\n  var uid = content.data('uid');\r\n\r\n  if (redirect){\r\n    window.popReload(redirect, '#content');\r\n    console.log('Redirecting ...', redirect);\r\n    console.log(content.data('close'));\r\n\r\n  //  $(target).modal('hide');\r\n  //  return;\r\n  }\r\n  //console.log('Closing ?',);\r\n  //console.log(content.data('close'))\r\n\r\n  if (content.data('close')){\r\n      console.log('Closing ...',);\r\n      $(target).modal('hide');\r\n      if (!redirect){\r\n        window.popReload(window.location.href);\r\n      }\r\n  }\r\n\r\n  //\r\n  var signatureRequired = content.data('require-signature');\r\n  var transactionRequired = content.data('require-transaction');\r\n\r\n  var defaultAccount = content.data('account');\r\n  if ( !defaultAccount && ( signatureRequired=='True' || transactionRequired=='True' )){\r\n      window.popReload('/web3.html', '#sidepanel');\r\n  } else {\r\n\r\n    //\r\n    $(target).html( $(data).find('#content').html() );\r\n\r\n    $(target+' a').click(loadNext);\r\n\r\n    if (target == '#content'){\r\n      history.pushState( {}, $(data).has('title').text(), url);\r\n      $('#sidepanel').modal('hide');\r\n    } else {\r\n      document.title = $(data).find('title').text();\r\n    }\r\n\r\n    stwitch(target, action, uid);\r\n\r\n    if (target == '#modalpanel'){\r\n      $(target).modal('show');\r\n    } else if (target == '#sidepanel') {\r\n      $(target).modal('show');\r\n    } else {\r\n      //$('.modal-backdrop').remove();\r\n    }\r\n    if (target == '#content'){\r\n    //  app.init();\r\n    }\r\n  }\r\n\r\n}\r\n\r\nwindow.parseResponse = parseResponse;\r\n\r\n$('body a').click(loadNext);\r\n\r\nfunction bind_dates(){\r\n\r\n  $('time.moment-from-now').each( function( index ){\r\n    try {\r\n        var datetime = moment( $(this).attr('datetime') );\r\n        $(this).text( datetime.fromNow(false) );\r\n    } catch( err ) {\r\n        console.log(err);\r\n    }\r\n  });\r\n\r\n}\r\n\r\nfunction stwitch(target, action, uid) {\r\n    bind_dates();\r\n    $('.message .close')\r\n      .on('click', function() {\r\n        $(this)\r\n          .closest('.message')\r\n          .transition('fade')\r\n        ;\r\n      });\r\n\r\n    // handle form submits to panel\r\n    $('#app form').bind('keypress', function(e) {\r\n       if( e.which === 13 )\r\n           return false;\r\n    });\r\n    $('#app form').submit(submitAForm);\r\n\r\n    console.log(uid+'/'+action);\r\n    $('#app').trigger({type:'app.switched',\r\n                       action:action,\r\n                       uid:uid});\r\n}\r\n\r\nfunction submitAForm(event){\r\n\r\n  event.preventDefault();\r\n\r\n  // get form parameters\r\n  var data = new FormData( $(event.currentTarget).closest(\"form\")[0] );\r\n\r\n  //\r\n  var target = '#'+$(event.currentTarget).closest('.pane').attr('id');\r\n  var action_url = $(event.currentTarget).attr('action');\r\n\r\n  // send it\r\n  $.ajax({\r\n      url: action_url,\r\n      data: data,\r\n      cache: false,\r\n      contentType: false,\r\n      processData: false,\r\n      method: 'POST',\r\n      type: 'POST', // For jQuery < 1.9\r\n      statusCode: {\r\n        402: function(response){\r\n          parseResponse(action_url, target, response.responseText);\r\n        },\r\n        403: function(response){\r\n          parseResponse(action_url, target, response.responseText);\r\n        },\r\n        401: function(response){\r\n          parseResponse(action_url, target, response.responseText);\r\n        },\r\n        404: function(response){\r\n          parseResponse(action_url, target, response.responseText);\r\n        },\r\n      },\r\n      success: function(data){\r\n          parseResponse(action_url, target, data);\r\n      },\r\n    beforeSend:function(){\r\n      $(event.currentTarget).find('fieldset').attr('disabled', true);\r\n    }\r\n  });\r\n  // disable form interactions\r\n  // prevent panel close\r\n  return false;\r\n}\r\n\r\nwindow.submitAForm = submitAForm;\r\n// finally init\r\n$(document).ready(function(){\r\n\r\n  Noty.setMaxVisible(10);\r\n  //Noty.setTheme('relax');\r\n  //Noty.setTimeout(4500);\r\n  var content = $('#content-main');\r\n  var redirect = content.data('redirect');\r\n  if (redirect){\r\n    window.popReload(redirect, '#content');\r\n    return;\r\n  }\r\n\r\n  window.onpopstate = function(event) {\r\n    //alert(\"location: \" + document.location + \", state: \" + JSON.stringify(event.state));\r\n    window.popReload(document.location);\r\n  };\r\n\r\n  (function(){\r\n   var serviceLocation = \"wss://\"+document.location.hostname+\":\"+document.location.port+\"/io.ws\";\r\n   var start = function(serviceLocation){\r\n     var ws = new WebSocket(serviceLocation);\r\n     var wsInterface = document.location.hash.slice(1);\r\n     ws.onopen = function() {\r\n        console.log('Connected ...');\r\n        //notie.alert({ text: 'Connected !' });\r\n        var notyf = new Noty({theme: 'relax',\r\n                  type: 'success',\r\n                  timeout: '5000',\r\n                  layout: 'bottomLeft',\r\n                  text: 'Okay, we are online'});\r\n        //\r\n        notyf.show();\r\n\r\n        // ask the user to sign in\r\n        if (window.web3) {\r\n          //https://guillaumeduveau.com/fr/blockchain/ethereum/metamask-web3\r\n          // Then replace the old injected version by the latest build of Web3.js version 1.0.0\r\n          window.web3old = window.web3;\r\n          window.web3 = new Web3(window.web3.currentProvider);\r\n          console.log('Got web3 ...');\r\n        } else {\r\n          var infura_url = 'https://ropsten.infura.io/v3/85b874cf0fe74f98a1006219a5e03985';\r\n          //var infura_url = 'http://localhost:7545';\r\n          window.web3 = new Web3(new Web3.providers.HttpProvider(infura_url));\r\n          console.log('Default infura web3 ...');\r\n        }\r\n\r\n        // listen for message handshake ?\r\n        var web3 = new Web3();\r\n        var account = web3.eth.accounts.create();\r\n\r\n        // listen for calls\r\n        document.body.addEventListener('ws-send', function(event){\r\n          // sign and send\r\n          console.log(event);\r\n          var eventData = event.detail;\r\n          eventData.interface = wsInterface;\r\n          var request = JSON.stringify(event.detail);\r\n          var signature = account.sign(request);\r\n          //console.log(signature);\r\n          ws.send(JSON.stringify(signature));\r\n        });\r\n\r\n     };\r\n     ws.onmessage = function (evt) {\r\n        //console.log(evt.data);\r\n        var msg = JSON.parse(evt.data);\r\n        //var app_event = new CustomEvent(msg['action'], {'detail':msg});\r\n        //document.body.dispatchEvent(app_event);\r\n        var mtype = 'success';\r\n        var mtimeout = 15000;\r\n        if (msg.todo){\r\n          mtype = 'warning';\r\n          mtimeout = 0;\r\n        }\r\n        var notyf = new Noty({theme: 'relax',\r\n                  type: mtype,\r\n                  timeout: mtimeout,\r\n                  layout: 'bottomLeft',\r\n                  text: msg.text,\r\n                  callbacks: {\r\n                    onTemplate: function() {\r\n                        this.barDom.innerHTML = '<div class=\"noty_body\">' + this.options.text + '<div>';\r\n                        // Important: .noty_body class is required for setText API method.\r\n                    },\r\n                    onShow: function() {\r\n                        $('.noty_body a').click(loadNext);\r\n                    },\r\n                  }\r\n                  }).show();\r\n\r\n        if (msg.path){\r\n          //history.pushState( {}, msg.text, msg.path);\r\n        }\r\n        if (msg.ext == '.html'){\r\n          parseResponse(msg.path, '#content', msg.data);\r\n        }\r\n        window.context = msg.context;\r\n\r\n        //console.log(msg.text);\r\n\r\n        // ws.send( JSON.stringify({action:'index', path:msg.context, 'ext':'/' }) );\r\n     };\r\n     ws.onclose = function(){\r\n       console.log('Connection lost ...');\r\n\r\n       var notyf = new Noty({theme: 'relax',\r\n                 type: 'error',\r\n                 timeout: '5000',\r\n                 layout: 'bottomLeft',\r\n                 text: 'Ooops .. looks like something went wrong'});\r\n       notyf.show();\r\n\r\n       //notie.alert({ text: 'Connection lost ...' });\r\n       window.ws = null;\r\n       setTimeout(function(){start(serviceLocation)}, 5000);\r\n     }\r\n   };\r\n\r\n   var content = $('#content-main');\r\n   var redirect = content.data('redirect');\r\n   var action = content.data('action');\r\n   var uid = content.data('uid');\r\n\r\n   stwitch('#content', action, uid);\r\n   start(serviceLocation);\r\n  })();\r\n\r\n  $('#sidepanel').on('hide.bs.modal', function(){\r\n     //window.popReload();\r\n  });\r\n\r\n});\r\n\n\n//# sourceURL=webpack:///./src/components/app.js?");

/***/ }),

/***/ "./src/components/profile.js":
/*!***********************************!*\
  !*** ./src/components/profile.js ***!
  \***********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("\r\n__webpack_require__(/*! ../actions/createEthereumAccount.js */ \"./src/actions/createEthereumAccount.js\");\r\n\r\n__webpack_require__(/*! ../components/web3.js */ \"./src/components/web3.js\")();\r\n\n\n//# sourceURL=webpack:///./src/components/profile.js?");

/***/ }),

/***/ "./src/components/project.js":
/*!***********************************!*\
  !*** ./src/components/project.js ***!
  \***********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("\r\n__webpack_require__(/*! ../actions/index.js */ \"./src/actions/index.js\");\r\n__webpack_require__(/*! ../actions/view.js */ \"./src/actions/view.js\");\r\n__webpack_require__(/*! ../actions/inviteOwner.js */ \"./src/actions/inviteOwner.js\");\r\n\r\n__webpack_require__(/*! ../actions/createProject.js */ \"./src/actions/createProject.js\");\r\n__webpack_require__(/*! ../actions/fundProject.js */ \"./src/actions/fundProject.js\");\r\n__webpack_require__(/*! ../actions/issueNewTokens.js */ \"./src/actions/issueNewTokens.js\");\r\n__webpack_require__(/*! ../actions/addOwner.js */ \"./src/actions/addOwner.js\");\r\n__webpack_require__(/*! ../actions/revokeOwner.js */ \"./src/actions/revokeOwner.js\");\r\n\r\n__webpack_require__(/*! ../actions/rewardContributor.js */ \"./src/actions/rewardContributor.js\");\r\n__webpack_require__(/*! ../actions/redeemToken.js */ \"./src/actions/redeemToken.js\");\r\n\r\n__webpack_require__(/*! ../actions/deployContract.js */ \"./src/actions/deployContract.js\");\r\n\r\n__webpack_require__(/*! ../actions/validateEthereumAddress.js */ \"./src/actions/validateEthereumAddress.js\");\r\n\r\nfunction unlockAccount(callback){\r\n  var keystore = $('#content-main').data('keystore');\r\n  if (keystore){\r\n    $('#extrapanel').modal('show');\r\n    $('#password_modal').bind('keypress', function(e) {\r\n       if( e.which === 13 )\r\n           var password = $('#account_password').val();\r\n           if (password){\r\n             /// unlocking account keystore with passwd\r\n             var account = web3.eth.accounts.decrypt(keystore, password);\r\n             var wallet = web3.eth.accounts.wallet.create();\r\n             wallet.add(account);\r\n             $('#extrapanel').modal('hide');\r\n             $('#account_password').val('');\r\n             callback();\r\n             account = null;\r\n             wallet = null;\r\n           } else {\r\n             // do nothing ...\r\n           }\r\n    });\r\n  } else {\r\n    callback();\r\n  }\r\n}\r\n\r\nfunction wrapControllerTransaction(form_selector, method, args, options, callback){\r\n\r\n    if (window.tributeControllerContract){\r\n      wrapContractTransaction(window.tributeControllerContract, form_selector, method, args, options, callback);\r\n    } else {\r\n\r\n      var userAccount = $('#content-main').data('account');\r\n      var tokenAddress = $('#app').data('address');\r\n\r\n      $.getJSON(\"/static/contracts/TributeController.json?\"+Math.random(), function(json) {\r\n\r\n          var code = json.bytecode;\r\n          var abi = json.abi;\r\n\r\n          var tributeControllerContract = new window.web3.eth.Contract(abi, tokenAddress);\r\n          tributeControllerContract.options.from = userAccount;\r\n          //myContract.options.from = web3.eth.accounts[0]; // default from address\r\n          //myContract.options.gasPrice = '20000000000000'; // default gas price in wei\r\n          //myContract.options.gas = 5000000; // provide as fallback always 5M gas\r\n          window.tributeControllerContract = tributeControllerContract;\r\n\r\n          wrapContractTransaction(tributeControllerContract, form_selector, method, args, options, callback);\r\n        });\r\n    }\r\n}\r\nwindow.wrapControllerTransaction = wrapControllerTransaction;\r\n\r\nfunction wrapTokenTransaction(form_selector, method, args, options, callback){\r\n\r\n  var userAccount = $('#content-main').data('account');\r\n  var tokenAddress = $('#content-main').data('address');\r\n\r\n  if(window.tributeTokenContract){\r\n    wrapContractTransaction(window.tributeTokenContract, form_selector, method, args, options, callback);\r\n  } else {\r\n    $.getJSON(\"/static/contracts/TributeToken.json?\"+Math.random(), function(json) {\r\n      var tributeTokenInterface = json;\r\n      var code = tributeTokenInterface.bytecode;\r\n      var abi = tributeTokenInterface.abi;\r\n\r\n      var tributeTokenContract = new window.web3.eth.Contract(abi, tokenAddress);\r\n      tributeTokenContract.options.from = userAccount;\r\n\r\n      window.tributeTokenContract = tributeTokenContract;\r\n      wrapContractTransaction(tributeTokenContract, form_selector, method, args, options, callback);\r\n    });\r\n  }\r\n}\r\nwindow.wrapTokenTransaction = wrapTokenTransaction;\r\n\r\nfunction wrapContractTransaction(contract, form_selector, method, args, options, callback){\r\n\r\n  $('#app form').off('submit');\r\n\r\n  var userAccount = $('#content-main').data('account');\r\n  var tokenAddress = $('#content-main').data('address');\r\n\r\n  var notyfReceipt = new Noty();\r\n  var receipt;\r\n\r\n  var notyfTransaction = new Noty(\r\n    {theme: 'relax',\r\n    type: 'warning',\r\n    timeout: 0,\r\n    layout: 'bottomRight',\r\n    text: 'Preparing transaction ...',\r\n    callbacks: {\r\n      onTemplate: function() {\r\n          this.barDom.innerHTML = '<div class=\"noty_body\">' + this.options.text + '<div>';\r\n          // Important: .noty_body class is required for setText API method.\r\n      },\r\n      onShow: function() {},\r\n    }\r\n  }).show();\r\n\r\n  // hide the form panel\r\n  //$(form_selector).closest('.modal-dialog').hide();\r\n  //$(form_selector).closest('.modal-dialog').css({'z-index':0});\r\n  //$(form_selector).closest('.modal-dialog').modal('hide');\r\n  function freeSpace(){\r\n\r\n    notyfTransaction.close();\r\n    $('#loader-overlay').modal('hide');\r\n\r\n  }\r\n\r\n  var sendTrans = function(){\r\n\r\n    contract.methods[method].apply(this, args)\r\n    .send(options)\r\n    .on('transactionHash', function(hash){\r\n        console.log(hash);\r\n        //notyf.close();\r\n        notyfReceipt = new Noty({theme: 'relax',\r\n          type: 'warning',\r\n          timeout: 0,\r\n          closeWith: [],\r\n          layout: 'bottomRight',\r\n          text: 'Transaction processing.<br /><a class=\"text-primary\" href=\"https://ropsten.etherscan.io/tx/'+hash+'\" target=\"_etherscan\" >'+hash+'</a><br/>Waiting for validation.',\r\n          callbacks: {\r\n            onTemplate: function() {\r\n                this.barDom.innerHTML = '<div class=\"noty_body\">' + this.options.text + '<div>';\r\n                // Important: .noty_body class is required for setText API method.\r\n            },\r\n            onShow: function() {},\r\n          }\r\n        }).show();\r\n\r\n\r\n\r\n    })\r\n    .on('confirmation', function(confirmationNumber, receipt){\r\n        console.log('confirmationNumber '+confirmationNumber);\r\n        if (confirmationNumber == 0){\r\n\r\n          console.log(receipt);\r\n\r\n          var notyfTransaction = new Noty({\r\n            theme: 'relax',\r\n            type: 'success',\r\n            timeout: 3500,\r\n            layout: 'bottomRight',\r\n            text: 'Transaction confirmed !',\r\n            callbacks: {\r\n              onTemplate: function() {\r\n                  this.barDom.innerHTML = '<div class=\"noty_body\">' + this.options.text + '<div>';\r\n                  // Important: .noty_body class is required for setText API method.\r\n              },\r\n              onShow: function() {},\r\n            }\r\n          }).show();\r\n\r\n          notyfReceipt.close();\r\n          //notyfReceipt.closeWith = ['click'];\r\n          //notyfReceipt.timeout = 5500;\r\n          //notyfReceipt.type = 'success';\r\n\r\n          if (callback){\r\n            \r\n            callback(receipt);\r\n\r\n            freeSpace();\r\n\r\n          } else {\r\n            var hash = receipt.transactionHash;\r\n            $('#id_tx').val(hash);\r\n            console.log(hash);\r\n\r\n            // send the final\r\n            $('#app form').off('submit');\r\n\r\n            $(form_selector).closest('.modal-dialog').hide();\r\n\r\n            $('#sidepanel').modal('hide');\r\n            $('#modalpanel').modal('hide');\r\n\r\n            //$(form_selector).submit(window.submitAForm);\r\n            //$(form_selector).submit();\r\n\r\n            console.log('Sending form ...');\r\n            var dataString = $(form_selector).serialize();\r\n\r\n            $.ajax({\r\n                type: \"POST\",\r\n                url: $(form_selector).attr('action'),\r\n                data: dataString,\r\n                success: function(msg) {\r\n                  console.log('Ok sent ...');\r\n                  freeSpace();\r\n                  //$('#loader-overlay').modal('hide');\r\n                  //notyfTransaction.close();\r\n                },\r\n                error: function(msg) {\r\n                  console.log('Error pushing form');\r\n                }\r\n            });\r\n          }\r\n        }\r\n    })\r\n    .on('receipt', function(receipt){\r\n      console.log('Receipt for transaction '+receipt.transactionHash );\r\n    })\r\n    .on('error', function(err){\r\n\r\n        console.log('ERROR');\r\n\r\n        console.error\r\n\r\n        notyfTransaction.close();\r\n        var notyfError = new Noty({theme: 'relax',\r\n          type: 'error',\r\n          timeout: 0,\r\n          layout: 'bottomRight',\r\n          text: err.message,\r\n          callbacks: {\r\n            onTemplate: function() {\r\n                this.barDom.innerHTML = '<div class=\"noty_body\">' + this.options.text + '<div>';\r\n                // Important: .noty_body class is required for setText API method.\r\n            },\r\n            onShow: function() {},\r\n          }\r\n        }).show();\r\n\r\n        // hide the form panel\r\n        $('#sidepanel').modal('hide');\r\n        $('#loader-overlay').modal('hide');\r\n\r\n    });\r\n\r\n  };\r\n\r\n\r\n  //\r\n  function checkAndSend(){\r\n\r\n    //\r\n    var zIndex = 1040 + (10 * $('.modal:visible').length);\r\n    $('#loader-overlay').css('z-index', zIndex);\r\n    $('#loader-overlay').modal('show');\r\n\r\n    // user balance has to have enought ether for the gas\r\n    web3.eth.getBalance(userAccount).then(function(balance){\r\n\r\n      var currentBalance = balance;\r\n      // Number.parseFloat(web3.utils.fromWei(balance)).toPrecision(4);\r\n\r\n      console.log('Balance:', currentBalance, balance);\r\n\r\n      contract.methods[method].apply(this, args).estimateGas({options})\r\n      .then(function(gasAmount){\r\n\r\n          options.gas = Math.round(gasAmount*5);\r\n\r\n          console.log(options);\r\n\r\n          if (currentBalance > options.gas){\r\n            sendTrans();\r\n          } else {\r\n\r\n            ///\r\n            var notyfTransaction = new Noty(\r\n              {theme: 'relax',\r\n              type: 'error',\r\n              timeout: 0,\r\n              layout: 'bottomRight',\r\n              text: 'You don\\' have enought ETH to for the gas.',\r\n              callbacks: {\r\n                onTemplate: function() {\r\n                    this.barDom.innerHTML = '<div class=\"noty_body\">' + this.options.text + '<div>';\r\n                    // Important: .noty_body class is required for setText API method.\r\n                },\r\n                onShow: function() {},\r\n              }\r\n            }).show();\r\n\r\n            ///\r\n            $('#sidepanel').modal('hide');\r\n            $('#loader-overlay').modal('hide');\r\n\r\n\r\n          }\r\n          //sendTrans();\r\n      })\r\n      .catch(function(error){\r\n        console.log('Cannot estimate gas');\r\n        console.error();\r\n      });\r\n\r\n    });\r\n\r\n  }\r\n\r\n\r\n  if ( $('#content-main').data('keystore') ){\r\n    unlockAccount(function(account){\r\n      checkAndSend();\r\n    });\r\n  } else {\r\n    checkAndSend();\r\n  }\r\n\r\n}\r\n\n\n//# sourceURL=webpack:///./src/components/project.js?");

/***/ }),

/***/ "./src/components/web3.js":
/*!********************************!*\
  !*** ./src/components/web3.js ***!
  \********************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("\r\nvar network_by_id = {\r\n  1: 'Mainnet',\r\n  3: 'Ropsten',\r\n  4: 'Rinkeby',\r\n  42: 'Kovan',\r\n  5777: 'Kovan',\r\n}\r\n\r\nfunction setupWeb3(){\r\n    ///\r\n    if (window.web3) {\r\n      //https://guillaumeduveau.com/fr/blockchain/ethereum/metamask-web3\r\n      // Then replace the old injected version by the latest build of Web3.js version 1.0.0\r\n      window.web3old = window.web3;\r\n      window.web3 = new Web3(window.web3.currentProvider);\r\n    } else {\r\n      // var infura_url = 'http://localhost:7545';\r\n      var infura_url = 'https://ropsten.infura.io/v3/85b874cf0fe74f98a1006219a5e03985';\r\n      window.web3 = new Web3(new Web3.providers.HttpProvider(infura_url));\r\n    }\r\n    \r\n    //checkingNetwork();\r\n}\r\n\r\nfunction checkingNetwork(){\r\n    // first of all\r\n    // check that we are on the right network\r\n    //\r\n    var networkId;\r\n    var tributeControllerNetwork = $('#app').data('network');\r\n\r\n    window.web3.eth.net.getId().then(function(nid){\r\n\r\n      networkId = nid;\r\n\r\n      $('#eth_network').text(network_by_id[networkId]);\r\n\r\n      var defaultAccount =  $('#content-main').data('account');\r\n\r\n      if ( defaultAccount && networkId && tributeControllerNetwork == networkId ){\r\n        var currentBalance = 0;\r\n        web3.eth.getBalance(defaultAccount).then(function(balance){\r\n          currentBalance = Number.parseFloat(web3.utils.fromWei(balance)).toPrecision(4);\r\n          console.log('Balance:', currentBalance, balance);\r\n          $('#eth_balance').text(currentBalance);\r\n        });\r\n      } else {\r\n        /// open warning message box about the initial setup for web3\r\n        // how do we setup web3 provider ?\r\n        // alert('You have to select network '+network_by_id[tributeControllerNetwork] );\r\n      }\r\n    });\r\n\r\n}\r\n\r\nfunction checkAccount(){\r\n\r\n  var defaultAccount =  $('#content-main').data('account');\r\n\r\n  if (defaultAccount){\r\n    var currentBalance = 0;\r\n    web3.eth.getBalance(defaultAccount).then(function(balance){\r\n      currentBalance = Number.parseFloat(web3.utils.fromWei(balance)).toPrecision(4);\r\n      console.log('Balance:', currentBalance, balance);\r\n    });\r\n  } else {\r\n    window.popReload('/web3.html', '#modalpanel');\r\n  }\r\n\r\n}\r\n\r\nmodule.exports = setupWeb3;\r\n\n\n//# sourceURL=webpack:///./src/components/web3.js?");

/***/ }),

/***/ "./src/index.js":
/*!**********************!*\
  !*** ./src/index.js ***!
  \**********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("__webpack_require__(/*! ./components/app.js */ \"./src/components/app.js\");\r\n__webpack_require__(/*! ./components/web3.js */ \"./src/components/web3.js\");\r\n__webpack_require__(/*! ./components/project.js */ \"./src/components/project.js\");\r\n\r\n__webpack_require__(/*! ./components/profile.js */ \"./src/components/profile.js\");\r\n\n\n//# sourceURL=webpack:///./src/index.js?");

/***/ })

/******/ });